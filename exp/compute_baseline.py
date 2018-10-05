import sys, argparse, os
dir_data_utils = os.path.dirname(os.path.realpath(__file__))+"/../data_utils"
sys.path.append(dir_data_utils)
from data_utils import get_mentions_from_BIO_file

doc = """ Compute naive baseline on an NER dataset using a simple dictionary
lookup based on the training data. Dataset should be a text file in
white-space separated columns with the token in the first column and
the label in the last column, and empty lines separating
sentences. Label encoding is presumed to be BIO-2. """

parser = argparse.ArgumentParser(description=doc)
parser.add_argument("-x", "--exclude_ambiguous", action="store_true",
                    help="Keep only non-ambiguous entity mentions.")
parser.add_argument("-v", "--verbose", action="store_true")
msg = ("Path of training set (text file in white-space separated "
       "columns with the token in the first column and the label "
       "in the last column, and empty lines separating sentences).")
parser.add_argument("train", help=msg)
parser.add_argument("test", help="Path of test set (same format as training set).")
msg = ("Path of output file (test set with extra column containing predictions.")
parser.add_argument("output", help=msg)
args = parser.parse_args()

# Get mentions from training set. BIO-2 label encoding consistency is
# required; another option would be to offer a "relaxed" mode, but I
# don't see a use case for this at the moment: the training data is
# supposed to be gold standard data, so the labeling should be
# consistent.
train_mentions = get_mentions_from_BIO_file(args.train, encoding="BIO-2", label_col=-1, ignore_boundaries=False, allow_prefix_errors=False, allow_type_errors=False)

# Extract mentions and entity types from the list of mentions
train_tuples = []
for (offset, tokens, labels) in train_mentions:
    train_tuples.append((" ".join(tokens), labels[0][2:]))
uniq_train_mentions = set(m for (m,t) in train_tuples)
if args.verbose:
    print("Nb training mentions: {}".format(len(train_tuples)))
    print("Nb uniq training mentions: {}".format(len(uniq_train_mentions)))

# Map (mention, entity type) tuples to their frequency
mention_type_freq_dist = {}
for (mention, etype) in train_tuples:
    if mention not in mention_type_freq_dist:
        mention_type_freq_dist[mention] = {}
    if etype not in mention_type_freq_dist[mention]:
        mention_type_freq_dist[mention][etype] = 0
    mention_type_freq_dist[mention][etype] += 1

# Map each mention to its most frequent entity type. Discard ambiguous
# mentions if the --exclude-ambiguous flag was used.
mention2etype = {}
nb_discarded = 0
for (mention, type_freq_dist) in mention_type_freq_dist.items():
    if args.exclude_ambiguous:
        if len(type_freq_dist) > 1:
            nb_discarded += 1
        else:
            mention2etype[mention] = list(type_freq_dist)[0]
    else:
        max_freq = 0
        most_freq_etype = None
        for (etype, freq) in type_freq_dist.items():
            if freq >= max_freq:
                max_freq = freq
                most_freq_etype = etype
        mention2etype[mention] = most_freq_etype
if args.exclude_ambiguous and args.verbose:
    print("Nb ambiguous mentions discarded: {}".format(nb_discarded))
    print("Nb non-ambiguous mentions kept: {}".format(len(mention2etype)))
max_mention_size = max(len(mention.split()) for mention in mention2etype.keys())
if args.verbose:
    print("Max mention size: {}".format(max_mention_size))


# Extract sentences from test set.
with open(args.test) as f:
    sents = []
    sent = []
    for line in f:
        stripped_line = line.strip()
        if len(stripped_line):
            sent.append(stripped_line)
        else:
            sents.append(sent[:])
            sent = []
    if len(sent):
        sents.append(sent[:])

# Predict mentions in test sentences
if args.verbose:
    print("Processing test set...")
with open(args.output, "w") as f:
    for sent in sents:
        # Extract tokens
        tokens = [line.split()[0] for line in sent]

        # Find all mentions
        mentions = []
        for mention_size in range(1,max_mention_size+1):
            for start in range(len(sent)-mention_size):
                candidate = " ".join(tokens[start:start+mention_size])
                if candidate in mention2etype:
                    mentions.append((start, mention_size, mention2etype[candidate]))

        # Eliminate overlap between mentions, keeping the longest mentions
        sorted_mentions = sorted(mentions, key=lambda x:x[1], reverse=True)
        marked_indices = set()
        mentions = []
        for (start, mention_size, etype) in sorted_mentions:
            overlap = False
            for index in range(start, start+mention_size):
                if index in marked_indices:
                    overlap = True
                    break
            if not overlap:
                mentions.append((start, mention_size, etype))
                for index in range(start, start+mention_size):
                    marked_indices.add(index)

        # Make labels
        labels = ["O" for _ in range(len(sent))]
        for (start, mention_size, etype) in mentions:
            labels[start] = "B-" + etype
            for index in range(start+1, start+mention_size):
                labels[index] = "I-" + etype
        
        # Write sentence with extra column containing predictions
        for index in range(len(sent)):
            line = sent[index]
            prediction = labels[index]
            elems = line.split()
            elems.append(prediction)
            f.write(" ".join(elems) + "\n")
        # Write empty line
        f.write("\n")
if args.verbose:
    print("Baseline predictions written -> {}\n".format(args.output))

    
    
