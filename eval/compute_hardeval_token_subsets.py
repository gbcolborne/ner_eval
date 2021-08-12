#!/usr/bin/env python
import os, argparse
from collections import defaultdict
from utils_hardeval import enforce_valid_bio2_labeling, convert_bio2_to_bilou, get_word_label_count_dict, get_diff_indices, write_table

doc="""Given NER training data, and optionally a test file, compute the
various subsets of tokens used in HardEval. If no test file is
provided, we use 10-fold cross-validation over the training data.

WARNING: labels must be in BIO-2 format.
"""

def load_labeled_data(path):
    word_col_ix = 0
    label_col_ix = -1
    tokens = []
    labels = []
    with open(path) as f:
        for line in f:
            elems = line.strip().split()
            if len(elems):
                tokens.append(elems[word_col_ix])
                labels.append(elems[label_col_ix])
    if len(tokens) == 0:
        msg = "Error: 0 tokens read"
        raise ValueError(msg)                
    return (tokens, labels)


def compute_test_token_subsets(train_examples, test_examples, dir_output, strict=False):
    # Extract data, convert labels to BILOU
    train_tokens, train_labels = zip(*train_examples)
    test_tokens, test_labels = zip(*test_examples)
    enforce_valid_bio2_labeling(train_labels)
    enforce_valid_bio2_labeling(test_labels)
    train_vocab = set(train_tokens)
    test_vocab = set(test_tokens)
    train_labels_bilou = convert_bio2_to_bilou(train_labels)
    test_labels_bilou = convert_bio2_to_bilou(test_labels)
    
    # Map words to their BILOU labels    
    train_word_to_labels = defaultdict(list)
    for i in range(len(train_examples)):
        word = train_tokens[i]
        label = train_labels_bilou[i]
        train_word_to_labels[word].append(label)
    test_word_to_labels = defaultdict(list)
    for i in range(len(test_examples)):
        word = test_tokens[i]
        label = test_labels_bilou[i]
        test_word_to_labels[word].append(label)
    
    # Convert labels to IO
    train_labels_io = ["O" if y == "O" else "I" for y in train_labels_bilou]
    test_labels_io = ["O" if y == "O" else "I" for y in test_labels_bilou]

    # Compute unseen tokens
    nb_test_tokens = len(test_examples)    
    test_subsets = {}
    unseen = test_vocab.difference(train_vocab)
    keep_unseen = [i for i in range(nb_test_tokens) if test_tokens[i] in unseen]
    keep_unseen_I = []
    keep_unseen_O = []
    for i in keep_unseen:
        if test_labels_io[i] == "I":
            keep_unseen_I.append(i)
        else:
            keep_unseen_O.append(i)
    test_subsets["unseen-I"] = keep_unseen_I
    test_subsets["unseen-O"] = keep_unseen_O    

    # Compute diff-I and diff-O tokens, i.e. O tokens that were
    # usually or exclusively I in training, and vice-versa
    word_io_count = get_word_label_count_dict(train_tokens, train_labels_io)
    test_indices_I = []
    test_indices_O = []
    for i,label in enumerate(test_labels_io):
        if label == "I":
            test_indices_I.append(i)
        else:
            test_indices_O.append(i)
    test_tokens_I = [test_tokens[i] for i in test_indices_I]
    test_labels_I = ["I" for _ in test_indices_I]
    indices = get_diff_indices(word_io_count, test_tokens_I, test_labels_I, strict=strict)
    test_subsets["diff-I"] = [test_indices_I[i] for i in indices]
    test_tokens_O = [test_tokens[i] for i in test_indices_O]
    test_labels_O = ["O" for _ in test_indices_O]
    indices = get_diff_indices(word_io_count, test_tokens_O, test_labels_O, strict=strict)
    test_subsets["diff-O"] = [test_indices_O[i] for i in indices]

    # Write IO prefix frequencies in training set for seen test words
    # (excluding "O")
    keys = ["I", "O"]
    io_info = []
    for word in test_vocab.intersection(train_vocab):
        io_fd = {}
        if word in word_io_count:
            io_fd = word_io_count[word]
        io_info.append([word] + [str(io_fd[k]) if k in io_fd else "0" for k in keys])
    io_info = sorted(io_info, key=lambda x:x[0])
    path = "{}/class_freqs_for_seen_words_IO.tsv".format(dir_output)
    header = ["Word"] + keys
    write_table(io_info, path, header=header, delim="\t")

    # I-X tokens that were usually I, but whose entity type was usually
    # (or exclusively) not X.
    train_indices_I = []
    for i,label in enumerate(train_labels_io):
        if label == "I":
            train_indices_I.append(i)
    train_tokens_I = [train_tokens[i] for i in train_indices_I]
    train_etypes_I = [train_labels_bilou[i][2:] for i in train_indices_I]
    word_etype_count = get_word_label_count_dict(train_tokens_I, train_etypes_I)
    usually_I = set()
    for word, io_fd in word_io_count.items():
        i_count = 0
        o_count = 0
        if "I" in io_fd:
            i_count = io_fd["I"]
        if "O" in io_fd:
            o_count = io_fd["O"]
        if i_count >= o_count:
            usually_I.add(word)
    test_indices_UI = [i for i in test_indices_I if test_tokens[i] in usually_I]
    test_tokens_UI = [test_tokens[i] for i in test_indices_UI]
    test_etypes_UI = [test_labels_bilou[i][2:] for i in test_indices_UI]
    indices = get_diff_indices(word_etype_count, test_tokens_UI, test_etypes_UI, strict=strict)
    test_subsets["diff-etype"] = [test_indices_UI[i] for i in indices]
    
    # Write entity type frequencies in training set for seen test
    # words (excluding "O")
    keys = list(set(train_etypes_I))
    etype_info = []
    for word in test_vocab.intersection(word_etype_count.keys()):
        etype_fd = word_etype_count[word]
        etype_info.append([word] + [str(etype_fd[k]) if k in etype_fd else "0" for k in keys])
    etype_info = sorted(etype_info, key=lambda x:x[0])
    path = "{}/class_freqs_for_seen_words_etype.tsv".format(dir_output)
    header = ["Word"] + keys
    write_table(etype_info, path, header=header, delim="\t")

    # Write token subsets
    header = ["Line", "Token", "Label"]
    for k in test_subsets:
        data = [[str(i), test_tokens[i], test_labels[i]] for i in test_subsets[k]]
        path = os.path.join(dir_output, 'tokens_%s.tsv' % k)
        write_table(data, path, header=header, delim="\t")
    return 


def main():
    format_warning = "Must be contain whitespace-separated columns with labels in BIO-2 format in the last column."
    parser = argparse.ArgumentParser(description=doc)
    parser.add_argument("-s", "--strict",
                        action="store_true",
                        help=("Use strict mode to detect tokens with surprising labels "
                              "(include tokens whose labels was never observed in training only)"))
    parser.add_argument("--path_train",
                        type=str,
                        help="Path of labeled train file (required). " + format_warning)    
    parser.add_argument("--path_test",
                        type=str,
                        help="Path of labeled test file (optional). " + format_warning)
    parser.add_argument("--dir_output",
                        type=str,
                        help="Path of output directory (required).")    
    args = parser.parse_args()

    assert args.path_train is not None
    assert args.dir_output is not None    
    if os.path.exists(args.dir_output):
        raise ValueError("%s already exists" % args.dir_output)
    os.makedirs(args.dir_output)

    print("\nReading training data from {}...".format(os.path.abspath(args.path_train)))
    train_tokens, train_labels = load_labeled_data(args.path_train)
    train_examples = list(zip(train_tokens, train_labels))
    print("Nb tokens in training set: {}".format(len(train_examples)))    

    # Do same for test file
    if args.path_test is not None:
        print("\nReading test data from {}...".format(os.path.abspath(args.path_test)))
        test_tokens, test_labels = load_labeled_data(args.path_test)
        test_examples = list(zip(test_tokens, test_labels))
        print("Nb tokens in test set: {}".format(len(test_examples)))        

    # Compute token subsets in test set
    compute_test_token_subsets(train_examples, test_examples, args.dir_output, args.strict)

    
if __name__ == "__main__":
    main()
