FROM dannixon/savu:latest

# Install additional Python dependencies
ADD requirements.txt \
    /requirements.txt

# Install project requirements, AND install pydevd - for remote debugging with PyCharm
RUN /miniconda/bin/pip install -r /requirements.txt && \
    rm /requirements.txt && /miniconda/bin/pip install pydevd

# Copy API application configuration
ADD ./config/dls.json \
    /hebi_config.json

# Expose API port
EXPOSE 5000

# Run server
CMD ["/webservice/run.sh"]

# Note: application files not added, they must be mounted
# via `docker run` via `-v/--mount /development/source:/webservice`