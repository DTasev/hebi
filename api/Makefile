OWNER=dtasev
DOCKERNAME=hebi
DOCKERNAME_DEV=hebi:dev

all: build-dev run

build-master:
	docker build -t $(OWNER)/$(DOCKERNAME) -f Dockerfile .

build-push-master: build-master
	docker push $(OWNER)/$(DOCKERNAME)

build-dev:
	# This installs the dependencies in a docker image
	# the source needs to be mounted manually at container:/webservice,
	# and savu needs to be mounted at container:/savu_custom
	docker build -t $(OWNER)/$(DOCKERNAME_DEV) -f dev.Dockerfile .

build-push-dev: build-dev
    docker push $(OWNER)/$(DOCKERNAME_DEV)

default_cmd = docker run

default_args = --gpus=all --network=host \
	    -v ~/dev/hebi/api:/webservice \
	    -v /mnt/e/:/data:ro \
	    -v /mnt/e/savu_output:/output:rw  \
	    -v ~/dev/savu:/savu_custom:ro  \
	    -e PUID=$$(id -u) -e PGID=$$(id -G) -it $(OWNER)/$(DOCKERNAME_DEV)
run:
	$(default_cmd) $(default_args)

run-gpu:
	$(default_cmd) --runtime=nvidia $(default_args)

run-bash:
	$(default_cmd) $(default_args) /bin/bash
