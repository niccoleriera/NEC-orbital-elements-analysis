from jobs import q, update_job_status, get_comet_dict, save_job_image  
import matplotlib.pyplot as plt
import numpy as np

def oe2rv(oe,mu,M):
    d2r=np.pi/180
    sma=oe[0]
    emag=oe[1]
    i=oe[2]*d2r
    sw=oe[3]*d2r
    bw=oe[4]*d2r
    nu= oe[5]*d2r
    rmag = sma*(1-emag**2)/(1+emag*np.cos(nu))
    r=np.array([rmag*np.cos(nu), rmag*np.sin(nu),0])
    p=sma*(1-emag**2)
    v= np.array([-np.sin(nu)*np.sqrt(mu/p), (emag +np.cos(nu))*np.sqrt(mu/p), 0])
    r1 = np.array([[np.cos(bw), -np.sin(bw), 0],[np.sin(bw), np.cos(bw), 0],[0,0,1]])
    r2 = np.array([[1,0,0],[0, np.cos(i), -np.sin(i)], [0, np.sin(i), np.cos(i)]])
    r3 = np.array([[np.cos(sw), -np.sin(sw), 0],[np.sin(sw), np.cos(sw),0],[0,0,1]])
    rotm = np.matmul(r1,r2)
    rotm = np.matmul(rotm,r3)
    rijk = rotm.dot(r)
    vijk = rotm.dot(v)
    E= np.arccos(abs(r[0]/sma))
  #print(r[0]/sma)
    M2 = E*-emag*np.sin(E)
    M2=-M2
    rcurr=np.zeros((3,1))
    err=abs(M2-M)
    rcurr[0]=rijk[0]
    rcurr[1]=rijk[1]
    rcurr[2]=rijk[2]


    return [rijk[0],rijk[1],rijk[2],vijk[0],vijk[1],vijk[2],rcurr,err]

@q.worker
def execute_job(jid):
    update_job_status(jid, "in progress")
        
    # index = int(float(request.args.get('index')))
    au2km = 1.496*10**8
    d2r=180/np.pi
    comet_data = get_comet_dict(jid)
    sma=(float(comet_data['q_au_1'])+float(comet_data['q_au_2']))/2*au2km
    emag = float(comet_data['e'])
    i = float(comet_data['i_deg'])*d2r
    sw = float(comet_data['w_deg'])*d2r
    bw = float(comet_data['node_deg'])*d2r
    nu=0
    oe=[sma,emag,i,sw,bw,nu]

    
    mu=1.327*10**11
    y2m = 525600
    T=float(comet_data['p_yr'])*y2m
    n=2*np.pi/T
    tcurr = T-float(comet_data['tp_tdb'])+float(comet_data['epoch_tdb'])
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
   # ax.scatter(curr[0],curr[1],curr[2],color='red',s=150)
    ax.scatter(0,0,0,color='orange',s=200)
    plt.savefig('/output_image.png')
    
    with open('/output_image.png', 'rb') as f:
        img = f.read()
    save_job_image(jid, img)
     
    update_job_status(jid, "complete") 

execute_job()
