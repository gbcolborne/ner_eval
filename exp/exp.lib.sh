# Validate config for experiment. Also, set variables train_set_static
# and dev_set_static that indicate whether the training and dev sets
# will change from one test set to the next, or if they remain static.
checkConfig() {
    for var_name in train_in train_out dev_in dev_out map down dir_data dir_ner_eval test_dnames train_dnames; do
	var_val=${!var_name}
	if [ -z "$var_val" ]; then
	    echo "Error: $var_name is null"; exit 1
	fi
    done
    if [ $train_in -eq 0 ] && [ $train_out -eq 0 ]; then
	echo 'Error: at least one of $train_in or $train_out must be set to 1'; exit 1
    fi
    if [ $dev_in -eq 0 ] && [ $dev_out -eq 0 ]; then
	echo 'Error: at least one of $train_in or $train_out must be set to 1'; exit 1
    fi
    if [ $train_out -eq 1 ]; then
	for dn in $train_dnames; do
	    if [ ! -f $dir_data/$dn.train.iob ]; then
		echo "Error: $dn.train.iob not found in $dir_data"; exit 1
	    fi
	done
    fi
    if [ $dev_out -eq 1 ]; then
	for dn in $train_dnames; do
	    if [ ! -f $dir_data/$dn.dev.iob ]; then
		echo "Error: $dn.dev.iob not found in $dir_data"; exit 1
	    fi
	done
    fi
    if [ $train_in -eq 1 ]; then
	for dn in $test_dnames; do
	    if [ ! -f $dir_data/$dn.train.iob ]; then
		echo "Error: $dn.train.iob not found in $dir_data"; exit 1
	    fi
	done
    fi
    if [ $dev_in -eq 1 ]; then
	for dn in $test_dnames; do
	    if [ ! -f $dir_data/$dn.dev.iob ]; then
		echo "Error: $dn.dev.iob not found in $dir_data"; exit 1
	    fi
	done
    fi
    # Set a variable which indicates whether the training set will
    # change from one test set to the next.
    if [ $train_out -eq 0 ]; then 
	# We are training in-domain, so the training set depends on
	# the test set
	train_set_static=0
    elif [ $train_in -eq 0 ]; then
	# We are training out-of-domain only. If none of the test set
	# names are in the list of training set names, then the
	# out-of-domain training set will be the same for all test
	# sets.
	train_set_static=1
	for dn in $test_dnames; do
	    dn_in_train=0
	    for odn in $train_dnames; do
		if [ "$dn" == "$odn" ]; then 
		    dn_in_train=1
		    break
		fi
	    done
	    if [ $dn_in_train -eq 1 ]; then
		train_set_static=0
		break
	    fi
	done
    else
	# We are training both in-domain and out-of-domain. If all of
	# the test set names are in the list of training set names,
	# then the in-and-out training set will be the same for all
	# test sets.
	train_set_static=1
	for dn in $test_dnames; do
	    dn_in_train=0
	    for odn in $train_dnames; do
		if [ "$dn" == "$odn" ]; then 
		    dn_in_train=1
		    break
		fi
	    done
	    if [ $dn_in_train -eq 0 ]; then
		train_set_static=0
		break
	    fi
	done
    fi
    # Set a variable which indicates whether the dev set will change
    # from one test set to the next, like we just did for the training
    # set.
    if [ $dev_out -eq 0 ]; then 
	dev_set_static=0
    elif [ $dev_in -eq 0 ]; then
	dev_set_static=1
	for dn in $test_dnames; do
	    dn_in_train=0
	    for odn in $train_dnames; do
		if [ "$dn" == "$odn" ]; then 
		    dn_in_train=1
		    break
		fi
	    done
	    if [ $dn_in_train -eq 1 ]; then
		dev_set_static=0
		break
	    fi
	done
    else
	dev_set_static=1
	for dn in $test_dnames; do
	    dn_in_train=0
	    for odn in $train_dnames; do
		if [ "$dn" == "$odn" ]; then 
		    dn_in_train=1
		    break
		fi
	    done
	    if [ $dn_in_train -eq 0 ]; then
		dev_set_static=0
		break
	    fi
	done
    fi
}
    
# Given the path of a training set, optionally apply transformations
# (i.e. mapping entity types, down-sampling negative examples), and
# shuffle sentences.
transformTrainingSet() {
    python $dir_ner_eval/data_utils/print_stats_on_data.py $1
    if [ $down -eq 1 ]; then
	echo "Down-sampling negative examples in $1..."
	python $dir_ner_eval/data_utils/downsample_neg.py $1 $1.tmp
	mv $1.tmp $1
    fi
    if [ $map -eq 1 ]; then
	echo "Mapping labels in $1..."
        python $dir_ner_eval/data_utils/map_labels.py $1 $1.tmp
        mv $1.tmp $1
    fi
    if [ $down -eq 1 ] || [ $map -eq 1 ]; then 
	python $dir_ner_eval/data_utils/print_stats_on_data.py $1
    fi
    echo "Shuffling training data..."
    python $dir_ner_eval/data_utils/shuffle_sentences.py $1 $1.tmp
    mv $1.tmp $1
}

# Given the name of a dataset, prepare training data (either
# in-domain, out-of-domain or in-and-out), and optionally apply
# transformations (i.e. mapping entity types and down-sampling
# negative examples), and shuffle sentences. Set $path_train as the
# path of the resulting training data, which will be in the temporary
# directory.
prepareTrainingSet() {
    if [ $train_out -eq 0 ]; then 
	echo "Preparing in-domain training set..."
        path_train=$scratch/$1.in-domain.train.iob
    elif [ $train_in -eq 0 ]; then
	echo "Preparing out-of-domain training set..."
	path_train=$scratch/$1.out-of-domain.train.iob
    else
	echo "Preparing in-and-out training set..."
	path_train=$scratch/$1.in-and-out.train.iob
    fi
    touch $path_train
    nb_added=1
    if [ $train_in -eq 1 ]; then 
	echo "  Adding $1"	
	cat $dir_data/$1.train.iob >> $path_train
	nb_added=$((nb_added+1))
    fi
    if [ $train_out -eq 1 ]; then 
	for odn in $train_dnames; do
	    if [ "$odn" != $1 ]; then
		echo "  Adding $odn"
		cat $dir_data/$odn.train.iob >> $path_train
		nb_added=$((nb_added+1))
		# Add an empty line just in case
		echo "" >> $path_train
	    fi
	done
    fi
    if [ $nb_added -eq 0 ]; then
	echo "WARNING: training set is empty. This can happen if train_dnames contains only one name which is also in test_dnames, and we are training on out-of-domain data only."
    fi
    transformTrainingSet $path_train
}

# Given the name of a dataset, prepare validation data (either
# in-domain, out-of-domain or in-and-out), and optionally apply
# transformation (mapping entity types). Set $path_dev as the path of
# the resulting dev set, which will be in the temporary directory.
prepareDevSet() {
    if [ $dev_out -eq 0 ]; then 
	echo "Preparing in-domain dev set..."
        path_dev=$scratch/$1.in-domain.dev.iob
    elif [ $dev_in -eq 0 ]; then
	echo "Preparing out-of-domain dev set..."
	path_dev=$scratch/$1.out-of-domain.dev.iob
    else
	echo "Preparing in-and-out dev set..."
	path_dev=$scratch/$1.in-and-out.dev.iob
    fi
    touch $path_dev
    nb_added=1
    if [ $dev_in -eq 1 ]; then 
	echo "  Adding $1"	
	cat $dir_data/$1.dev.iob >> $path_dev
	nb_added=$((nb_added+1))
    fi
    if [ $dev_out -eq 1 ]; then 
	for odn in $train_dnames; do
	    if [ "$odn" != $1 ]; then
		echo "  Adding $odn"
		cat $dir_data/$odn.dev.iob >> $path_dev
		nb_added=$((nb_added+1))
	    fi
	done
    fi
    if [ $nb_added -eq 0 ]; then
	echo "WARNING: dev set is empty. This can happen if train_dnames contains only one name which is also in test_dnames, and we are validating on out-of-domain data only."
    fi
    transformTestSet $path_dev
}

# Given the path of a dev or test set, optionally apply tranformation
# (i.e. mapping entity types). Modify data in place.
transformTestSet() {
    python $dir_ner_eval/data_utils/print_stats_on_data.py $1
    if [ $map -eq 1 ]; then
	echo "Mapping types in $1..."
        python $dir_ner_eval/data_utils/map_labels.py "$1" "$1.tmp"
        mv "$1.tmp" "$1"
	python $dir_ner_eval/data_utils/print_stats_on_data.py $1
    fi
}

# Given the name of a dataset, copy the corresponding test set from
# $dir_data to the temporary directory $scratch and optionally apply
# transformation (mapping entity types). Set $path_test as the path of
# the resulting test data, which will be located in $scratch.
prepareTestSet() {
    path_test=$scratch/$1.test.iob
    cp $dir_data/$1.test.iob $path_test
    transformTestSet $path_test
}

# Given the name of a dataset, prepare training, dev, and test
# sets. Set $path_train, $path_dev, and $path_test, which will be
# located in the temporary directory $scratch.
prepareData() {
    prepareTrainingSet $1
    prepareDevSet $1
    prepareTestSet $1
}

# Make temporary directory $scratch.
# Input:
# $1 - system name
# $2 - path of directory in which we create $scratch
mkdirScratch() {
    scratch=$(mktemp -d -p $2 -t "NER-exp-$1-XXXXXXXXXX")
}

# Set traps for execution. 
setTraps() {
    trap "reportErrAndExit" ERR
    trap "exit 1" SIGINT SIGTERM
    trap "rm -rf $scratch" EXIT
}

# Report error and exit
reportErrAndExit() {
    echo "Error on line $(caller)" >&2
    exit 1
}

# Make directory $dir_results to store results of an experiment. 
mkdirResults() {
    timestamp=$(date +%Y%m%d_%H%M%S)
    dir_results=$dir_this/Results-$system_name-$timestamp
    mkdir $dir_results
}

