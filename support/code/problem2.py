def Build2(
    Data,
    Forecasts,
    Day:int,
    scenario2=Scenario,
)->Scenarioset:
    Load2,Pv2,Point=horizon1(Forecasts,Day)
    Load6,Pv6,Indices,Raw=Residual(
        Data,Forecasts,Day
    )
    if Indices[0] < 0:
        return Scenarioset(
            Net1=Point[None,:],
            Weights=np.ones(1),
            Source2=Indices,
            Point=Point,
            Reduction=0.0,
            Max=-1,
        )
    X=Trajectory(Load6,Pv6)
    Unique=len(np.unique(np.round(X,8),axis=0))
    K=max(1,min(scenario2,len(Indices),Unique))
    Model1=KMeans(
        n_clusters=K,
        random_state=Random+Day,
        n_init=5,
        max_iter=80,
    )
    Model1.fit(X,sample_weight=Raw)
    Labels=Model1.labels_
    Medoids:list[int]=[]
    Probabilities=[]
    Assigned=np.zeros(len(Indices))
    for Cluster in range(K):
        Members=np.flatnonzero(Labels == Cluster)
        if len(Members) == 0:
            continue
        Distances=np.sum((X[Members]-Model1.cluster_centers_[Cluster]) ** 2,axis=1)
        Medoid=int(Members[int(np.argmin(Distances))])
        Medoids.append(Medoid)
        Probabilities.append(float(np.sum(Raw[Members])))
        Assigned[Members]=np.sqrt(np.maximum(Distances,0.0))
    Probabilities1=np.asarray(Probabilities,dtype=float)
    Probabilities1 /= np.sum(Probabilities1)
    Medoids1=np.asarray(Medoids,dtype=int)
    Load7=np.maximum(Load2[None,:]+Load6[Medoids1],0.0)
    Pv7=np.maximum(Pv2[None,:]+Pv6[Medoids1],0.0)
    Net2=Load7-Pv7
    return Scenarioset(
        Net1=Net2,
        Weights=Probabilities1,
        Source2=Indices[Medoids1],
        Point=Point,
        Reduction=float(np.sum(Raw*Assigned)),
        Max=int(np.max(Indices)+1),
    )
Lp={}
def Stochastic(
    scenario2:int,
    Horizon2,
    Eta2,
    Eta3,
):
    Key=(scenario2,Horizon2,round(Eta2,8),round(Eta3,8))
    if Key in Lp:
        return Lp[Key]
    K,H=scenario2,Horizon2
    Ig=0
    Ic=Ig+H
    Ir=Ic+K*H
    Ie=Ir+K*H
    Iq=Ie+K*H
    Isoc=Iq+K*H
    Izeta=Isoc+K*(H+1)
    Ixi=Izeta+1
    N=Ixi+K
    Aeq=lil_matrix((2*K*H,N),dtype=float)
    for W in range(K):
        for T in range(H):
            Flow=W*H+T
            Row2=W*H+T
            Row3=K*H+W*H+T
            Aeq[Row2,Ig+T]=1.0
            Aeq[Row2,Ir+Flow]=1.0
            Aeq[Row2,Ie+Flow]=1.0
            Aeq[Row2,Ic+Flow]=-1.0
            Aeq[Row2,Iq+Flow]=-1.0
            soc0=Isoc+W*(H+1)+T
            Aeq[Row3,soc0+1]=1.0
            Aeq[Row3,soc0]=-1.0
            Aeq[Row3,Ic+Flow]=-Eta2
            Aeq[Row3,Ir+Flow]=1.0/Eta3
    indices1={
        "g":Ig,
        "c":Ic,
        "r":Ir,
        "e":Ie,
        "q":Iq,
        "soc":Isoc,
        "zeta":Izeta,
        "xi":Ixi,
        "n":N,
        "k":K,
        "h":H,
    }
    Lp[Key]=(Aeq.tocsr(),indices1)
    return Lp[Key]

def Solve(
    Scenarios:Scenarioset,
    Price,
    soc4,
    Risk2,
    Alpha=Cvar,
    Eta2=Eta,
    Eta3=Eta1,
    Terminal=soc2,
)->Stochasticsolution:
    Net1=np.asarray(Scenarios.Net1,dtype=float)
    Weights=np.asarray(Scenarios.Weights,dtype=float)
    K,H=Net1.shape
    Aeq,Idx=Stochastic(K,H,Eta2,Eta3)
    Beq=np.concatenate([Net1.reshape(-1),np.zeros(K*H)])
    Pmax=Power*Delta
    Bounds=[]
    Bounds.extend([(0.0,None)]*H)
    Bounds.extend([(0.0,Pmax)]*(K*H))
    Bounds.extend([(0.0,Pmax)]*(K*H))
    Bounds.extend([(0.0,None)]*(K*H))
    Bounds.extend([(0.0,None)]*(K*H))
    for Item in range(K):
        for T in range(H+1):
            if T == 0:
                Bounds.append((soc4,soc4))
            elif T == H:
                Bounds.append((Terminal,Terminal))
            else:
                Bounds.append((Soc,Soc1))
    Bounds.append((0.0,None))
    Bounds.extend([(0.0,None)]*K)
    Objective=np.zeros(Idx["n"],dtype=float)
    Objective[Idx["g"] :Idx["g"]+H]=Price
    Emergency8=Emergency*Price
    for W in range(K):
        Start=Idx["e"]+W*H
        Objective[Start :Start+H]=(1.0-Risk2)*Weights[W]*Emergency8
    Objective[Idx["zeta"]]=Risk2
    Objective[Idx["xi"] :Idx["xi"]+K]=Risk2*Weights/(1.0-Alpha)
    Objective[Idx["c"] :Idx["c"]+K*H] += 1e-7
    Objective[Idx["r"] :Idx["r"]+K*H] += 1e-7
    Objective[Idx["q"] :Idx["q"]+K*H] += 1e-8
    Aub=lil_matrix((K,Idx["n"]),dtype=float)
    for W in range(K):
        Start=Idx["e"]+W*H
        Aub[W,Start :Start+H]=Emergency8
        Aub[W,Idx["zeta"]]=-1.0
        Aub[W,Idx["xi"]+W]=-1.0
    result1=linprog(
        Objective,
        A_ub=Aub.tocsr(),
        b_ub=np.zeros(K),
        A_eq=Aeq,
        b_eq=Beq,
        bounds=Bounds,
        method="highs",
        options={"presolve":True},
    )
    if not result1.success:
        raise RuntimeError(f"两阶段随机规划失败：{result1.message}")
    X=result1.x
    C=X[Idx["c"] :Idx["c"]+K*H].reshape(K,H)
    R=X[Idx["r"] :Idx["r"]+K*H].reshape(K,H)
    E=X[Idx["e"] :Idx["e"]+K*H].reshape(K,H)
    Q=X[Idx["q"] :Idx["q"]+K*H].reshape(K,H)
    Soc3=X[Idx["soc"] :Idx["soc"]+K*(H+1)].reshape(K,H+1)
    scenario3=np.dot(E,Emergency8)
    Zeta=X[Idx["zeta"]]
    cvar2=Zeta+np.sum(Weights*np.maximum(scenario3-Zeta,0.0))/(1.0-Alpha)
    Balance=X[Idx["g"] :Idx["g"]+H][None,:]+R+E-C-Q-Net1
    soc7=Soc3[:,1:]-Soc3[:,:-1]-Eta2*C+R/Eta3
    return Stochasticsolution(
        Grid=X[Idx["g"] :Idx["g"]+H].copy(),
        Charge1=C,
        Discharge=R,
        Emergency2=E,
        Spill=Q,
        Soc3=Soc3,
        Objective=float(result1.fun),
        Expected=float(np.dot(Weights,scenario3)),
        Cvar1=float(cvar2),
        Max1=float(np.max(np.abs(Balance))),
        Max2=float(np.max(np.abs(soc7))),
    )
