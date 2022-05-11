NAME="pavanshukla99"
APP="necelements"
VER="latest"
FPORT="5030"
RPORT="6430"
UID="872932"
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
	RIP=$$(docker inspect ${NAME}_db | grep \"IPAddress\" | head -n1 | awk -F\" '{print $$4}') && \
	docker run --name ${NAME}_${APP}_api --env REDIS_IP=${RIP} -p ${FPORT}:5000 -d ${NAME}/${APP}_api:${VER}

run-wrk: build-wrk
	RIP=$$(docker inspect ${NAME}_db | grep \"IPAddress\" | head -n1 | awk -F\" '{print $$4}') && \
	docker run --name ${NAME}_${APP}_wrk --env REDIS_IP=${RIP} -d ${NAME}/${APP}_wrk:${VER}

rm-db:
	- docker rm -f ${NAME}_${APP}_db

rm-api:
	- docker rm -f ${NAME}_${APP}_api 

rm-wrk:
	- docker rm -f ${NAME}_${APP}_wrk

cycle-api: rm-api build-api run-api

cycle-db: rm-db build-db run-db

cycle-wrk: rm-wrk build-wrk run-wrk

all: cycle-db cycle-api cycle-wrk
