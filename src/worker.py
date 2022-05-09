from jobs import q, update_job_status, oe2rv 
import matplotlib.pyplot as plt
import numpy as np

@q.worker
def execute_job(jid):
    update_job_status(jid, "in progress")
    
    index = int(float(request.args.get('index')))
    au2km = 1.496*10**8
    d2r=180/np.pi
    sma=(comet_data[index]['q_au_1']+comet_data[index]['q_au_2'])/2*au2km
    emag = comet_data[index]['e']
    i = comet_data[index]['i_deg']*d2r
    sw = comet_data[index]['w_deg']*d2r
    bw = comet_data[index]['node_deg']*d2r
    nu=0
    oe=[sma,emag,i,sw,bw,nu]

    
    mu=1.327*10**11
    y2m = 525600
    T=comet_data[index]['p_yr']*y2m
    n=2*np.pi/T
    tcurr = T-comet_data[index]['tp_tdb']+comet_data[index]['epoch_tdb']
    M=n*(tcurr)

    k=1000
    cond=0;
    curr=[]
    tol=10**-2
    traj=[]
    rx,ry,rz,vx,vy,vz = ([] for h in range(6))
    for j in range(k):
        traj.append(oe2rv(oe,mu,M))
        rx.append(traj[j][0])
        ry.append(traj[j][1])
        rz.append(traj[j][2])
        vx.append(traj[j][3])
        vy.append(traj[j][4])
        vz.append(traj[j][5])
        if(traj[j][7]<tol and cond==0 and j>0):
            curr = traj[j-1][6]/au2km        
            cond=cond+1
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.scatter(rx,ry,rz,color='blue')
    ax.scatter(curr[0],curr[1],curr[2],color='red',s=150)
    ax.scatter(0,0,0,color='orange',s=200)
         
    update_job_status(jid, "complete") 

execute_job()
