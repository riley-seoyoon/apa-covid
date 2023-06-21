FROM ubuntu:22.04

LABEL SeoYoonPark "sypark217@snu.ac.kr"

ENV TZ="Asia/Seoul"
ARG DEBIAN_FRONTEND=noninteractive 
SHELL ["/bin/bash", "-c"]

RUN apt update && apt install -y \
    libpq-dev \
    pkg-config \
    wget \
    emacs \
    unzip \
    tzdata \
    software-properties-common

RUN apt update && apt upgrade -y

RUN wget -O miniconda3.sh http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && chmod +x miniconda3.sh \
    && ./miniconda3.sh -b \
    && rm ./miniconda3.sh

ENV PATH /root/miniconda3/bin:$PATH

RUN add-apt-repository ppa:git-core/ppa && add-apt-repository ppa:marutter/rrutter4.0 && \
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9 \
    && apt update

RUN apt install -y r-base

RUN apt install -y r-cran-tidyverse \
    libcurl4-openssl-dev \
    r-cran-biocmanager

RUN conda install -y --channel conda-forge radian

CMD ["/bin/bash"]
