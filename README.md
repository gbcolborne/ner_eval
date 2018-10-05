# ner_eval

Some code to install and test various named entity recognition (NER) systems on different datasets, allowing for both in-domain and out-of-domain evaluation, using standard evaluation metrics and automatic error analysis.

Installation and testing scripts are provided for the following systems:

* [CRF++](http://taku910.github.io/crfpp/) (version 0.58)
* [Stanford NER](https://nlp.stanford.edu/software/CRF-NER.shtml) (version 3.9.1)
* [Illinois NER](https://github.com/CogComp/cogcomp-nlp), i.e. the NER package in CogComp-NLP (version 4.0.9)
* [NeuroNER](http://neuroner.com/) 
* [SpaCy](https://spacy.io/)
* The baseline used for the CoNLL-2003 shared task (see [paper](https://www.aclweb.org/anthology/W03-0419.pdf)).

The systems may be trained and tuned on in-domain data, out-of-domain data or both. See `exp/exp.cfg` for details.


## Requirements


* Python 3 (some scripts aren't compatible with Python 2 at the moment, and `NeuroNER` requires Python 3)
* [numpy](http://www.numpy.org/)
* [matplotlib](https://matplotlib.org/) if you want to use `eval/plot_scores.py`
* Bash
* Perl (for `conlleval` evaluation script)
* Maven to compile `Illinois NER`

## Usage

To install and test one or more NER systems, do the following:

1. Obtain and prepare datasets. Datasets must be text files containing 2 whitespace-separated columns, with tokens in the first and labels in the second, and with empty lines between sentences. Labels should be encoded using [BIO-2](https://en.wikipedia.org/wiki/Inside%E2%80%93outside%E2%80%93beginning_(tagging)) format.  Dataset names must match a specific pattern, as explained in `exp/exp.cfg`. The directory `data_utils` contains various scripts used to preprocess, analyze, and transform datasets.

2. Install systems you would like to evaluate. You might want to review the installation scripts first. Note: if you install `NeuroNER`, make sure your default Python interpreter uses Python 3 (you can use a virtual environment if you don't want to change your system's default interpreter). 

```bash
chmod a+x install/install*
install/install_crfpp.sh install-directory
install/install_stanford_ner.sh install-directory
install/install_illinois_ner.sh install-directory
install/install_neuroner.sh install-directory
install/install_spacy.sh
```

3. If using `Stanford NER`, prepare the configuration file you will use to train the model. You can use one of the configuration files used to train the models provided with `Stanford NER`, which are located in the sub-directory `classifiers` (e.g. `english.conll.4class.distsim.prop`). The values of `trainFile` and `serializeTo` can be left blank, as they will be replaced automatically during the tests. Also, if you want to use distributional features, you will need to obtain some distributional clusters and provide their path in the configuration file -- see Christopher Manning's answer [here](https://stackoverflow.com/a/17765107) for details, and note that [Alex Clark's code](https://github.com/ninjin/clark_pos_induction) can be used to create distributional clusters. Otherwise, set `useDistSim = false`.

4. If using `SpaCy` or `NeuroNer`, get pre-trained [GloVe](https://nlp.stanford.edu/projects/glove/) word embeddings. You can use any other pre-trained word embeddings, but they must be in a text file. `SpaCy` expects that file to have a header as in word2vec's text format, whereas `NeuroNER` expects no header (as in GloVe's text format).

```bash
chmod a+x install/get_glove_embeddings.sh
install/get_glove_embeddings.sh download-directory
```

5. If using `SpaCy`, the text file containing the pre-trained word embeddings must have a header as in word2vec's text format, so if it does not (as in GloVe's format), you must add a header. You can use the script `exp/get_glove_shape.py` to get this header. The following 2 lines will copy the embeddings in `path-output` and add that header.

```bash
python exp/print_glove_shape.py path-embeddings > path-output
cat path-embeddings >> path-output
```

6. If using `SpaCy`, initialize a model containing the pre-trained word embeddings. Note: the parameter `nb-vectors-kept` specifies the number of unique embeddings that the vocabulary is pruned to (-1 for no pruning) -- see [SpaCy's doc](https://spacy.io/api/cli#init-model). 

```bash
chmod a+x exp/spacy_init_model.sh
exp/spacy_init_model.sh language path-embeddings nb-vectors-kept path-model
```

7. Test baseline system and `conlleval` evaluation script.

```bash
python exp/compute_baseline.py path-training-file path-test-file path-output
chmod a+x eval/conlleval
eval/conlleval < path-output
```

8. Review the configuration file `exp/test_scripts/exp.cfg`.

9. Run the tests for a given system.

```bash
cd exp/test_scripts
chmod a+x exp_*.sh
./exp_baseline.sh
```

The predictions of the system on each test set and the evaluation results will be written in a time-stamped sub-directory. These include the results of the `conlleval` evaluation script, as well as the output of the script `eval/error_analysis.py`. You can also evaluate the predictions using `eval/hard_eval.py`.

You can copy the `test_scripts` directory elsewhere, modify the configuration file, and run the tests there if you want, e.g. if you want to create different directories for different experimental configurations (e.g. whether you train in-domain or out-of-domain).
