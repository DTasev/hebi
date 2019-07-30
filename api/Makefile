all: build run

build-master:
	sudo docker build -t hebi -f Dockerfile .

build-dev:
	# This installs the dependencies in a docker image
	# the source needs to be mounted manually at container:/webservice,
    # and savu needs to be mounted at container:/savu_custom
	sudo docker build -t hebi-dev -f dev.Dockerfile .

run:
	docker run --network=host \
	    -v ~/dev/hebi/api:/webservice \
	    -v /mnt/e/:/data:ro \
	    -v ~/dev/hebi/output:/output:rw  \
	    -v ~/dev/savu:/savu_custom:ro  \
	    -e PUID=$$(id -u) -e PGID=$$(id -g) -it unhebi /bin/bash
