import json
from flask import Flask, request
import redis
import numpy as np
import matplotlib.pyplot as plt

app = Flask(__name__)
#rd = redis.Redis(host='127.0.0.1', port = '6422', db=0) #change this later
comet_data = []
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


@app.route('/data', methods=['POST'])
def load_data():
    """
    This function reads in Near Earth Comets' Orbital Elements data and stores it in the Redis database.
    Returns:
    A string that lets the user know that the data has been read from the file.
    """
 #   rd.set('data', json.dumps(data))
    global comet_data
    with open('b67r-rgxc.json', 'r') as f:
        comet_data = json.load(f)
    return f'Data has been read from file\n'

@app.route('/data', methods= ['GET'])
def read_data():
    """
    This function takes the Near Earth Comets' Orbital Elements data that has been loaded as a key and returns it as a JSON list.
    Returns:
    The JSON list of the Near Earth Comets' Orbital Elements data.
    """
    comet_data_dict = {}
    comet_data_dict['comets'] = []
    for i in range(len(comet_data)):
        comet_data_dict['comets'].append(comet_data[i])
    return(comet_data_dict)

@app.route('/comets/<comet>', methods= ["GET"])
def get_comets(comet):
    return(comet_data[4])

def start_data()->str: 
    """
    Plots trajectory
    Args:
        index:
    Returns:
        result(string): 
    """
    
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
     
    return "Trajectory plotted \n"


@app.route('/rv/',methods=['GET'])

def rv_data()->str:
    """
    Prints position data
    Args:
        index
    Returns:
        result(string): 
    """

    index = int(float(request.args.get('index')))
    d2r=180/np.pi
    sma=(comet_data[index]['q_au_1']+comet_data[index]['q_au_2'])/2
    emag = comet_data[index]['e']
    i = comet_data[index]['i_deg']*d2r
    sw = comet_data[index]['w_deg']*d2r
    bw = comet_data[index]['node_deg']*d2r
    nu=0
    oe=[sma,emag,i,sw,bw,nu]

    au2km = 1.496*10**8
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
    return 'Position:\n' +'\n'.join(curr) +'\n'  

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
