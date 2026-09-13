def Build(Price,Loade,Pve,Etac,Etad,Pmax,Soclow1,Sochigh1,Soc01,)->dict[str,Any]:
    N=len(Price)
    pmax1=Pmax*Step
    Ig,Ic,Ir,Iq=0,N,2*N,3*N
    Isoc,Iu=4*N,5*N+1
    Nv=6*N+1
    Objective=np.zeros(Nv)
    Objective[Ig:Ig+N]=Price
    Lb=np.zeros(Nv)
    Ub=np.full(Nv,np.inf)
    Ub[Ic:Ic+N]=pmax1
    Ub[Ir:Ir+N]=pmax1
    Lb[Isoc:Isoc+N+1]=Soclow1
    Ub[Isoc:Isoc+N+1]=Sochigh1
    Lb[Isoc]=Ub[Isoc]=Soc01
    Lb[Isoc+N]=Ub[Isoc+N]=Soc01
    Ub[Iu:Iu+N]=1.0
    Int=np.zeros(Nv,dtype=int)
    Int[Iu:Iu+N]=1
    Aeq=lil_matrix((2*N,Nv))
    Beq=np.zeros(2*N)
    for T in range(N):
        Aeq[T,Ig+T]=1.0
        Aeq[T,Ic+T]=-1.0
        Aeq[T,Ir+T]=1.0
        Aeq[T,Iq+T]=-1.0
        Beq[T]=Loade[T]-Pve[T]
        Aeq[N+T,Isoc+T+1]=1.0
        Aeq[N+T,Isoc+T]=-1.0
        Aeq[N+T,Ic+T]=-Etac
        Aeq[N+T,Ir+T]=1.0/Etad
    Aub=lil_matrix((2*N,Nv))
    Bub=np.zeros(2*N)
    for T in range(N):
        Aub[T,Ic+T]=1.0
        Aub[T,Iu+T]=-pmax1
        Aub[N+T,Ir+T]=1.0
        Aub[N+T,Iu+T]=pmax1
        Bub[N+T]=pmax1
    Constraint=[LinearConstraint(Aeq.tocsr(),Beq,Beq),LinearConstraint(Aub.tocsr(),-np.inf,Bub),]
    return {"n":N,"objective":Objective,"bounds":Bounds(Lb,Ub),"integrality":Int,"constraints":Constraint,"indices":{"g":Ig,"c":Ic,"r":Ir,"q":Iq,"soc":Isoc,"u":Iu},"pmax":pmax1,}
def Get(Raw,Problem,Cost1):
    N=Problem["n"]
    Idx=Problem["indices"]
    X=Raw.x
    return Result(Cost1=float(Cost1),Cost2=float(np.dot(Problem["objective"],X)),Grid=X[Idx["g"]:Idx["g"]+N].copy(),Chong=X[Idx["c"]:Idx["c"]+N].copy(),Fang=X[Idx["r"]:Idx["r"]+N].copy(),Cut=X[Idx["q"]:Idx["q"]+N].copy(),Soc=X[Idx["soc"]:Idx["soc"]+N+1].copy(),Mode=X[Idx["u"]:Idx["u"]+N].copy(),Msg=str(Raw.message),)

def Run(Price,Loade,Pve,Etac=Effc,Etad=Effd,Pmax=Maxpower,Soclow1=Soclow,Sochigh1=Sochigh,Soc01=Soc0,Lex=True,Relax=False,):
    Problem=Build(Price,Loade,Pve,Etac,Etad,Pmax,Soclow1,Sochigh1,Soc01,)
    if Relax:
        Int=np.zeros_like(Problem["integrality"])
    else:
        Int=Problem["integrality"]
    Opts={"mip_rel_gap":1e-9,"time_limit":60.0,"disp":False}
    Primary=milp(Problem["objective"],integrality=Int,bounds=Problem["bounds"],constraints=Problem["constraints"],options=Opts,)
    Cost1=float(Primary.fun)
    if not Lex:
        return Get(Primary,Problem,Cost1)
    Nv=len(Problem["objective"])
    N=Problem["n"]
    Idx=Problem["indices"]
    Costtolerance=max(1e-6,abs(Cost1)*1e-10)
    Costcapacity=LinearConstraint(Problem["objective"].reshape(1,-1),-np.inf,Cost1+Costtolerance,)
    St2con=Problem["constraints"]+[Costcapacity]
    Curtailobjective=np.zeros(Nv)
    Curtailobjective[Idx["q"]:Idx["q"]+N]=1.0
    St2=milp(Curtailobjective,integrality=Int,bounds=Problem["bounds"],constraints=St2con,options=Opts,)
    Curtailtolerance=max(1e-7,abs(float(St2.fun))*1e-10)
    Curtailcapacity=LinearConstraint(Curtailobjective.reshape(1,-1),-np.inf,float(St2.fun)+Curtailtolerance,)
    Throughputobjective=np.zeros(Nv)
    Throughputobjective[Idx["c"]:Idx["c"]+N]=1.0
    Throughputobjective[Idx["r"]:Idx["r"]+N]=1.0
    st3=milp(Throughputobjective,integrality=Int,bounds=Problem["bounds"],constraints=St2con+[Curtailcapacity],options=Opts,)
    return Get(st3,Problem,Cost1)
