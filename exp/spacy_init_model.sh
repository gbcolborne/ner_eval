#! /usr/bin/env bash

# Initializes a SpaCy model using pre-trained word embeddings

print_usage() {
    echo -e "Usage: $0 [language path-embeddings nb-words-kept path-model]"
    echo
    echo "Args:"
    echo -e "\t-language: code of a language supported by SpaCy (e.g. en, fr, es, it, etc.)."
    echo -e "\t-path-embeddings: path of word embeddings in word2vec text format"
    echo -e "\t-nb-words-kept: nb unique embeddings the vocab is pruned to (-1 for no pruning)"
    echo -e "\t-path-model: path where model will be written"
    
}

if [[ $1 == "-h" || $1 == "--help" ]]; then
    print_usage
    exit 0
fi
if [ "$#" -ne 4 ]; then
    print_usage
    exit 1
fi

# Initialize model
echo "Initializing model..."
python -m spacy init-model $1 $4 --vectors-loc $2 --prune-vectors $3

