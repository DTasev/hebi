FROM dtasev/savu:latest

ARG SAVU_REVISION=master

# Install additional Python dependencies
COPY requirements.txt dev.requirements.txt /

# Install project requirements, AND install pydevd - for remote debugging with PyCharm
RUN yum install -y which && \
    /miniconda/bin/pip install -r /requirements.txt -r /dev.requirements.txt && \
    rm /dev.requirements.txt /requirements.txt

# Copy API application configuration
ADD ./config/dls.json /hebi_config.json

# Pick up savu custom source, if provided
RUN echo "export PYTHONPATH=/savu_custom" >> /savu_setup.sh

# Expose API port
EXPOSE 5000

# Run server
CMD ["/webservice/run.sh"]

# Note: application files not added, they must be mounted
# via `docker job` via `-v/--mount /development/source:/webservice`