def end1(price_after_horizon:np.ndarray,scale=TERMINAL_SCALE):
    price=np.maximum(np.asarray(price_after_horizon,dtype=float),1e-8)
    quantiles=np.quantile(price,[0.90,0.80,0.70,0.55,0.40,0.25])*ETA_D*scale
    marginal=np.maximum.accumulate(quantiles[::-1])[::-1]
    values=np.zeros(len(TERMINAL_KNOTS))
    for i in range(len(TERMINAL_KNOTS)-2,-1,-1):
        values[i]=values[i+1]+marginal[i]*(TERMINAL_KNOTS[i+1]-TERMINAL_KNOTS[i])
    slopes=np.diff(values)/np.diff(TERMINAL_KNOTS)
    slopes=np.maximum.accumulate(slopes)
    intercepts=values[:-1]-slopes*TERMINAL_KNOTS[:-1]
    return End(knots=TERMINAL_KNOTS.copy(),values=values,slopes=slopes,intercepts=intercepts,)
@dataclass
class Model:
    objective_expected:np.ndarray
    aeq:csr_matrix
    beq:np.ndarray
    aub_base:csr_matrix
    bub_base:np.ndarray
    bounds:list[tuple[float|None,float|None]]
    indices:dict[str,Any]
    scenario_cost_vectors:list[np.ndarray]
def Model1(net_scenarios,weights:np.ndarray,price,soc_initial:float,terminal,base_plan,fixed_grid=None,emergency_multiplier=EMERGENCY_MULTIPLIER,):
    net=np.asarray(net_scenarios,dtype=float)
    weights=np.asarray(weights,dtype=float)
    weights=weights/weights.sum()
    price=np.asarray(price,dtype=float)
    k,h=net.shape
    if base_plan is None:
        Hold22=0
    else:
        Hold22=len(base_plan)
    current_count=(Hold22)
    grid=0
    up=h
    down=up+current_count
    scenario_base=down+current_count
    scenario_width=5*h+2
    scenario_indices:list[dict[str,int]]=[]
    for s in range(k):
        base=scenario_base+s*scenario_width
        scenario_indices.append({"charge":base,"discharge":base+h,"emergency":base+2*h,"spill":base+3*h,"soc":base+4*h,"theta":base+5*h+1,})
    regret=scenario_base+k*scenario_width
    nvar=regret+1
    aeq=lil_matrix((2*k*h+current_count,nvar),dtype=float)
    beq=np.zeros(2*k*h+current_count)
    row=0
    for s,idx in enumerate(scenario_indices):
        for t in range(h):
            aeq[row,grid+t]=1.0
            aeq[row,idx["discharge"]+t]=1.0
            aeq[row,idx["emergency"]+t]=1.0
            aeq[row,idx["charge"]+t]=-1.0
            aeq[row,idx["spill"]+t]=-1.0
            beq[row]=net[s,t]
            row+=1
        for t in range(h):
            aeq[row,idx["soc"]+t+1]=1.0
            aeq[row,idx["soc"]+t]=-1.0
            aeq[row,idx["charge"]+t]=-ETA_C
            aeq[row,idx["discharge"]+t]=1.0/ETA_D
            row+=1
    if base_plan is not None:
        base_array=np.asarray(base_plan,dtype=float)
        for t in range(current_count):
            aeq[row,grid+t]=1.0
            aeq[row,up+t]=-1.0
            aeq[row,down+t]=1.0
            beq[row]=base_array[t]
            row+=1
    bounds:list[tuple[float|None,float|None]]=[]
    if fixed_grid is None:
        bounds.extend([(0.0,None)]*h)
    else:
        fixed=np.asarray(fixed_grid,dtype=float)
        Pack15=[]
        for v in fixed:
            Pack15.append((float(v), float(v)))
        bounds.extend((Pack15))
    if base_plan is not None:
        bounds.extend([(0.0,None)]*current_count)
        Pack9=[]
        for v in base_plan:
            Pack9.append((0.0, float(max(0.0, v))))
        bounds.extend((Pack9))
    for idx in scenario_indices:
        bounds.extend([(0.0,PERIOD_MAX_KWH)]*h)
        bounds.extend([(0.0,PERIOD_MAX_KWH)]*h)
        bounds.extend([(0.0,None)]*h)
        bounds.extend([(0.0,None)]*h)
        bounds.extend([(SOC_MIN,SOC_MAX)]*(h+1))
        bounds.append((None,None))
    bounds.append((0.0,None))
    for idx in scenario_indices:
        bounds[idx["soc"]]=(float(soc_initial),float(soc_initial))
    expected=np.zeros(nvar)
    common=np.zeros(nvar)
    if base_plan is None:
        common[grid:grid+h]=price
    else:
        common[up:up+current_count]=UP_MULTIPLIER*price[:current_count]
        common[down:down+current_count]=DOWN_PENALTY*price[:current_count]
        if current_count<h:
            common[grid+current_count:grid+h]=price[current_count:]
    expected+=common
    scenario_cost_vectors:list[np.ndarray]=[]
    for s,idx in enumerate(scenario_indices):
        vector=common.copy()
        vector[idx["emergency"]:idx["emergency"]+h]=emergency_multiplier*price
        vector[idx["theta"]]=1.0
        scenario_cost_vectors.append(vector)
        expected+=weights[s]*(vector-common)
    nub=k*len(terminal.slopes)
    aub=lil_matrix((nub,nvar),dtype=float)
    bub=np.zeros(nub)
    row=0
    for idx in scenario_indices:
        end_soc=idx["soc"]+h
        for slope,intercept in zip(terminal.slopes,terminal.intercepts):
            aub[row,end_soc]=float(slope)
            aub[row,idx["theta"]]=-1.0
            bub[row]=-float(intercept)
            row+=1
    indices={"grid":grid,"up":up,"down":down,"scenario":scenario_indices,"regret":regret,"nvar":nvar,"h":h,"k":k,"current_count":current_count,"weights":weights,}
    return Model(objective_expected=expected,aeq=aeq.tocsr(),beq=beq,aub_base=aub.tocsr(),bub_base=bub,bounds=bounds,indices=indices,scenario_cost_vectors=scenario_cost_vectors,)
