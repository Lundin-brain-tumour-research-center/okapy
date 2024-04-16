###############################################################################
# Base image
###############################################################################
FROM mambaorg/micromamba:1.5.6

###############################################################################
# Basic setup
###############################################################################

# mambaorg/micromamba defaults to a non-root user. Add a "USER root" to install packages as root:
USER root

# Set working directory
WORKDIR /app

# Generate version file
ARG VERSION=unknown
RUN echo "${VERSION}" > /app/VERSION

# Add cv2 dependencies (ffmpeg libsm6 libxext6); 'procps' needed by nextflow
RUN apt-get update && \
    apt-get install apt-transport-https -y && \
    apt-get install ffmpeg libsm6 libxext6 procps -y

###############################################################################
# Install code
###############################################################################

# Copy project files
COPY okapy ./okapy
COPY assets ./assets
COPY bin ./bin
COPY README.md ./

###############################################################################
# Configure the entrypoint scripts
###############################################################################

# Copy the entrypoint scripts and make it executable
RUN chmod +x /app/bin/*

# Create entrypoint to run executable script in environment
# -> No entrypoint: import issues, not compatible with nextflow
#ENTRYPOINT ["micromamba", "run", "-n", "base", "python",  "/app/bin/segmentation_converter.py"]

###############################################################################
# Create micromamba environment
###############################################################################

ENV MAMBA_ROOT_PREFIX=/home/mambauser/mamba_envs
ENV PYTHONPATH=/app
# Copy conda environment file and install environment with micromamba
COPY  conda/environment.yml environment.yml
RUN micromamba install --yes --name base -f environment.yml   && \
    micromamba clean --all --yes
RUN micromamba config set use_lockfiles False

# Activate micromamba environment
ARG MAMBA_DOCKERFILE_ACTIVATE=1

###############################################################################
# Container Image Metadata (label schema: http://label-schema.org/rc1/)
###############################################################################

ARG BUILD_DATE=today
ARG VCS_REF=unknown

LABEL org.label-schema.build-date=${BUILD_DATE} \
    org.label-schema.name="OkaPy" \
    org.label-schema.description="OkaPy" \
    org.label-schema.version=${VERSION} \
    org.label-schema.maintainer="Daniel Abler" \
    org.label-schema.vcs-ref=${VCS_REF} \
    org.label-schema.vcs-url="https://github.com/Lundin-brain-tumour-research-center/okapy.git" \
    org.label-schema.schema-version="1.0" \
    org.label-schema.docker.cmd="TBC" \
    org.label-schema.docker.cmd.test="TBC"






