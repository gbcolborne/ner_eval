import argparse 
import copy
import re

""" Preprocess conll-2003 dataset. Convert to 2-column format with IOB-2 labels. Code largely based on Abbas's code here: https://github.com/ghaddarAbs/NER-with-LS/blob/master/preprocess.py. """

def create_conll_iob2(path_in, path_out):
    """ Convert from 4-column format with IOB-1 labels to 2-column
    format with IOB-2 labels. This is a very lightly modified version
    of a function in Abbas's code here:
    https://github.com/ghaddarAbs/NER-with-LS/blob/master/preprocess.py. """
    sent_words = []
    tags_gold = []

    words = []
    tags = []

    with open(path_in) as data_file:
        for line in data_file:
            if line.strip():
                vals = line.strip().split(" ")
                if vals[0] != "-DOCSTART-":
                    words.append(vals[0])
                    tags.append(vals[-1])

            elif len(words) > 0:
                tags = iob1_to_iob2(tags)
                sent_words.append(copy.deepcopy(words))
                tags_gold.append(copy.deepcopy(tags))

                words = []
                tags = []

    output = [zip(x, y) for x, y in zip(sent_words, tags_gold)]
    st = '\n\n'.join(['\n'.join([' '.join(sub_lst) for sub_lst in lst]) for lst in output]) + "\n"

    with open(path_out, 'w') as f:
        f.write(st + "\n")


def iob1_to_iob2(tags):
    """ Convert from IOB-1 to IOB-2. This code was copied from Abbas's code here: https://github.com/ghaddarAbs/NER-with-LS/blob/master/preprocess.py. """
    prev = "O"
    for i in range(len(tags)):
        tag = re.sub(r'^B-|^I-', '',  tags[i])
        if tags[i].startswith("I-") and not prev.endswith("-"+tag):
            tags[i] = "B-"+tag
        prev = tags[i]

    return tags

def main():
    parser = argparse.ArgumentParser("Preprocess conll-2003 dataset. Convert to 2-column format with IOB-2 labels.")
    parser.add_argument("path_in", help="Path of conll-2003 dataset, a text file with 4 space-separate columns, with tokens in the first and IOB-1 labels in the last.")
    parser.add_argument("path_out")
    args = parser.parse_args()
    create_conll_iob2(args.path_in, args.path_out)


if __name__ == "__main__":
    main()
