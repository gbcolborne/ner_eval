#! /usr/bin/env bash

# Installs NeuroNER (see
# https://github.com/Franck-Dernoncourt/NeuroNER/blob/master/install_ubuntu.sh)

print_usage() {
    echo -e "Usage: $0 [install-directory]"
    echo
    echo "Args:"
    echo -e "\t-install-directory"
}

if [ "$#" -ne 1 ]; then
    print_usage
    exit 1
fi
if [[ $1 == "-h" || $1 == "--help" ]]; then
    print_usage
    exit 0
fi

# Install TensorFlow and other dependencies
echo "Installing dependencies..."
sudo pip install -U networkx matplotlib scikit-learn scipy pycorenlp
sudo pip install -U tensorflow

# Install SpaCy
sudo pip install -U spacy
sudo python -m spacy download en

# Install NeuroNER
echo "Installing NeuroNER-master in $1..."
cd $1
wget https://github.com/Franck-Dernoncourt/NeuroNER/archive/master.zip
unzip master.zip

# Clean up
rm master.zip

# Fix some known bugs in NeuroNer
# (https://github.com/Franck-Dernoncourt/NeuroNER/issues/87 and
# https://github.com/Franck-Dernoncourt/NeuroNER/issues/76).
echo "Fixing a few bugs..."
cd NeuroNER-master/src
cat main.py | sed "s/^\(from neuroner import NeuroNER\)$/\1\\nfrom distutils import util/" > main.py.tmp
mv main.py.tmp main.py
cat utils_plots.py | sed "s/ax = pc.get_axes()/ax = pc.axes/" > utils_plots.py.tmp
mv utils_plots.py.tmp utils_plots.py

