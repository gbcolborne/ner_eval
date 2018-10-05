import argparse, os, copy
from collections import defaultdict
from glob import glob

doc="""Given the path of the CoNLL-2012 version of OntoNotes, extract
words and NER labels for the *_gold_conll files, and make a 2-column
text file containing the tokens and labels (in BIO-2 format) for each
of the 5 domains in CoNLL and each of the 3 partitions.  Note: this
code borrows heavily from NER-with-LS/preprocess.py, by Abbas Ghaddar
(see https://github.com/ghaddarAbs/NER-with-LS)."""

def make_dataset(data_dir, partition_name, domain_name, output_path):
    """Given the path of the directory containing the CoNLL-2012 dataset
    (OntoNotes), a partition name (train, development or test) and
    domain name (nw, bn, bc, wb, tc, mz), extract annotated data for that
    partition and domain from the dataset, and write a 2-column text
    file containing the tokens and labels (in BIO-2 format).

    """
    if partition_name not in ["train", "development", "test"]:
        msg = 'Error: unrecognized partition name "{}"'.format(partition_name)
        raise ValueError(msg)
    if domain_name not in ["nw", "bn", "bc", "wb", "tc", "mz"]:
        msg = 'Error: unrecognized domain name "{}"'.format(domain_name)
        raise ValueError(msg)
    
    file_paths = []
    top = "{}/v4/data/{}".format(data_dir, partition_name)
    top += "/data/english/annotations/{}".format(domain_name)
    for root, dirs, files in os.walk(top):
        file_paths += glob(os.path.join(root, '*_gold_conll'))

    words = []
    tags = []

    for path in file_paths:        
        w, t = load_onto_file(path)
        words += w 
        tags += t

    output = [zip(x, y) for x, y in zip(words, tags)]
    st = '\n\n'.join(['\n'.join([' '.join(sub_lst) for sub_lst in lst]) for lst in output]) + "\n"

    with open(output_path, 'w') as f:
        f.write(st + "\n")

def load_onto_file(path):
    """Given the path of one of the *_gold_conll files in the CoNLL-2012
    dataset (OntoNotes), return words and NER tags.

    """
    with open(path) as f:
        sent_words = []
        sent_tags = []
        words = []
        tags = []
        for line in f:
            elems = line.strip().split()
            if len(elems):
                if elems[0] in ['#begin', '#end']:
                    continue
                words.append(replace_parentheses(elems[3]))
                tags.append(elems[10])
            elif len(words):
                tags = transform_onto_tags(tags)
                sent_words.append(copy.deepcopy(words))
                sent_tags.append(copy.deepcopy(tags))
                words = []
                tags = []
        if len(words):
            tags = transform_onto_tags(tags)
            sent_words.append(copy.deepcopy(words))
            sent_tags.append(copy.deepcopy(tags))
    return sent_words, sent_tags

def transform_onto_tags(lst):
    """Convert bracketed tokens of an OntoNotes file (CoNLL-2012 dataset)
    to a list of BIO-2 labels.

    """
    tags = ["O"] * len(lst)
    flag = False
    cur = "O"
    for i in range(len(lst)):
        if lst[i][0] == "(" and not flag:
            cur = lst[i].replace("(", "").replace(")", "").replace("*", "")
            tags[i] = "B-" + cur
            if lst[i][-1] != ")":
                flag = True

        elif flag and lst[i].startswith("*"):
            tags[i] = "I-" + cur
            if lst[i][-1] == ")":
                flag = False
    return tags

def replace_parentheses(word):
    word = word.replace('/.', '.')
    if not word.startswith('-'):
        return word

    if word == '-LRB-':
        return '('
    elif word == '-RRB-':
        return ')'
    elif word == '-LSB-':
        return '['
    elif word == '-RSB-':
        return ']'
    elif word == '-LCB-':
        return '{'
    elif word == '-RCB-':
        return '}'
    else:
        return word


parser = argparse.ArgumentParser(description=doc)
parser.add_argument("input_dir", help="path of CoNLL-2012 dataset")
parser.add_argument("output_dir", help="path where we will write the output files")
args = parser.parse_args()
if not os.path.exists(args.output_dir):
    os.mkdir(args.output_dir)

data_dir = os.path.abspath(args.input_dir)
for dom in ["bc", "bn", "nw", "mz", "tc", "wb"]:
    for part in ["train", "dev", "test"]:
        if part == "dev":
            part_alias = "development"
        else:
            part_alias = part
        output_path = "{}/ontonotes.{}.{}.iob".format(args.output_dir, dom, part)
        print("Making {}...".format(output_path))
        make_dataset(data_dir, part_alias, dom, output_path)

