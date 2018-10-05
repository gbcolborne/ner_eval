#! /usr/bin/env bash

# Installs CRF++
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

# Download and unzip
cd $1
wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=0B4y35FiV1wh7QVR6VXJ5dWExSTQ' -O CRF++-0.58.tar.gz
tar -xvzf CRF++-0.58.tar.gz

# Install
cd CRF++-0.58
./configure
make
sudo make install

# Clean up
cd ..
rm CRF++-0.58.tar.gz

echo
echo "To test installation, try the commands crf_learn and crf_test."
echo "You may need to copy libcrfpp.so.O from /usr/local/lib to /usr/lib."
echo 
