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

# License is now required for Anaconda
# RUN conda update -n base conda

# # TRY MAMBA?
# RUN rm -rf /opt/conda3 \
#     && rm -rf ~/.condarc ~/.conda
# RUN wget "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
# RUN bash Miniforge3-$(uname)-$(uname -m).sh -b


RUN rm /bin/sh && ln -s /bin/bash /bin/sh

ENV PATH="/root/.pixi/bin:${PATH}"

# RUN echo 'export PATH="/root/.pixi/bin:$PATH"' >> /root/.bashrc \
#     && source /root/.bashrc

# RUN echo $PATH \
#     && more /root/.bashrc


# TRY PIXI?
# RUN wget -qO- https://pixi.sh/install.sh | sh

# Restart the shell to ensure pixi is in the path
# RUN export PATH="/root/.pixi/bin:$PATH"
# RUN echo 'export PATH="/root/.pixi/bin:$PATH"' >> /root/.bashrc
# RUN source /root/.bashrc

RUN wget -qO- https://pixi.sh/install.sh | sh

# RUN export PATH="/root/.pixi/bin:$PATH"

# RUN pixi init py313 \ 
#     && cd py313 \
#     && pixi add python=3.13 \
#     && pixi add pandas \
#     && pixi project channel add bioconda \
#     && pixi add kraken2 \
#     && pixi add jinja2 \
#     && pixi add nose \
#     && pixi add requests

WORKDIR /kb

RUN pixi init module \ 
    && cd module \
    && pixi add python=3.13 \
    && pixi add pandas \
    && pixi project channel add bioconda \
    && pixi add kraken2 \
    && pixi add jinja2 \
    && pixi add nose \
    && pixi add requests

RUN pip install jsonrpcbase \
    && pip install coverage


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

# RUN echo 'export PYTHONPATH="/py313"' >> /root/.bashrc
RUN echo 'alias python="pixi run python"' >> /root/.bashrc \
    && echo 'alias python3="pixi run python"' >> /root/.bashrc \
    && source /root/.bashrc

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
