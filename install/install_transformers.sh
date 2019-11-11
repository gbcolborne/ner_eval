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
conda install pytorch==1.0.0 torchvision==0.2.1 cuda80 -c pytorch
pip install transformers==2.1.1

