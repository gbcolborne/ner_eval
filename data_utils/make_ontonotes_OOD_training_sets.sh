#! /usr/bin/env bash

# Make out-of-domain (leave-one-out) training set for each of the
# domains in OntoNotes.


print_usage() {
    echo "Usage: $0 [path-data path-output]"
    echo
    echo "Args:"
    echo "  -path-data path of dir containing a file ontonotes.<name>.train.iob for each of the following domain names: bc, bn, mz, nw, tc, wb"
    echo "  -path-output path of dir where out-of-domain training sets will be written"
}

if [[ $1 == "-h" || $1 == "--help" ]]; then
    print_usage
    exit 0
fi
if [ "$#" -ne 2 ]; then
    print_usage
    exit 1
fi

mkdir $2

train_dnames="bc bn mz nw tc wb"

for dn in $train_dnames; do
    path_train=$2/ontonotes.$dn.train.out-of-domain.iob
    echo "Making $path_train"
    for odn in $train_dnames; do
	if [ "$odn" != "$dn" ]; then
	    echo "  Adding $odn"
	    cat $1/ontonotes.$odn.train.iob >> $path_train
	    # Add an empty line just in case
	    echo "" >> $path_train
	fi
    done
    echo
done
