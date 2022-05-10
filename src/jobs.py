import json
import os
import uuid
import redis
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


def instantiate_job(jid, status, comet):
    """
    This function creates a python dictionary to store the job id, status, and start and end parameters.
    """
    if type(jid) == str:
        return {'id': jid, 'status': status, 'comet': comet}
    return {'id': jid.decode('utf-8'), 'status': status.decode('utf-8'), 'comet': comet.decode('utf-8')}

def save_job(job_key, job_dict):
    rd.set(job_key, job_dict)

def queue_job(jid):
    q.put(jid) 

def add_job(comet):
    jid = generate_jid()
    job_dict = instantiate_job(jid, "submitted", comet)
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

def add_key(jid, key, value):
    job_dict = json.loads(rd.get(generate_job_key(jid)))
    job_dict[key] = value
    save_job(generate_job_key(jid), json.dumps(job_dict)) 

def save_job_image(jid, value):
    rd.hset('image.{}'.format(jid), 'image', value) 

def get_comet_dict(jid):
    job_dict = json.loads(rd.get(generate_job_key(jid)))
    comet = job_dict['comet'] 
    return json.loads(rd.get(str(comet))) 
