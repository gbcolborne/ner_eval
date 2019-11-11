#! /usr/bin/env bash

# Evaluates BERT. Writes results in a time-stamped subdirectory
# wherever this script is located.
system_name=bert
dir_this=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
source $dir_this/exp.cfg
source $dir_ner_eval/exp/exp.lib.sh
checkConfig
mkdirScratch $system_name $dir_tmp
setTraps
mkdirResults

bert_cfg_name="bert-base-uncased" 

# Fine-tune model using pre-trained BERT model. Save model at best epoch.
# Input:
# $1 - path of training set
# $2 - path of dev set
# $3 - path where we write the model directory (in which we include a file containing all the labels in the training set )
# $4 - path of cache directory containing downloaded pre-trained models
trainModel() {
    # Make temporary directories
    mkdir $scratch/data $scratch/output

    # Copy data (they need to be named train.txt and dev.txt)
    cp $1 ${scratch}/data/train.txt
    cp $2 ${scratch}/data/dev.txt

    # Get unique labels in training set
    python ${dir_ner_eval}/data_utils/print_labels_in_data.py $1 > ${scratch}/data/labels.txt

    # Prepare to train model  
    train_cmd="python ${dir_ner_eval}/exp/run_transformers_ner.py --data_dir ${scratch}/data --model_type bert --model_name_or_path $bert_cfg_name --output_dir ${scratch}/output --overwrite_output_dir --labels ${scratch}/data/labels.txt --cache_dir $4 --do_train --do_eval"
    # lower-case if model is uncased
    if [[ $bert_cfg_name =~ "uncased" ]]; then
        train_cmd="${train_cmd} --do_lower_case"
    fi

    # Train
    eval $train_cmd
    
    # Save best model, and include the file containing the labels.
    mv ${scratch}/output $3
    cp ${scratch}/data/labels.txt $3

    # Clean up
    rm -rf ${scratch}/data ${scratch}/output
}

# Test model.
# Input:
# $1 - path of model directory (must also contain a file called labels.txt, containing all the unique labels in the training set)
# $2 - path of test set
# $3 - path where we write the predictions
testModel() {
    mkdir $scratch/data $scratch/output

    # Copy data (they need to be named test.txt
    cp $2 ${scratch}/data/test.txt

    # Prepare command for evaluation
    test_cmd="python ${dir_ner_eval}/exp/run_transformers_ner.py --data_dir ${scratch}/data --model_type bert --model_name_or_path $1 --output_dir ${scratch}/output --overwrite_output_dir --labels $1/labels.txt --do_predict"
    # lower-case if model is uncased
    if [[ $bert_cfg_name =~ "uncased" ]]; then
        test_cmd="${test_cmd} --do_lower_case"
    fi
    eval test_cmd

    # Save predictions
    mv ${scratch}/output/test_predictions.txt $3

    # Clean up
    rm -rf ${scratch}/data ${scratch}/output
}


# Set cache directory for downloaded pre-trained models
dir_cache=${scratch}/cache_pretrained_models

# Loop over test sets
for data_name in $test_dnames; do
    echo
    echo "Running test on $data_name..."
    prepareData $data_name
    path_pred=$dir_results/$data_name.pred.txt

    # Train model. If both training set and dev set are static (which
    # can happen if we are training and validating on both in-domain
    # and out-of-domain data, for example -- see the checkConfig
    # function for more details), we only need to train one model for
    # all test sets.
    if [ $train_set_static -eq 0 ] || [ $dev_set_static -eq 0 ] || [ -z $path_model ] ; then
	echo "Training model on $path_train, using $path_dev for validation..."
	path_model=$scratch/model-$data_name
	trainModel $path_train $path_dev $path_model $dir_cache
    fi

    # Compute predictions
    echo "Computing predictions on $path_test..."
    testModel $path_model $path_test $path_pred

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
