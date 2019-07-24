all: build run

build:
	sudo docker build -t hebi -f Dockerfile .
run:
	docker run --network=host \
	    -v ~/dev/hebi/api:/webservice \
	    -v /mnt/e/:/data:ro \
	    -v ~/dev/hebi/output:/output:rw  \
	    -v ~/dev/savu:/savu_custom:ro  \
	    -e PUID=$$(id -u) -e PGID=$$(id -g) -it unhebi /bin/bash
