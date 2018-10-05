import sys, os, argparse
from data_utils import get_mentions_from_BIO_file

doc = """ Print some info on an NER dataset in column text format
    (tokens in the first column, BIO-1 or BIO-2 labels in the last
    column, empty lines between sentences)."""

parser = argparse.ArgumentParser(description=doc)
parser.add_argument("-e", "--encoding", choices=["BIO-1", "BIO-2"], default="BIO-2")
msg = "In relaxed mode, label encoding is not required to be consistent"
parser.add_argument("-r", "--relax", action="store_true", help=msg)
parser.add_argument("input", help="path of input file")
args = parser.parse_args()
args.input=os.path.abspath(args.input)

# Get mentions
if args.relax:
    mentions = get_mentions_from_BIO_file(args.input, encoding=args.encoding, label_col=-1, ignore_boundaries=False, allow_prefix_errors=True, allow_type_errors=True)
else:
    try:
        mentions = get_mentions_from_BIO_file(args.input, encoding=args.encoding, label_col=-1, ignore_boundaries=False, allow_prefix_errors=False, allow_type_errors=False)
    except ValueError as err:
        msg = "\nERROR: ValueError caught while extracting mentions. "
        msg += "Fix errors in data or use relaxed mode.\n"
        print(msg)
        raise 

# Extract mentions and entity types from list of mentions
mentions = [(" ".join(tokens), labels[0][2:]) for (_,tokens,labels) in mentions]

# Get number of mentions and number of entity types
etypes = set()
for (mention, etype) in mentions:
    etypes.add(etype)

# Get number of sents
nb_sents = 0
with open(args.input) as f:
    sent = []
    for line in f:
        elems = line.strip().split()
        if len(elems):
            sent.append(elems[0])
        else:
            # We have an empty line
            if len(sent):
                if not len(sent) == 1 or not sent[0] == "-DOCSTART-":
                    nb_sents += 1
                sent = []
# If there is no empty line at the end of the file, we have not counted the last sentence.
if len(sent):
    nb_sents += 1

# Print stats
msg = "Stats on {} -> ".format(os.path.basename(args.input))
msg += "nb sents: {}; ".format(nb_sents)
msg += "nb mentions: {}; ".format(len(mentions))
msg += "nb entity types: {}".format(len(etypes))
sys.stdout.write(msg+"\n")
sys.stdout.flush()
