# Use nvidia L4T as base image
FROM nvcr.io/nvidia/l4t-base:r36.2.0

WORKDIR /

RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
       	build-essential \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    \
    && gcc --version \
    && g++ --version

# Install python
ARG PYTHON_VERSION_ARG="3.10"

ENV PYTHON_VERSION=${PYTHON_VERSION_ARG} \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_CACHE_PURGE=true \
    PIP_ROOT_USER_ACTION=ignore \
    TWINE_NON_INTERACTIVE=1 \
    DEBIAN_FRONTEND=noninteractive

RUN set -x \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
	python${PYTHON_VERSION} \
	python${PYTHON_VERSION}-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && curl -sS https://bootstrap.pypa.io/get-pip.py | python${PYTHON_VERSION} || \
       curl -sS https://bootstrap.pypa.io/pip/3.6/get-pip.py | python3.6 \
    && ln -s /usr/bin/python${PYTHON_VERSION} /usr/local/bin/python3 \
    && which python3 \
    && python3 --version \
    && which pip3 \
    && pip3 --version \
    && python3 -m pip install --upgrade pip --index-url https://pypi.org/simple \
    && pip3 install --no-cache-dir --verbose --no-binary :all: psutil \
    && pip3 install --upgrade --no-cache-dir \
       	    setuptools \
   	    packaging \
   	    'Cython<3' \
   	    wheel

# Copy rrms-utils
COPY rrms-utils /rrms-utils
RUN cd /rrms-utils/ && pip3 install .

# Copy analytics
COPY analytics /analytics
RUN cd /analytics && pip3 install --ignore-installed --no-cache-dir  .

WORKDIR /analytics
