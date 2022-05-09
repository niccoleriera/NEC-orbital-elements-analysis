import json
import os
import uuid
import redis
import numpy as np
import matplotlib.pyplot as plt 
from hotqueue import HotQueue

#redis_ip = os.environ.get('REDIS_IP')
#if not redis_ip:
#    raise Exception()
redis_ip = '172.17.0.4'
rd = redis.Redis(host=redis_ip, port='6379', db=0)
q = HotQueue("queue", host=redis_ip, port='6379', db=1)

def generate_jid():
    """
    This function generates the job ID for the jobs.
    """
    return str(uuid.uuid4())

def generate_job_key(jid):
    """
    """
    return 'job.{}'.format(jid)

def instantiate_job(jid, status, start, end):
    """
    This function creates a python dictionary to store the job id, status, and start and end parameters.
    """
    if type(jid) == str:
        return {'id': jid, 'status': status, 'start': start, 'end': end}
    return {'id': jid.decode('utf-8'), 'status': status.decode('utf-8'), 'start': start.decode('utf-8'), 'end': end.decode('utf-8')}

def save_job(job_key, job_dict):
    rd.set(job_key, job_dict)

def queue_job(jid):
    q.put(jid) 

def add_job(start, end):
    jid = generate_jid()
    job_dict = instantiate_job(jid, "submitted", start, end)
    save_job(generate_job_key(jid), json.dumps(job_dict)) 
    queue_job(jid)
    return job_dict

def update_job_status(jid, status):
    job = json.loads(rd.get(generate_job_key(jid))) 

    if job:
        job['status'] = status
        save_job(generate_job_key(jid), json.dumps(job)) 
    else:
        raise Exception()

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
