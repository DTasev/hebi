FROM dtasev/savu:latest

# Install additional Python dependencies
ADD requirements.txt /requirements.txt

RUN yum install -y git wget && \
    /miniconda/bin/pip install -r /requirements.txt && \
    rm /requirements.txt && /miniconda/bin/pip install pydevd && \
    git clone --single-branch --branch master https://github.com/dtasev/hebi /hebi && \
    cp -r /hebi/api/ /webservice && \
    cp /hebi/api/config/dls.json /hebi_config.json

# Expose API port
EXPOSE 5000

# TODO IDaaS folder mounts - this will be specific to the VMs

# Run server
CMD ["/webservice/run.sh"]
