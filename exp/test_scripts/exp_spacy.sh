#! /usr/bin/env bash

# Evaluates SpaCy. Writes results in a time-stamped subdirectory
# wherever this script is located.
system_name=spacy
dir_this=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
source $dir_this/exp.cfg
source $dir_ner_eval/exp/exp.lib.sh
checkConfig
mkdirScratch $system_name $dir_tmp
setTraps
mkdirResults

# Train model using SpaCy. Save model at best epoch.
# Input:
# $1 - path of training set
# $2 - path of dev set
# $3 - path where we write the model
trainModel() {
    mkdir $scratch/data $scratch/model

    # Convert data to 4-column format, then to json files
    python $dir_ner_eval/data_utils/convert_columns_to_conll.py $1 $scratch/data/train.iob
    python $dir_ner_eval/data_utils/convert_columns_to_conll.py $2 $scratch/data/dev.iob
    python -m spacy convert -c ner $scratch/data/train.iob $scratch/data
    python -m spacy convert -c ner $scratch/data/dev.iob $scratch/data

    # Train model. Some hyper-parameters are specified via environment variables.
    train_cmd="batch_from=1 batch_to=16"
    train_cmd="$train_cmd python -m spacy train en $scratch/model "
    train_cmd="$train_cmd $scratch/data/train.iob.json $scratch/data/dev.iob.json"
    train_cmd="$train_cmd -v $path_spacy_embed_model -n 30 -P -T -G -g $spacy_gpu"
    eval $train_cmd

    # Get path of model at best epoch. 
    dir_best=$(python $dir_ner_eval/exp/spacy_get_best_model.py -m ents_f $scratch/model)

    # Change meta.json file so that we can load the model.
    mv $dir_best/meta.json $dir_best/meta.json.bkp
    mv $scratch/model/model-final/meta.json $dir_best/meta.json

    # Save best model
    mv $dir_best $path_model

    # Clean up
    rm -rf $scratch/data $scratch/model
}


# Loop over test sets
for data_name in $test_dnames; do
    echo -e "\nRunning test on $data_name..."
    prepareData $data_name
    path_pred=$dir_results/$data_name.pred.txt

    # Train model. If both training set and dev set are static (which
    # can happen if we are training and validating on both in-domain
    # and out-of-domain data, for example -- see the checkConfig
    # function for more details), we only need to train one model for
    # all test sets.
    if [ $train_set_static -eq 0 ] || [ $dev_set_static -eq 0 ] || [ -z $path_model ] ; then
	echo "Training model on $path_train, using $path_dev for validation..."
	path_model=$scratch/$model-$data_name
	trainModel $path_train $path_dev $path_model
    fi

    # Compute predictions
    echo "Computing predictions on $path_test..."
    python $dir_ner_eval/exp/spacy_predict.py $path_model $path_test $path_pred

    # Evaluate predictions
    echo "Evaluating predictions..."
    path_res=$dir_results/$data_name.conlleval.txt
    path_err=$dir_results/$data_name.error-analysis.txt
    $dir_ner_eval/eval/conlleval < $path_pred > $path_res
    python $dir_ner_eval/eval/error_analysis.py -e BIO-2 $path_pred > $path_err
    echo "Test on $data_name completed."
done
	
echo -e "\nResults written in $dir_results"
