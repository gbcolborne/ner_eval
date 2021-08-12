from __future__ import division, print_function, unicode_literals
import string, re, unicodedata

# Valid ASCII characters (not including whitespace)
VALID_CHARS = string.ascii_letters + string.digits + string.punctuation

def unicode_to_ASCII(s):
    """Convert a Unicode string to plain ASCII, based on
    http://stackoverflow.com/a/518232/2809427. 

    Note: characters that can not be converted to ASCII letters,
    digits or punctuation are removed (including whitespace), so the
    output string may be shorter than the input string.

    """
    norm = s
    
    # Normalize curly quotes
    norm = re.sub("’", "'", norm)
    norm = re.sub("[”“]", "\"", norm)

    # Map non-ASCII chars to ASCII base form, remove combining
    # characters, and remove any remaining unwanted characters
    # (characters that could not be converted to ASCII, whitespace,
    # etc.)
    norm = ''.join(
        c for c in unicodedata.normalize('NFD', norm)
        if unicodedata.category(c) != 'Mn'
        and c in VALID_CHARS
    )
    return norm        

def enforce_valid_bio2_labeling(labels):
    prev_prefix = 'O'
    prev_etype = None
    for label in labels:
        if label == 'O':
            etype = None
        else:
            etype = label[2:]
        prefix = label[0]
        if prefix == 'I':
            if prev_prefix == 'O':
                msg = 'Invalid BIO-2 labeling: I follows O'
                raise ValueError(msg)
            if etype != prev_etype:
                print(labels)
                msg = 'Invalid BIO-2 labeling: I follows label with different entity type'
                raise ValueError(msg)
        prev_prefix = prefix
        prev_etype = etype
                
def get_bio2_mention_offsets(labels):
    """Given a list of BIO-2 labels, find mention boundaries, yield a
    (start offset, end offset) tuple for each mention.

    """

    # Pad labels with an extra O at the end to avoid going out of
    # bounds when we look for the end offset of the mentons we find
    prefixes = [x[0] for x in labels]
    prefixes.append("O")
    i = 0
    while i < len(labels):
        prefix = prefixes[i]
        if prefix == "B":
            end = i
            while prefixes[end+1][0] == "I":
                end += 1
            yield (i, end)
            i = end + 1
        else:
            i += 1


def convert_bio2_to_bilou(labels):
    """Given a list of BIO-2 labels, return list of corresponding BILOU
    labels.

    """
    bilou_labels = ["O" for _ in range(len(labels))]
    for (beg, end) in get_bio2_mention_offsets(labels):
        etype = labels[beg][2:]
        length = 1  + end - beg 
        if length > 1:
            bilou_labels[beg] = "B-{}".format(etype)
            bilou_labels[end] = "L-{}".format(etype)
            for i in range(beg+1,end):
                bilou_labels[i] = "I-{}".format(etype)
        else:
            bilou_labels[beg] = "U-{}".format(etype)
    return bilou_labels


def compute_TER(pred, gold):
    """Given a list of predicted labels and a list of gold labels, compute
    token error rate (TER). Return TER and number of errors.

    """
    if len(pred) != len(gold):
        msg = "Error: length mismatch between tokens and gold labels"
        raise ValueError(msg)
    if len(pred) == 0:
        return 0, 0
    nb_errors = 0
    for (p, g) in zip(pred, gold):
        if p != g:
            nb_errors += 1
    token_error_rate = nb_errors / len(pred)
    return token_error_rate, nb_errors


def get_word_label_count_dict(tokens, labels):
    """Given a list of tokens and a list of labels, make a dict that maps
    words to a dict that maps labels to the frequency of the label
    given the word.

    """
    word_label_count = {}
    for word, label in zip(tokens, labels):
        if word not in word_label_count:
            word_label_count[word] = {}
        if label not in word_label_count[word]:
            word_label_count[word][label] = 0
        word_label_count[word][label] += 1
    return word_label_count


def get_diff_indices(word_label_count, test_tok, test_gold, strict=False):
    """Get indices of test tokens whose gold label was not seen in
    training (strict version) or was not the most frequent label in
    training (lax version), excluding tokens that were not seen at all
    in training.

    Args:
    - train_tok: list of train tokens
    - train_gold: list of train labels
    - test_tok: list of test tokens
    - test_gold: list of test labels
    - strict: use strict mode

    Returns:
    - list of indices 

    """
    max_label_count = {}
    for word, label_fd in word_label_count.items():
        max_label_count[word] = max(label_fd.values())
    keep = []
    for i,(word,label) in enumerate(zip(test_tok, test_gold)):
        if word in word_label_count:
            if label not in word_label_count[word]:
                keep.append(i)
            elif not strict and word_label_count[word][label] < max_label_count[word]:
                keep.append(i)
    return keep


def write_table(table, path, header=None, delim="\t"):
    """Given a table and an optional header (list of column names), write table. """
    with open(path, "w") as f:
        if header:
            f.write(delim.join(header)+"\n")
        for row in table:
            f.write(delim.join(row)+"\n")
