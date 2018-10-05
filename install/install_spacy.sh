#! /usr/bin/env bash

# Installs SpaCY
print_usage() {
    echo "Usage: $0 [-cuda9]"
    echo
    echo "Options:"
    echo "  -cuda9: CUDA version is 9.0 rather than 8.0"
}

if [[ $1 == "-h" || $1 == "--help" ]]; then
    print_usage
    exit 0
fi
if [[ $1 == "-cuda9" ]]; then
    # SpaCy assumes CUDA 8.0 by default. If using version 9.0, we have
    # to set the environment variable CUDA9. See
    # https://spacy.io/usage/.
    export CUDA9=1
fi

# Make sure CUDA_HOME has been set
if [[ -z "${CUDA_HOME}" ]]; then
    echo "Error: Please set CUDA_HOME environment variable (e.g. /usr/local/cuda-8.0)"
    exit 1
fi

# Make sure CUDA binaries are on PATH
export PATH=$PATH:$CUDA_HOME/bin

# Install SpaCy
echo "Installing SpaCy..."
sudo pip install -U spacy

# Download models
python -m spacy download en 
python -m spacy download en_core_web_md
