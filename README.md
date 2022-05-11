# Near Earth Comets Orbital Elements Analysis

This project works with Near Earth Comets' orbital elements data from NASA and performs various operations to sort through the different comet data, add jobs to the queue to plot the trajectory of a given comet, get the status of the job, and download the plot image. This repository contains 2 Dockerfiles--one for the worker and one for the api, a Makefile, 3 python scripts, a tester script, 6 production yml files, and 6 test yml files.

Before interacting with this application, you must first download the data set used by inputting the following in your terminal:

> wget https://data.nasa.gov/resource/b67r-rgxc.json

## How To Deploy the Application on Kubernetes
To deploy the application on the kubernetes cluster, you must first ssh to k8s like the following:
> ssh username@coe332-k8s.tacc.cloud

Once here you need to git clone the repository:
> git clone https://github.com/niccoleriera/NEC-orbital-elements-analysis

Apply the files as follows:

> kubectl apply -f app-prod-db-pvc.yml
> kubectl apply -f app-prod-db-deployment.yml
> kubectl apply -f app-prod-db-service.yml
> kubectl apply -f app-prod-api-service.yml
> kubectl apply -f app-prod-api-deployment.yml
> kubectl apply -f app-prod-wrk-deployment.yml

To make sure everything is up and running, do the following
> kubectl get deployments
> kubectl get pods

Everything should say running.

## How to run the Test Script
First make sure to install pytest
> pip3 install --user pytest

Additionally, this tester script requries the requests module:
> pip3 install --user requests

To run the tests, simply, put "pytest" into the command line.

## How to Interact With the System for CRUD Operations
To add the data to the Redis database:
> curl https://isp-proxy.tacc.utexas.edu/nriera-1/data -X POST 

To read the data that was uploaded to the database:
> curl https://isp-proxy.tacc.utexas.edu/nriera-1/data 

The data is formatted with variables like 'e' and 'w'. The following shows the meaning of each variable:
> curl https://isp-proxy.tacc.utexas.edu/nriera-1/oelements

The following gives a list of the comets that are in the data and their respective indices in the list:
> curl https://isp-proxy.tacc.utexas.edu/nriera-1/cometsindex

The following gives the dictionary of a specific comet at its index in the list:
> curl https://isp-proxy.tacc.utexas.edu/nriera-1/comet/<index> 

## How to Create Jobs and Retrieve Results
To create a job:
> curl https://isp-proxy.tacc.utexas.edu/nriera-1/jobs -X POST -d '{"comet": "1P/Halley"}' -H "Content-Type: application/json"

You can input whichever comet whose trajectory you would like to plot. 

To get the job's status:
> curl https://isp-proxy.tacc.utexas.edu/nriera-1/jobs/<jid> 

Once the status says complete, that means that the worker has finished plotting its trajectory. 

To download the image made by the worker:
> curl https://isp-proxy.tacc.utexas.edu/nriera-1/download/<jid> > output.png

To download the image to your computer:
> scp username@isp02.tacc.utexas.edu:~/output.png .

## Sources
“Near-Earth Comets - Orbital Elements API.” NASA, NASA, data.nasa.gov/Space-Science/Near-Earth-Comets-Orbital-Elements-API/ysqn-vd8v. 
