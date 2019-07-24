FROM dannixon/savu:latest

ARG SAVU_REVISION=master

# Install additional Python dependencies
COPY requirements.txt dev.requirements.txt /

# Install project requirements, AND install pydevd - for remote debugging with PyCharm
RUN /miniconda/bin/pip install -r /requirements.txt -r /dev.requirements.txt && \
    rm /dev.requirements.txt /requirements.txt

# Copy API application configuration
ADD ./config/dls.json /hebi_config.json

# Expose API port
EXPOSE 5000

# Run server
CMD ["/webservice/run.sh"]

# Note: application files not added, they must be mounted
# via `docker run` via `-v/--mount /development/source:/webservice`