#! /usr/bin/env bash

# Installs Illinois NER
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

# Remember where we started
dir_this=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# Download Cogcomp-NLP
cd $1
wget https://github.com/CogComp/cogcomp-nlp/archive/4.0.9.tar.gz
tar -xvzf 4.0.9.tar.gz

# Clean up
rm 4.0.9.tar.gz

# Modify source of ner package to enable annotation in BIO format
echo "Modifying and compiling cogcomp-nlp-4.0.9/ner."
cd cogcomp-nlp-4.0.9/ner
cp $dir_this/illinois_mod_src/annotateBIO.sh scripts
cp $dir_this/illinois_mod_src/NETagBIO.java src/main/java/edu/illinois/cs/cogcomp/ner/LbjTagger
cp $dir_this/illinois_mod_src/NerTagger.java src/main/java/edu/illinois/cs/cogcomp/ner

# Compile NER package using Maven
mvn compile
mvn dependency:copy-dependencies
mvn -DskipTests=true -Dlicense.skip=true install

echo
echo "If all went well, cogcomp-nlp-4.0.9 has been installed in $1."
echo "To annotate in BIO format, use cogcomp-nlp-4.0.9/ner/scripts/annotateBIO.sh."
echo 
