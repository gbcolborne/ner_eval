import os, sys, argparse
sys.path.append(os.path.dirname(__file__)+"/..")
from data_utils import get_mentions_from_BIO_file, count_tokens_and_sents

doc = """Count and analyze entity mentions in an NER dataset in column
text format (tokens in the first column, BIO-2 labels in the last
column, empty lines between sentences).

"""

# Args
parser = argparse.ArgumentParser(description=doc)
parser.add_argument('path')
parser.add_argument('-i', '--ignore_boundaries', action="store_true", help="Ignore sentence boundaries")
args = parser.parse_args()
path = os.path.abspath(args.path)

# Count tokens and sentences
nb_tokens, nb_sents = count_tokens_and_sents(args.path)
print("Nb sentences: {}".format(nb_sents))
print("Nb tokens: {}".format(nb_tokens))

# Get entity mentions
mentions = get_mentions_from_BIO_file(path, encoding="BIO-2", label_col=-1, 
                                      ignore_boundaries=args.ignore_boundaries,
                                      allow_prefix_errors=False, 
                                      allow_type_errors=False)

# Map entity types to frequencies and to set of mentions. Map unique
# mentions to frequency and to set of types. Map (mention, type)
# tuples to freq.
type_to_mentions = {}
type_to_freq = {}
mention_to_types = {}
mention_to_freq = {}
tuple_to_freq = {}
for (line, tokens, labels) in mentions:
    mention = " ".join(tokens)
    type_ = labels[0][2:]
    if type_ not in type_to_mentions:
        type_to_mentions[type_] = set()
    type_to_mentions[type_].add(mention)
    if type_ not in type_to_freq:
        type_to_freq[type_] = 0
    type_to_freq[type_] += 1
    if mention not in mention_to_types:
        mention_to_types[mention] = set()
    mention_to_types[mention].add(type_)
    if mention not in mention_to_freq:
        mention_to_freq[mention] = 0
    mention_to_freq[mention] += 1
    if (mention, type_) not in tuple_to_freq:
        tuple_to_freq[(mention, type_)] = 0
    tuple_to_freq[(mention, type_)] += 1

# Print nb mentions
nb_mentions = sum(mention_to_freq.values())
nb_uniq_mentions = len(mention_to_freq)
print("Nb mentions: {}".format(nb_mentions))
print("Nb unique mentions: {}".format(nb_uniq_mentions))

# Print entity types
types = type_to_freq.keys()
print("Nb entity types: " + str(len(types)))
print("Entity types: " + ", ".join(sorted(types)))

# Print type frequency distribution
print("Entity type frequency distribution:")
sorted_types = sorted(types, key=type_to_freq.get, reverse=True)
for t in sorted_types:
    freq = type_to_freq[t]
    pct = 100. * freq / nb_mentions
    print("- {}: {} ({:.1f}%)".format(t, freq, pct))

# Print most frequent mentions by type
max_shown = 10
for t in sorted_types:
    print("\nMost frequent {} mentions:".format(t))
    mentions = type_to_mentions[t]
    sorted_mentions = sorted(mentions, key=lambda m:tuple_to_freq[(m,t)], reverse=True)
    nb_shown = min(max_shown, len(mentions))
    for i in range(nb_shown):
        m = sorted_mentions[i]
        msg = "- {} ({} as {}, {} total)".format(m, tuple_to_freq[(m,t)], t, mention_to_freq[m])
        print(msg)
    if len(mentions) > max_shown:
        print("- ... ({} more)".format(len(mentions)-max_shown))
        
# Check what percentage of mentions are ambiguous (i.e. they have been
# labeled with more than 1 entity type in the dataset)
ambig = [k for (k,v) in mention_to_types.items() if len(v) > 1]
nb_ambig = sum(mention_to_freq[m] for m in ambig)
pct_ambig = nb_ambig * 100. / nb_mentions
nb_ambig_uniq = len(ambig)
pct_ambig_uniq = nb_ambig_uniq * 100. / nb_uniq_mentions
print("\n% ambiguous mentions: {:.1f}% ({}/{})".format(pct_ambig, nb_ambig, nb_mentions))
print("% ambiguous unique mentions: {:.1f}% ({}/{})".format(pct_ambig_uniq, nb_ambig_uniq, nb_uniq_mentions))
print("Ambiguous mentions:")
ambig = sorted(ambig)
max_shown = 10
nb_shown = min(nb_ambig_uniq, max_shown)
for i in range(nb_shown):
    mention = ambig[i]
    print("- {}: {}".format(mention, mention_to_types[mention]))
if nb_ambig_uniq > max_shown:
    print("- ... ({} more)".format(nb_ambig_uniq-max_shown))
