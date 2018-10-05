import argparse, random

doc = """ Given an NER dataset in column text format (tokens in the
    first column, IO or BIO labels in the last column, empty lines between
    sentences), remove sentences that do not contain any entity
    mentions. -DOCSTART- tokens are deleted. """

def contains_mention(sent):
    for line in sent:
        elems = line.strip().split()
        label = elems[-1]
        if label != "O":
            return True
    return False

def write_sent(sent, file_):
    for line in sent:
        file_.write(line)
    # Add empty line between this sentence and the next
    output_file.write("\n")

parser = argparse.ArgumentParser(description=doc)
parser.add_argument("input")
parser.add_argument("output")
parser.add_argument("-v", "--verbose", action="store_true")
args = parser.parse_args()

# Read sentences. Discard sentences that do not contain any entity
# mentions, as well as -DOCSTART- tokens.
with open(args.input) as input_file, open(args.output, "w") as output_file:
    nb_kept = 0
    nb_discarded = 0
    current_sent = []
    for line in input_file:
        if len(line.strip()):
            current_sent.append(line)
        else:
            if len(current_sent):
                if contains_mention(current_sent):
                    write_sent(current_sent, output_file)
                    nb_kept += 1
                else:
                    nb_discarded += 1
                current_sent = []
            
    # Append last sentence if there wasn't an empty line at the end of the file.
    if len(current_sent):
        if contains_mention(current_sent):
            write_sent(current_sent, output_file)
            nb_kept += 1
        else:
            nb_discarded += 1
if args.verbose:
    print("Nb sentences kept: {}".format(nb_kept))
    print("Nb sentences discarded: {}".format(nb_discarded))
        
