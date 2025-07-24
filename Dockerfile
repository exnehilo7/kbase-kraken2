FROM kbase/sdkpython:3.8.0

LABEL key="Mark Flynn"
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

# RUN apt-get update

RUN apt-get update && apt-get -y upgrade \
    && apt-get install -y --no-install-recommends \
        git \
        wget

# -----------------------------------------
# Install prerequisites


# -- original code: -------------------------------
# RUN conda install -yc \
#     bioconda pandas kraken2 jinja2 nose requests \
#     && pip install jsonrpcbase coverage
# ---------------------------------------------------------

RUN conda update -n base conda

RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# bioconda no longer required?
RUN conda create -n py313 python=3.13 \
    && source activate py313 \
    && conda config --add channels bioconda 
    # && conda config --add channels conda-forge 

RUN conda install -y pandas 
RUN conda install -y kraken2 
RUN conda install -y jinja2 
RUN conda install -y nose  
RUN conda install -y requests 
RUN pip install jsonrpcbase 
RUN pip install coverage 
RUN conda clean -afy


WORKDIR /kb/module

# ncbi-blast+ is already installed in bioperl
RUN apt update
RUN apt-get install -y build-essential
RUN apt-get install -y autoconf
RUN apt-get install -y autogen
RUN apt-get install -y libssl-dev
RUN apt-get install -y bioperl

RUN cd ../ && \
    git clone https://github.com/marbl/Krona && \
    cd Krona/KronaTools && \
    ./install.pl --prefix /kb/deployment && \
    mkdir taxonomy && \
    ./updateTaxonomy.sh

# -- Was commented out by original author -------------------------------
# Install kraken2
#RUN cd /usr/ && \
#    wget http://github.com/DerrickWood/kraken2/archive/v2.0.7-beta.tar.gz && \
#    tar xzvf v2.0.7-beta.tar.gz && \
#    cd kraken2-2.0.7-beta && \
#    ./install_kraken2.sh /usr/local/bin/kraken2-v2.0.7 && \
#    ln -s /usr/local/bin/kraken2-v2.0.7/kraken2* /usr/local/bin/ && \
#    kraken2-build -h
# ---------------------------------------------------------------------

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module
RUN chmod +x /kb/module/lib/kraken2/src/kraken2.sh

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
