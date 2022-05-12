NAME="niccoleriera"
APP="necelements"
VER="latest"
FPORT="5022"
RPORT="6422"
UID="876531"
GID="816966"

list:
	- docker images | grep ${NAME}
	- docker ps -a | grep ${NAME}

build-db:
	docker pull redis:6

build-api:
	docker build -t ${NAME}/${APP}_api:${VER} -f docker/Dockerfile.api .

build-wrk:
	docker build -t ${NAME}/${APP}_wrk:${VER} -f docker/Dockerfile.wrk .

run-db: build-db
	docker run --name ${NAME}_${APP}_db -p ${RPORT}:6379 -d -u ${UID}:${GID} -v ${PWD}/data/:/data redis:6 --save 1 1

run-api: build-api
	RIP=$$(docker inspect ${NAME}_${APP}_db | grep \"IPAddress\" | head -n1 | awk -F\" '{print $$4}') && \
	docker run --name ${NAME}_${APP}_api --env REDIS_IP=$${RIP} -p ${FPORT}:5000 -d ${NAME}/${APP}_api:${VER}

run-wrk: build-wrk
	RIP=$$(docker inspect ${NAME}_${APP}_db | grep \"IPAddress\" | head -n1 | awk -F\" '{print $$4}') && \
	docker run --name ${NAME}_${APP}_wrk --env REDIS_IP=$${RIP} -d ${NAME}/${APP}_wrk:${VER}

rm-db:
	- docker rm -f ${NAME}_${APP}_db

rm-api:
	- docker rm -f ${NAME}_${APP}_api 

rm-wrk:
	- docker rm -f ${NAME}_${APP}_wrk 

push-api:
	docker push ${NAME}/${APP}_api:${VER}
	
push-wrk:
	docker push ${NAME}/${APP}_wrk:${VER}

push-all: push-api push-wrk

deploy-test:
	kubectl apply -f kubernetes/test/app-test-db-pvc.yml
	kubectl apply -f kubernetes/test/app-test-db-service.yml
	kubectl apply -f kubernetes/test/app-test-db-deployment.yml
	kubectl apply -f kubernetes/test/app-test-api-service.yml
	kubectl apply -f kubernetes/test/app-test-api-deployment.yml
	kubectl apply -f kubernetes/test/app-test-wrk-deployment.yml

deploy-prod:
	kubectl apply -f kubernetes/prod/app-prod-db-pvc.yml
	kubectl apply -f kubernetes/prod/app-prod-db-service.yml
	kubectl apply -f kubernetes/prod/app-prod-db-deployment.yml
	kubectl apply -f kubernetes/prod/app-prod-api-service.yml
	kubectl apply -f kubernetes/prod/app-prod-api-deployment.yml
	kubectl apply -f kubernetes/prod/app-prod-wrk-deployment.yml
cycle-api: rm-api build-api run-api

cycle-db: rm-db build-db run-db

cycle-wrk: rm-wrk build-wrk run-wrk

all: cycle-db cycle-api cycle-wrk
