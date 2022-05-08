import json
import os
import uuid
from flask import Flask, request, send_file
import redis
from hotqueue import HotQueue

redis_ip = os.environ.get('REDIS_IP')
if not redis_ip:
    raise Exception()

rd = redis.Redis(host=redis_ip, port=6379, db=0)
q = HotQueue("queue"m host=redis_ip, port=6379, db=1)

def generate_jid():
    """
    This function generates the job ID for the jobs.
    """
    return str(uuid.uuid4())

def generate_job_key(jid):
    """
    """
    return 'job.{}'.format(jid)

def instantiate_job(jid, start, end):
    """
    This function creates a python dictionary to store the job id, status, and start and end parameters.
    """
    if type(jid) == str:
        return {'id': jid, 'status': status, 'start': start, 'end': end}
    return {'id': jid.decode('utf-8'), 'status': status.decode('utf-8'), 'start': start.decode('utf-8'), 'end': end.decode('utf-8')}

def save_job(job_key, job_dict):
    rd.hset(job_key, mapping=job_dict)

def queue_job(jid):
    q.put(jid) 

def add_job(start, end, status="submitted"):
    jid = generate_jid()
    job_dict = instantiate_job(jid, status, start, end)
    save_job(generate_job_key(jid), job_dict) 
    queue_job(jid)
    return job_dict

def updata_job_statues(jid, status):
    job = get_job_by_id(jid)
    if job:
        job['status'] = status
        save_job(generate_job_key(jid), job)

