import json
import numpy as np
from flask import Flask, request, send_file
from jobs import rd, q, add_job, generate_job_key 

app = Flask(__name__)

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
    arg1 = ((1-emag**2)**.5*np.sin(nu))/(1+emag*np.cos(nu))
    arg2 = (emag+np.cos(nu))/(1+emag*np.cos(nu))
    M2 = np.arctan2(arg1,arg2)-emag*arg1
    rcurr=np.zeros((6,1))
    err=abs(M2-M)
    tol=10**-2
    rcurr[0]=rijk[0]
    rcurr[1]=rijk[1]
    rcurr[2]=rijk[2]  
    rcurr[3]=vijk[0]
    rcurr[4]=vijk[1]
    rcurr[5]=vijk[2]

    return [rijk[0],rijk[1],rijk[2],vijk[0],vijk[1],vijk[2],rcurr,err]

@app.route('/', methods= ['GET'])
def app_information():
    """
    ### NEC Orbital Elements Analysis ###
    
    /                                                    (GET) print this information
    /data                                                (POST) uploads the data to the Redis database, (GET) reads the data in the database (DELETE) Deletes all data in the database.
    /jobs                                                (POST) creates a new job
    /jobs						 (GET) gets information on how to submit a job
    /jobs/<jid>                                          (GET) gets the status of the job
    /download/<jid>                                      (GET) downloads the image with the job's plots
    /oelements						 (GET) print what the variables in the data means
    /cometsindex                                         (GET) prints all of the comets in the data and their indices 
    /comet/<index>                                       (GET) prints the comet at that index in the list
    /rv/<index>                                          (GET) gets the position data and velocity of the comet at that index
    """
    return(app_information.__doc__)

@app.route('/data', methods=['POST'])
def load_data():
    """
    This function reads in Near Earth Comets' Orbital Elements data and stores it in the Redis database.
    Returns:
    A string that lets the user know that the data has been read from the file.
    """
    rd.flushdb() 
    global comet_data
  
    with open('b67r-rgxc.json', 'r') as f:
        comet_data = json.load(f)

    for item in comet_data:
        rd.set(item['object'], json.dumps(item))

    return 'Data has been read from file\n'

@app.route('/data', methods= ['GET'])
def read_data():
    """
    This function takes the Near Earth Comets' Orbital Elements data that has been loaded as a key and returns it as a JSON list.
    Returns:
    The JSON list of the Near Earth Comets' Orbital Elements data.
    """
    list_of_data = []

    for item in rd.keys():
        list_of_data.append(json.loads(rd.get(item)))

    return (f'{json.dumps(list_of_data, indent=2)}\n') 

@app.route('/data/', methods=['GET'])
def delete_data():
    """
    Deletes all of the data from the redis database.
    """
    rd.flushdb()
    return 'Data has been flushed from the database\n'

@app.route('/oelements', methods= ["GET"])
def orbital_elements():
    """
    The following contains the meaning of the variables given in the data.

    e = eccentricity of the orbit
    i = inclination; angle with respect to x-y ecliptic plane
    node = longitude of the ascending node
    TP = Time of perihelion passage (formatted as a calendar date)
    Epoch = Epoch of the elements represented as the Modified Julian Date
    w = Argument of perihelion
    q = Perihelion distance
    Q = aphelion distance
    P = sidereal orbital period
    MOID = Minimum Orbit Intersection Distance
    A1 = non-gravitational radial acceleration parameter
    A2 = non-gravitational transverse accelerational parameter
    A3 = non-gravitational normal acceleration parameter
    DT = non-gravitational perihelion maximum offset
    Ref = Orbit solution reference 
    """
    return(orbital_elements.__doc__) 

@app.route('/cometsindex', methods= ['GET'])
def index_info():
    """
    Returns a dictionary with all the comets in the data and their respective indices. 
    """
    index_dict = {}
 
    for i in range(len(comet_data)):
        index_dict[comet_data[i]['object']] = i        
    return(index_dict)

@app.route('/comet/<index>', methods=['GET'])
def get_comet(index):
    """
    Returns the dictionary with information on a specific comet
    """
    return comet_data[int(index)] 

@app.route('/jobs', methods=['GET'])
def jobs_info_api():
    """
    To submit a job, do something similar to the following (this is just an example):
    curl localhost:5022/jobs -X POST -d '{"comet": "1P/Halley"}' -H "Content-Type: application/json"
    """
    return(jobs_info_api.__doc__) 

@app.route('/jobs', methods=['POST'])
def jobs_api():
    """
    API route for creating a new job to do some analysis. This route accepts a JSON payload
    describing the job to be created.
    """
    try:
        job = request.get_json(force=True)
    except Exception as e:
        return json.dumps({'status': "Error", 'message': 'Invalid JSON: {}.'.format(e)})
    return json.dumps(add_job(job['comet']))

@app.route('/jobs/<jid>', methods= ['GET'])
def get_job_status(jid):
    """
    Returns the status of the specified job.
    """
    jobs_dict = json.loads(rd.get(generate_job_key(jid)))
    return jobs_dict  

@app.route('/rv/<index>',methods=['GET'])
def rv_data(index)->str:
    """
    Returns position and velocity of the comet at the index specified.
    """
    au2km = 1.496*10**8
    d2r=180/np.pi
    sma=( float(comet_data[int(index)]['q_au_1'])+ float(comet_data[int(index)]['q_au_2']))/2*au2km 
    emag = float(comet_data[int(index)]['e'])
    i = float(comet_data[int(index)]['i_deg'])
    sw = float(comet_data[int(index)]['w_deg'])
    bw = float(comet_data[int(index)]['node_deg'])
    nu=0
    oe=[sma,emag,i,sw,bw,nu]

    mu=1.327*10**11
    y2m = 525600
    T= float(comet_data[int(index)]['p_yr'])*y2m
    n=2*np.pi/T
    tcurr = T- float(comet_data[int(index)]['tp_tdb']) + float(comet_data[int(index)]['epoch_tdb'])
    M=n*(tcurr)
    if(M>np.pi):
        M=M-2*np.pi

    k=1000
    cond=0;
    curr=[]
    tol=1
    traj=[]
    rx,ry,rz,vx,vy,vz = ([] for h in range(6))
    for j in range(k):
        oe[5] = oe[5]+360/k
        traj.append(oe2rv(oe,mu,M))
        rx.append(traj[j][0]/au2km)
        ry.append(traj[j][1]/au2km)
        rz.append(traj[j][2]/au2km)
        vx.append(traj[j][3]/au2km)
        vy.append(traj[j][4]/au2km)
        vz.append(traj[j][5]/au2km)
        if(traj[j][7]<tol and j>0):
            tol = traj[j][7]
            curr = traj[j-1][6]/au2km
    curr2 = []
    curr2=[str(curr[0]),str(curr[1]),str(curr[2])]
    cvel = [str(curr[3]*au2km),str(curr[4]*au2km),str(curr[5]*au2km)]
    return '\n' +'Position (AU):\n' +'\n'.join(curr2) +'\n\n' + 'Velocity (km/s)\n'+'\n'.join(cvel)+'\n\n'+ 'Mean Anomaly Error (degrees): '+str(tol*180/np.pi)+'\n\n' 

@app.route('/download/<jid>', methods=['GET'])
def download(jid):
    """
    Downloads the job id image from Redis.
    """
    path = f'/app/{jid}.png'
    with open(path, 'wb') as f:
        f.write(rd.hget('image.{}'.format(jid), 'image'))
    return send_file(path, mimetype='image/png', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
