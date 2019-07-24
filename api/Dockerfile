FROM dannixon/savu:latest

# Install additional Python dependencies
ADD requirements.txt \
    /requirements.txt
RUN /miniconda/bin/pip install -r /requirements.txt && \
    rm /requirements.txt && /miniconda/bin/pip install pydevd


# Clone the latest suitable release for the hebi application
# TODO create a special branch for IDaaS
RUN git clone --single-branch --branch master https://github.com/dtasev/hebi /hebi && \
    cp -r /hebi/api/webservice /webservice && \
    cp /hebi/api/config/dls.json /hebi_config.json

# Expose API port
EXPOSE 5000

# TODO IDaaS folder mounts - this will be specific to the VMs

# Run server
CMD ["/webservice/run.sh"]
