def Cut(values:np.ndarray,weights,level):
    x=np.asarray(values,dtype=float)
    w=np.asarray(weights,dtype=float)
    order=np.argsort(x)
    sx,sw=x[order],w[order]
    cumulative=np.cumsum(sw)/np.sum(sw)
    return float(sx[min(int(np.searchsorted(cumulative,level)),len(sx)-1)])
def Grid(step)->np.ndarray:
    count=int(round((SOC_MAX_KWH-SOC_MIN_KWH)/step))
    states=SOC_MIN_KWH+np.arange(count+1)*step
    return states
def Step(step,power_max_kw:float=POWER_MAX_KW):
    max_energy=power_max_kw*DELTA_T
    max_up=int(math.floor(ETA_C*max_energy/step+1e-10))
    max_down=int(math.floor(max_energy/(ETA_D*step)+1e-10))
    offsets=np.arange(-max_down,max_up+1,dtype=int)
    charge=np.where(offsets>0,offsets*step/ETA_C,0.0)
    discharge=np.where(offsets<0,-offsets*step*ETA_D,0.0)
    return offsets,charge,discharge
def Solve(net_scenarios,weights:np.ndarray,price:np.ndarray,soc_initial,step=GRID_STEP_KWH,mode="plan",base_grid:np.ndarray|None=None,terminal_salvage=0.0,terminal_anchor:float=SOC_INITIAL_KWH,terminal_anchor_weight=TERMINAL_ANCHOR_WEIGHT,force_terminal=False,emergency_multiplier=EMERGENCY_MULTIPLIER,up_multiplier:float=UP_MULTIPLIER,down_penalty:float=DOWN_PENALTY,):
    net=np.asarray(net_scenarios,dtype=float)
    weights=np.asarray(weights,dtype=float)
    price=np.asarray(price,dtype=float)
    weights=weights/weights.sum()
    h=len(price)
    states=Grid(step)
    initial_index=int(np.argmin(np.abs(states-soc_initial)))
    offsets,charge_by_offset,discharge_by_offset=Step(step)
    battery_by_offset=charge_by_offset-discharge_by_offset
    n_states=len(states)
    if force_terminal:
        terminal=np.full(n_states,1e14)
        terminal[int(np.argmin(np.abs(states-terminal_anchor)))]=0.0
    else:
        terminal=(-terminal_salvage*(states-SOC_MIN_KWH)+terminal_anchor_weight*max(float(np.mean(price)),1e-6)*np.abs(states-terminal_anchor))
    next_value=terminal.copy()
    policy=np.full((h,n_states),-1,dtype=np.int16)
    grid_policy=np.zeros((h,n_states),dtype=float)
    value_at_time=np.zeros((h,n_states),dtype=float)
    plan_level=float(np.clip(1.0-1.0/emergency_multiplier,0.0,1.0))
    adjust_level=float(np.clip(1.0-up_multiplier/emergency_multiplier,0.0,1.0))
    for t in range(h-1,-1,-1):
        q_plan_base=Cut(net[:,t],weights,plan_level)
        q_adjust_base=Cut(net[:,t],weights,adjust_level)
        stage_cost=np.zeros(len(offsets))
        q_choice=np.zeros(len(offsets))
        for k,battery in enumerate(battery_by_offset):
            requirement=net[:,t]+battery
            if mode=="plan":
                q=max(0.0,q_plan_base+battery)
                adjustment=0.0
                normal=price[t]*q
            else:
                base=max(0.0,float(base_grid[t]))
                q=max(base,q_adjust_base+battery,0.0)
                adjustment=price[t]*(up_multiplier*max(q-base,0.0)+down_penalty*max(base-q,0.0))
                normal=0.0
            e=float(np.dot(weights,np.maximum(requirement-q,0.0)))
            stage_cost[k]=normal+adjustment+emergency_multiplier*price[t]*e
            q_choice[k]=q
        current_value=np.full(n_states,np.inf)
        for k,offset in enumerate(offsets):
            if offset>=0:
                current_indices=np.arange(0,n_states-offset,dtype=int)
            else:
                current_indices=np.arange(-offset,n_states,dtype=int)
            next_indices=current_indices+offset
            candidates=stage_cost[k]+next_value[next_indices]
            better=candidates<current_value[current_indices]
            if not np.any(better):
                continue
            chosen_current=current_indices[better]
            chosen_next=next_indices[better]
            current_value[chosen_current]=candidates[better]
            policy[t,chosen_current]=chosen_next
            grid_policy[t,chosen_current]=q_choice[k]
        value_at_time[t]=current_value
        next_value=current_value
    grid=np.zeros(h)
    charge=np.zeros(h)
    discharge=np.zeros(h)
    soc=np.zeros(h+1)
    soc[0]=states[initial_index]
    i=initial_index
    max_residual=0.0
    for t in range(h):
        j=int(policy[t,i])
        delta=states[j]-states[i]
        if delta>=0:
            charge[t]=delta/ETA_C
        else:
            discharge[t]=-delta*ETA_D
        grid[t]=grid_policy[t,i]
        soc[t+1]=states[j]
        max_residual=max(max_residual,abs(soc[t+1]-soc[t]-ETA_C*charge[t]+discharge[t]/ETA_D))
        i=j
    return Plan(grid=grid,charge=charge,discharge=discharge,soc=soc,bellman_value=float(value_at_time[0,initial_index]),bellman_residual=float(max_residual),)
def Salvage(price_forecast,day_index,scale:float=TERMINAL_SCALE)->float:
    next_index=min(day_index+1,N_DAYS-1)
    return float(scale*ETA_D*np.quantile(price_forecast[next_index],0.75))
def Weigh(q3data,forecasts,scenario,day_index,issue_index:int,):
    weights=np.asarray(scenario.weights,dtype=float).copy()
    start=ISSUE_STARTS[issue_index]
    if issue_index==0 or start==0 or np.all(np.asarray(scenario.source_days)<0):
        return weights/weights.sum(),1.0,"冷启动"
    actual_net=(q3data.load_power[day_index,:start]-q3data.pv_power[day_index,:start])*DELTA_T
    point_net=(forecasts.load_stage[day_index,0,:start]-forecasts.pv_corrected[day_index,0,:start])*DELTA_T
    current_error=actual_net-point_net
    window=min(36,start)
    slope=0.0
    if window>1:
        slope=np.mean(np.diff(current_error[-window:]))
    current_feature=np.asarray([np.mean(current_error[-window:]),np.std(current_error[-window:]),slope,])
    source_features=[]
    valid_source:list[bool]=[]
    for source_day in np.asarray(scenario.source_days,dtype=int):
        if source_day<0:
            source_features.append(np.zeros(3))
            valid_source.append(False)
            continue
        residual=forecasts.net_residual[source_day,0,:start]
        slope=0.0
        if window>1:
            slope=np.nanmean(np.diff(residual[-window:]))
        feature=np.asarray([np.nanmean(residual[-window:]),np.nanstd(residual[-window:]),slope,])
        source_features.append(feature)
        valid_source.append(bool(np.all(np.isfinite(feature))))
    features=np.vstack(source_features)
    valid=np.asarray(valid_source)
    if not np.any(valid):
        return weights/weights.sum(),1.0,"历史不足"
    history=forecasts.net_residual[max(0,day_index-90):day_index,0,:start]
    spread=1.0
    if len(history):
        spread=np.nanstd(np.nanmean(np.diff(history[:,-window:],axis=1),axis=1))
    scale=np.asarray([np.nanstd(np.nanmean(history[:,-window:],axis=1)),np.nanstd(np.nanstd(history[:,-window:],axis=1)),spread,])
    scale[~np.isfinite(scale)|(scale<1e-6)]=1.0
    distance=np.sqrt(np.sum(((features-current_feature)/scale)**2,axis=1))
    kernel=np.exp(-0.5*np.minimum(distance,8.0)**2)
    kernel[~valid]=0.0
    conditional=weights*(SCENARIO_BLEND+(1.0-SCENARIO_BLEND)*kernel)
    conditional=conditional/conditional.sum()
    effective=float(1.0/np.sum(conditional**2))
    mean_error=current_feature[0]
    regime="平稳"
    if mean_error>scale[0]*0.35:
        regime="偏高"
    elif mean_error<-scale[0]*0.35:
        regime="偏低"
    return conditional,effective,regime
