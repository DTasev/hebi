FROM dannixon/savu:latest

# Install additional Python dependencies
ADD requirements.txt \
    /requirements.txt
RUN /miniconda/bin/pip install -r /requirements.txt && \
    rm /requirements.txt

RUN /miniconda/bin/pip install pydevd

# Add Python application
#ADD . /webservice

# Copy API application configuration
ADD ./config/dls.json \
    /hebi_config.json

# Expose API port
EXPOSE 5000

# Run server
CMD ["/webservice/run.sh"]
