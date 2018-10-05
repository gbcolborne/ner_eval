#! /usr/bin/env bash

# Evaluates NER baseline. Writes results in a time-stamped
# subdirectory wherever this script is located.
system_name=baseline
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

    # Compute baseline predictions
    echo "Computing predictions on $path_test..."
    python $dir_ner_eval/exp/compute_baseline.py $path_train $path_test $path_pred

    # Evaluate predictions
    echo "Evaluating predictions..."
    path_res=$dir_results/$data_name.conlleval.txt
    path_err=$dir_results/$data_name.error-analysis.txt
    $dir_ner_eval/eval/conlleval < $path_pred > $path_res
    python $dir_ner_eval/eval/error_analysis.py -e BIO-2 $path_pred > $path_err
    echo "Test on $data_name completed."
done

echo	
echo "Results written in $dir_results"
