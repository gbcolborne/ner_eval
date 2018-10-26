#! /usr/bin/env bash

# Evaluates NeuroNER. Writes results in a time-stamped subdirectory
# wherever this script is located.
system_name=neuroner
dir_this=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
source $dir_this/exp.cfg
source $dir_ner_eval/exp/exp.lib.sh
checkConfig
mkdirScratch $system_name $dir_tmp
setTraps
mkdirResults

# Train model using NeuroNER and save predictions and evaluation results.
# Input:
# $1 - path of train data
# $2 - path of dev data
# $3 - path of test data
# $4 - path where we will write predictions on test set
# $5 - path where we will write the JSON file in which NeuroNER stores its evaluation results
trainModel() {
    # Backup configuration file, whose relative path is hard-coded in
    # NeuroNER, and create custom configuration file.
    cd $dir_neuroner/src
    mv parameters.ini parameters.ini.bkp
    mods="dataset_text_folder=${scratch}/data"
    mods="${mods},output_folder=${scratch}/output"
    mods="${mods},token_pretrained_embedding_filepath=${path_embeddings}"
    mods="${mods},train_model=True"
    mods="${mods},use_pretrained_model=False"
    mods="${mods},main_evaluation_mode=conll"
    mods="${mods},number_of_gpus=0"
    mods="${mods},number_of_cpu_threads=8"
    mods="${mods},maximum_number_of_epochs=100"
    python $dir_ner_eval/exp/gen_config.py -r $mods parameters.ini.bkp parameters.ini

    # Copy data where NeuroNER can find it (the relative paths of the
    # data are hard-coded in NeuroNER)
    mkdir $scratch/data $scratch/output
    cp $1 $scratch/data/train.txt
    cp $2 $scratch/data/valid.txt
    cp $3 $scratch/data/test.txt

    # Train model. Since we are using the GPU-enabled version of
    # TensorFlow, we will tell NeuroNER not to use the GPU, as this is
    # actually slower (at least on my machine).
    CUDA_VISIBLE_DEVICES="" python main.py

    # Copy predictions on test set. First we have to find the name of
    # the sub-directory which NeuroNER has created in the output
    # directory we specified. Note: the glob pattern `*/` will match
    # all sub-directories, and `cd */` will move into the first result
    # if there are more than one (source:
    # https://stackoverflow.com/questions/28980380). Then we have to
    # find the path of the predictions made at the best epoch.
    cd $scratch/output
    cd */
    subdir_output=$(pwd)
    cp $(python $dir_ner_eval/exp/neuroner_get_predictions_path.py $subdir_output test) $4

    # Copy the JSON file containing the evaluation results
    tar -czf $5.tgz results.json

    # Restore original configuration file
    cd $dir_neuroner/src
    mv parameters.ini.bkp parameters.ini

    # Clean up
    rm -rf $scratch/data $scratch/output
}

# Loop over test sets
for data_name in $test_dnames; do
    echo
    echo "Running test on $data_name..."
    prepareData $data_name
    path_pred=$dir_results/$data_name.pred.txt

    # Train model and save predictions and evaluation results.
    echo "Training model on $path_train, using $path_dev for validation..."
    path_model=$scratch/model-$data_name
    trainModel $path_train $path_dev $path_test $path_pred $data_name.results.json

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

