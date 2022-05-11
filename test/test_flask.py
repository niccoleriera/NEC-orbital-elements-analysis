import json
import os
import re
import time 

import pytest, requests

api_host = os.environ.get('REDIS_IP', 'localhost')
api_port = '5022'
api_prefix = f'http://{api_host}:{api_port}' 

def test_info():
    route = f'{api_prefix}/'
    response = requests.get(route) 

    assert response.ok == True
    assert response.status_code == 200

def test_data_load():
    route = f'{api_prefix}/data'
    response = requests.post(route) 

    assert response.ok == True
    assert response.status_code == 200
    assert response.content == b'Data has been read from file\n' 

def test_data_read():
    route = f'{api_prefix}/data'
    response = requests.get(route) 
    assert response.ok == True
    assert response.status_code == 200
    assert isinstance(response.json(), list) == True
    assert isinstance(response.json()[0], dict) == True
    assert 'object' in response.json()[0].keys() 

def test_orbital_elements():
    route = f'{api_prefix}/oelements'
    response = requests.get(route)

    assert response.ok == True
    assert response.status_code == 200

def test_cometsindex():
    route = f'{api_prefix}/cometsindex'
    response = requests.get(route)
    
    assert response.ok == True
    assert response.status_code == 200
    assert isinstance(response.json(), dict) == True

def test_comet_index():
    route = f'{api_prefix}/comet/2'
    response = requests.get(route)

    assert response.ok == True
    assert response.status_code == 200
    assert isinstance(response.json(), dict) == True
    assert 'object' in response.json().keys()

def test_jobs_info():
    route = f'{api_prefix}/jobs'
    response = requests.get(route) 
 
    assert response.ok == True
    assert response.status_code == 200 
    assert bool(re.search('To submit a job', response.text)) == True 

def test_jobs_cycle():
    route = f'{api_prefix}/jobs'
    job_data = {'comet': '1P/Halley'} 
    response = requests.post(route, json=job_data)

    assert response.ok == True 
    assert response.status_code == 200
    
    UUID = response.json()['id']
    assert response.json()['status'] == 'submitted'

    time.sleep(8)
    route = f'{api_prefix}/jobs/{UUID}'
    response = requests.get(route)
    
    assert response.ok == True
    assert response.status_code == 200 

    assert response.json()['status'] == 'complete' 
