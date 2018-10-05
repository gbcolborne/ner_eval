#! /usr/bin/env bash

# Evaluates CRF++. Writes results in a time-stamped subdirectory
# wherever this script is located.
system_name=crfpp
dir_this=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
source $dir_this/exp.cfg
source $dir_ner_eval/exp/exp.lib.sh
checkConfig
mkdirScratch $system_name $dir_tmp
setTraps
mkdirResults

# Loop over test sets
for data_name in $test_dnames; do
    echo
    echo "Running test on $data_name..."
    prepareData $data_name
    path_pred=$dir_results/$data_name.pred.txt

    # Train model. If training set is static (which can happen if we
    # are training on both in-domain and out-of-domain data, for
    # example -- see the checkConfig function for more details), then
    # we only need to train one model for all test sets, as CRF++ does
    # not use a dev set for training.
    if [ $train_set_static -eq 0 ] || [ -z $path_model ] ; then
	echo "Training model on $path_train..."
	path_model=$scratch/$data_name.model
	crf_learn $path_crfpp_templates $path_train $path_model
    fi

    # Compute predictions
    echo "Computing predictions on $path_test..."
    crf_test -m $path_model $path_test > $path_pred

    # Evaluate predictions
    echo "Evaluating predictions..."
    path_res=$dir_results/$data_name.conlleval.txt
    path_err=$dir_results/$data_name.error-analysis.txt
    $dir_ner_eval/eval/conlleval -d "\t" < $path_pred > $path_res
    python $dir_ner_eval/eval/error_analysis.py -e BIO-2 $path_pred > $path_err
    echo "Test on $data_name completed."
done

echo	
echo "Results written in $dir_results"
