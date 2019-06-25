all: build run

build:
	sudo docker build -t hebi -f Dockerfile .
run:
	sudo docker run --network=host -v ~/dev/hebi/api:/webservice:rw -v /mnt/e/:/data:rw -it hebi
