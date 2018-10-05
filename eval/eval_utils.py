import numpy as np
from math import log

def get_column_from_file(path, col_ix, split_on_empty=False):
    """Given the path of a text file containing whitespace-separated
    columns, return values found in a given column (or None if line is
    empty).

    If split_on_empty is True, then split on empty lines and return a
    list of the sub-lists found between empty lines.

    """
    values = []
    with open(path) as f:
        for line in f:
            elems = line.strip().split()
            if len(elems):
                values.append(elems[col_ix])
            else:
                values.append(None)
    if split_on_empty:
        lst = []
        sub = []
        for v in values:
            if v is None:
                if len(sub):
                    lst.append(sub)
                    sub = []
            else:
                sub.append(v)
        return lst
    else:
        return values

    
def get_bio2_mention_offsets(labels):
    """ Given a list of BIO-2 labels, find mention boundaries, return
    start offsets and end offsets of the mentions. """
    offsets = []
    prefixes = [x[0] for x in labels]
    # Pad labels with an extra O at the end to avoid going out of
    # bounds when we look for the end offset of the mentons we find
    prefixes.append("O")
    i = 0
    while i < len(labels):
        prefix = prefixes[i]
        if prefix == "B":
            end = i
            while prefixes[end+1][0] == "I":
                end += 1
            offsets.append((i, end))
            i = end + 1
        else:
            i += 1
    return offsets


def get_bilou_mention_offsets(labels):
    """ Given a list of BILOU labels, find mention boundaries, return
    start offsets and end offsets of the mentions. """
    offsets = []
    prefixes = [x[0] for x in labels]
    # Pad labels with an extra O at the end to avoid going out of
    # bounds when we look for the end offset of the mentons we find
    prefixes.append("O")
    i = 0
    while i < len(labels):
        prefix = prefixes[i]
        if prefix == "U":
            offsets.append((i,i))
            i += 1
        elif prefix == "B":
            end = i
            while prefixes[end+1] == "I":
                end += 1
            # Next should be L
            end += 1
            if prefixes[end] != "L":
                msg = "Error: expected L at index {}".format(end)
                msg += " in {}".format(prefixes)
                raise ValueError(msg)
            offsets.append((i, end))
            i = end + 1
        else:
            i += 1
    return offsets


def convert_bio2_to_bilou(labels):
    """ Given a list of BIO-2 labels, return list of corresponding BILOU labels. """
    offsets = get_bio2_mention_offsets(labels)
    bilou_labels = ["O" for _ in range(len(labels))]
    for (beg, end) in offsets:
        etype = labels[beg][2:]
        length = 1  + end - beg 
        if length > 1:
            bilou_labels[beg] = "B-{}".format(etype)
            bilou_labels[end] = "L-{}".format(etype)
            for ins in range(beg+1,end):
                bilou_labels[ins] = "I-{}".format(etype)
        else:
            bilou_labels[beg] = "U-{}".format(etype)
    return bilou_labels
    
def get_entropy(counts, base=2):
    """ Compute Shannon's entropy on a list (or array) of class (or event) frequencies.  """
    nb_classes = len(counts)
    if nb_classes <= 1:
        return 0.
    probs = np.divide(counts, np.sum(counts))
    if np.count_nonzero(probs) <= 1:
        return 0.
    entropy = 0.
    for p in probs:
        if p > 0.0:
            entropy -= p * log(p, base)
    return entropy
