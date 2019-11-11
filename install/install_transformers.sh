#! /usr/bin/env bash

# Installs PyTorch and the Transformers Library
print_usage() {
    echo "Usage: $0"
    echo
    echo "Options:"
}

if [[ $1 == "-h" || $1 == "--help" ]]; then
    print_usage
    exit 0
fi

# Install PyTorch and Transformers
conda install pytorch==1.2.0 torchvision==0.4.0 cudatoolkit=10.0 -c pytorch
pip install transformers==2.1.1

# Install dependencies for run_transformer_ner.py script
pip install seqeval==0.0.12 
pip install tensorboardX==1.9