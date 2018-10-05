#! /usr/bin/env bash

# Download some GloVe embeddings

print_usage() {
    echo -e "Usage: $0 download-directory"
    echo
    echo "Args:"
    echo -e "\t-download-directory"
}

if [ "$#" -ne 1 ]; then
    print_usage
    exit 1
fi
if [[ $1 == "-h" || $1 == "--help" ]]; then
    print_usage
    exit 0
fi


cd $1
wget http://neuroner.com/data/word_vectors/glove.6B.100d.zip
unzip glove.6B.100d.zip
wget http://neuroner.com/data/word_vectors/glove.840B.300d.zip
unzip glove.840B.300d.zip
