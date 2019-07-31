OWNER=dtasev
DOCKERNAME=hebi
DOCKERNAME_DEV=hebi:dev

all: build-dev run

build-master:
	sudo docker build -t $(DOCKERNAME) -f Dockerfile .

build-push-dev: build-master
	docker push $(OWNER)/$(DOCKERNAME)

build-dev:
	# This installs the dependencies in a docker image
	# the source needs to be mounted manually at container:/webservice,
    # and savu needs to be mounted at container:/savu_custom
	sudo docker build -t $(DOCKERNAME_DEV) -f dev.Dockerfile .

build-push-dev: build-dev
    docker push $(OWNER)/$(DOCKERNAME_DEV)

default_run = docker run --network=host \
	    -v ~/dev/hebi/api:/webservice \
	    -v /mnt/e/:/data:ro \
	    -v ~/dev/hebi/output:/output:rw  \
	    -v ~/dev/savu:/savu_custom:ro  \
	    -e PUID=$$(id -u) -e PGID=$$(id -g) -it $(DOCKERNAME_DEV)
run:
	$(default_run)

run-bash:
	$(default_run) /bin/bash
