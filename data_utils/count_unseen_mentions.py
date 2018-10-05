import os, sys, argparse
from collections import defaultdict
from data_utils import get_mentions_from_BIO_file

doc="""Check overlap of entity mentions between two NER datasets in
    column text format (tokens in the first column, BIO-2 labels in
    the last column, empty lines between sentences).

"""

# Args
parser = argparse.ArgumentParser(description=doc)
parser.add_argument('train', help="path of training set")
parser.add_argument('test', help="path of test set")
args = parser.parse_args()
train_path = os.path.abspath(args.train)
test_path = os.path.abspath(args.test)

# Extract (mention, type) tuples
mentions_train = get_mentions_from_BIO_file(train_path)
mentions_test = get_mentions_from_BIO_file(test_path)
tuples_train = []
tuples_test = []
for (line, tokens, labels) in mentions_train:
    mention = " ".join(tokens)
    etype = labels[0][2:]
    tuples_train.append((mention, etype))
for (line, tokens, labels) in mentions_test:
    mention = " ".join(tokens)
    etype = labels[0][2:]
    tuples_test.append((mention, etype))

# Map test tuples to frequency
tuple2freq = defaultdict(int)
for t in tuples_test:
    tuple2freq[t] += 1

# Split test tuples into seen and unseen subsets
tuple_set_train = set(tuples_train)
tuple2freq_seen = {}
tuple2freq_unseen = {}
for (t,f) in tuple2freq.items():
    if t in tuple_set_train:
        tuple2freq_seen[t] = f
    else:
        tuple2freq_unseen[t] = f
    
# Map test mentions to frequency
mention2freq = defaultdict(int)
for (t,f) in tuple2freq.items():
    m = t[0]
    mention2freq[m] += f

# Split test mentions into seen and unseen subsets
mention_set_train = set([m for (m,c) in tuple_set_train])
mention2freq_seen = {}
mention2freq_unseen = {}
for (m,f) in mention2freq.items():
    if m in mention_set_train:
        mention2freq_seen[m] = f
    else:
        mention2freq_unseen[m] = f
        
# Print seen and unseen tuples and mentions
max_shown = 20 # Max examples shown (sorted by frequency)
width = 40 # Width of first column
for (key_type, freq_dist) in zip(["Seen tuples", "Unseen tuples", "Seen mentions", "Unseen mentions"],
                                 [tuple2freq_seen, tuple2freq_unseen, mention2freq_seen, mention2freq_unseen]):
    print("\n\n\n" + "="*(width+16))
    print("{0: <{width}}{1}".format(key_type, "Freq in test set", width=width))
    print("="*(width+16))
    for key in sorted(freq_dist.keys(), key=freq_dist.get, reverse=True)[:max_shown]:
        print("{0: <{width}}{1}".format(str(key), freq_dist[key], width=width))
    if len(freq_dist) > max_shown:
        print("... ({} more)".format(len(freq_dist)-max_shown))
    print("="*(width+16))
    left_field = "ALL {} {}".format(len(freq_dist), key_type.upper())
    print("{0: <{width}}{1}".format(left_field, sum(freq_dist.values()), width=width))
    print("="*(width+16))    


# Print summary
nb_mentions = sum(mention2freq.values())
nb_unseen_mentions = sum(mention2freq_unseen.values())
pct_unseen_mentions = 100. * nb_unseen_mentions / nb_mentions
nb_mentions_uniq = len(mention2freq)
nb_unseen_mentions_uniq = len(mention2freq_unseen)
pct_unseen_mentions_uniq = 100. * nb_unseen_mentions_uniq / nb_mentions_uniq
nb_tuples = sum(tuple2freq.values())
nb_unseen_tuples = sum(tuple2freq_unseen.values())
pct_unseen_tuples = 100. * nb_unseen_tuples / nb_tuples
nb_tuples_uniq = len(tuple2freq)
nb_unseen_tuples_uniq = len(tuple2freq_unseen)
pct_unseen_tuples_uniq = 100. * nb_unseen_tuples_uniq / nb_tuples_uniq

print("\n\n=======\nSUMMARY\n=======")
print("Ratio of unseen mentions: {:.1f}% ({}/{})".format(pct_unseen_mentions, nb_unseen_mentions, nb_mentions))
print("Ratio of unseen unique mentions: {:.1f}% ({}/{})".format(pct_unseen_mentions_uniq, nb_unseen_mentions_uniq, nb_mentions_uniq))
print("Ratio of unseen tuples: {:.1f}% ({}/{})".format(pct_unseen_tuples, nb_unseen_tuples, nb_tuples))
print("Ratio of unseen unique tuples: {:.1f}% ({}/{})".format(pct_unseen_tuples_uniq, nb_unseen_tuples_uniq, nb_tuples_uniq))
print("=======\n")

