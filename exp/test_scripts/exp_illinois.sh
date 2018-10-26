#! /usr/bin/env bash

# Evaluates Illinois NER. Writes results in a time-stamped
# subdirectory wherever this script is located.
system_name=illinois
dir_this=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
source $dir_this/exp.cfg
source $dir_ner_eval/exp/exp.lib.sh
checkConfig
mkdirScratch $system_name $dir_tmp
setTraps
mkdirResults
cd $dir_illinois_ner


# Train model using Illinois NER
# Input:
# $1 - path where we write config file
# $2 - name of model
# $3 - path of training set
# $4 - path of dev set 
trainModel() {
    # Make directories where Illinois NER will find the data. It asks
    # for paths of directories, not files, and processes all the files
    # in those directories.
    mkdir $scratch/train $scratch/dev 

    # Write config
    touch $1
    echo "modelName = $2" >> $1
    etypes=$(python $dir_ner_eval/data_utils/print_entity_types_in_data.py $3)
    echo "labelTypes = $etypes" >> $1
    echo "pathToModelFile = $scratch" >> $1

    # Convert datasets to 9-column format expected by Illinois NER
    python $dir_ner_eval/data_utils/convert_columns_to_illinois.py $3 $scratch/train/train.iob
    python $dir_ner_eval/data_utils/convert_columns_to_illinois.py $4 $scratch/dev/dev.iob

    # Train model
    scripts/train.sh $scratch/train $scratch/dev $1

    # Clean up
    rm -rf $scratch/train $scratch/dev
}

# Compute predictions of model on test set
# Input:
# $1 - path of model's configuration file
# $2 - path of test set
# $3 - path where we write predictions
computePredictions() {
    # Make directories where Illinois NER will find the test set and
    # write the predictions. For each file in the test directory,
    # Illinois NER will write a file in the prediction directory.
    mkdir $scratch/test $scratch/pred

    # Convert test set to 9-column format expected by Illinois NER
    python $dir_ner_eval/data_utils/convert_columns_to_illinois.py $2 $scratch/test/test.iob
    
    # Compute predictions
    scripts/annotateBIO.sh $scratch/test $scratch/pred $1
    cp $scratch/pred/test.iob $3

    # Remove -DOCSTART- tokens from prediction file, as the
    # annotateBIO script only outputs the token in these cases, not
    # the gold label nor the predicted label, and this causes an error
    # when running conlleval on the predictions.
    python $dir_ner_eval/data_utils/remove_DOCSTART.py $3 $3.tmp
    mv $3.tmp $3

    # Clean up
    rm -rf $scratch/test $scratch/pred
}

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
    if [ $train_set_static -eq 0 ] || [ $dev_set_static -eq 0 ] || [ -z $path_config ] ; then
	echo "Training model on $path_train, using $path_dev for validation..."
	path_config=$scratch/$data_name.properties
	trainModel $path_config $data_name $path_train $path_dev
    fi 

    # Compute predictions
    echo "Computing predictions on $path_test..."
    computePredictions $path_config $path_test $path_pred

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
