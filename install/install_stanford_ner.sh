#! /usr/bin/env bash

# Installs Stanford NER
print_usage() {
    echo "Usage: $0 [install-directory]"
    echo
    echo "Args:"
    echo "  -install-directory"
}

if [ "$#" -ne 1 ]; then
    print_usage
    exit 1
fi
if [[ $1 == "-h" || $1 == "--help" ]]; then
    print_usage
    exit 0
fi

# Download
echo "Installing stanford-ner-2018-02-17 in $1."
cd $1
wget https://nlp.stanford.edu/software/stanford-ner-2018-02-27.zip
unzip stanford-ner-2018-02-27.zip

# Clean up
rm stanford-ner-2018-02-27.zip
