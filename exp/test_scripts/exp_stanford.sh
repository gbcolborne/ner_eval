#! /usr/bin/env bash

# Evaluates Stanford NER. Writes results in a time-stamped
# subdirectory wherever this script is located.
system_name=stanford
dir_this=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
source $dir_this/exp.cfg
source $dir_ner_eval/exp/exp.lib.sh
checkConfig
mkdirScratch $system_name $dir_tmp
setTraps
mkdirResults
cd $dir_stanford_ner

# Train model using Stanford NER.
# Input:
# $1 - path of training data
# $2 - path where we write the model
# $3 - path of config template
# $4 - path where we write the config file
trainModel() {
    python $dir_ner_eval/exp/gen_config.py -r trainFile=$1,serializeTo=$2 $3 $4
    java -Xmx${max_mem_gb}g -cp stanford-ner.jar edu.stanford.nlp.ie.crf.CRFClassifier -prop $4
}

# Loop over test sets
for data_name in $test_dnames; do
    echo -e "\nRunning test on $data_name..."
    prepareData $data_name
    path_pred=$dir_results/$data_name.pred.txt

    # Train model. If training set is static (which can happen if we
    # are training on both in-domain and out-of-domain data, for
    # example -- see the checkConfig function for more details), then
    # we only need to train one model for all test sets, as Stanford
    # NER does not use a dev set for training.
    if [ $train_set_static -eq 0 ] || [ -z $path_model ] ; then
	echo "Training model on $path_train..."
	path_model=$scratch/model.crf.ser.gz
	path_config=$scratch/model.prop
	trainModel $path_train $path_model $path_stanford_config_template $path_config
    fi

    # Compute predictions
    echo "Computing predictions on $path_test..."
    java -Xmx${max_mem_gb}g -cp stanford-ner.jar edu.stanford.nlp.ie.crf.CRFClassifier -loadClassifier $path_model -testFile $path_test -map word=0,answer=1 > $path_pred

    # Evaluate predictions
    echo "Evaluating predictions..."
    path_res=$dir_results/$data_name.conlleval.txt
    path_err=$dir_results/$data_name.error-analysis.txt
    $dir_ner_eval/eval/conlleval -d "\t" < $path_pred > $path_res
    python $dir_ner_eval/eval/error_analysis.py -e BIO-2 $path_pred > $path_err
    echo "Test on $data_name completed."
done
	
echo -e "\nResults written in $dir_results"
