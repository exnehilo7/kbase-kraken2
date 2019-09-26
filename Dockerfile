FROM kbase/sdkbase2:python
MAINTAINER Mark Flynn
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

# RUN apt-get update


# -----------------------------------------
# Install prerequisites
RUN apt update && \
    apt-get install -y build-essential wget unzip python2.7 \
    python-dev git python-pip curl autoconf autogen libssl-dev \
    ncbi-blast+

# Install kraken2
RUN cd /usr/ && \
    wget http://github.com/DerrickWood/kraken2/archive/v2.0.7-beta.tar.gz && \
    tar xzvf v2.0.7-beta.tar.gz && \
    cd kraken2-2.0.7-beta && \
    ./install_kraken2.sh /usr/local/bin/kraken2-v2.0.7 && \
    ln -s /usr/local/bin/kraken2-v2.0.7/kraken2* /usr/local/bin/ && \
    kraken2-build -h
COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
