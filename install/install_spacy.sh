#! /usr/bin/env bash

# Installs SpaCY
print_usage() {
    echo -e "Usage: $0"
}

if [[ $1 == "-h" || $1 == "--help" ]]; then
    print_usage
    exit 0
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
