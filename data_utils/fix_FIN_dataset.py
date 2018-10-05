import sys, os, argparse

dsc = """ Fix labeling inconsistencies in FIN dataset. If a token labeled
'I' is not actually inside a mention, switch 'I' to 'B'. If the entity
type of a mention labeled 'I' does not match that of the previous
token, interact with user to fix annotations. Write corrected data if
any inconsistencies were found. """

def label_is_inside(label):
    if label and label[0] == "I":
        return True

def labels_are_consistent(labels):
    """ Check if mentions start with a 'B' and that the entity type is
    consistent within each mention. 

    """
    bio_prefixes = [label[0] for label in labels]
    etypes = [bio_label_to_etype(label) for label in labels]
    # Check if the BIO prefixes are consistent (i.e. an 'I' never follows an 'O')
    prev_prefix = bio_prefixes[0]
    for i in range(1, len(labels)):
        prefix = bio_prefixes[i]
        if prefix == "I" and prev_prefix == "O":
            return False
        prev_prefix = prefix
    # Check if the entity types are consistent (i.e. the same for all
    # labels associated with the same mention)
    prev_etype = None
    for i in range(len(labels)):
        etype = etypes[i]
        if bio_prefixes[i] == "I" and etype != prev_etype:
            return False
        prev_etype = etype
    return True

def bio_label_to_etype(label):
    if label == "O":
        return None
    else:
        return label[2:]

parser = argparse.ArgumentParser(description=dsc)
parser.add_argument("input", help="path of dataset")
args = parser.parse_args()
args.input = os.path.abspath(args.input)

# Load data
tokens = []
labels = []
with open(args.input) as f_in:
    rows = []
    for line in f_in:
        elems = line.strip().split()
        if len(elems):
            tokens.append(elems[0])
            labels.append(elems[-1])
        else:
            tokens.append(None)
            labels.append(None)

# Check mentions
source_was_OK = True
nb_lines = len(tokens)
line_ix = 0
while line_ix < nb_lines:
    label = labels[line_ix]
    if not label or label == "O":
        line_ix += 1
    else:
        # A mention starts at line_ix. Check how many tokens it
        # contains (i.e. how many tokens labeled "I" follow it).
        mention_size = 1
        while label_is_inside(labels[line_ix + mention_size]):
            mention_size += 1
        # Check if mention starts with an "I":
        if label == "I":
            print("\nMention at line {} starts with an 'I':".format(line_ix))
            for i in range(mention_size):
                print("    {} {} {}".format(line_ix+i, tokens[line_ix+i], labels[line_ix+i]))
            labels[line_ix] = "B-" + labels[line_ix][2:]
            print("First label switched to 'B'")
            source_was_OK = False
        # Check if all the entity types match
        while not labels_are_consistent(labels[line_ix:line_ix+mention_size]):
            print("\nMention at line {} has inconsistent entity types:".format(line_ix))
            for i in range(mention_size):
                print("    {} {} {}".format(line_ix+i, tokens[line_ix+i], labels[line_ix+i]))
            corr_ix = int(input("Select a line number to correct a label: "))
            corr_type = input("Type correct label: ")
            labels[corr_ix] = corr_type
            source_was_OK = False
        line_ix += mention_size            

if source_was_OK:
    print("\nNo inconsistencies found.\n")
else:
    # Write corrected mentions
    fn = args.input + ".fixed"
    with open(fn, "w") as f_out:
        for i in range(nb_lines):
            token = tokens[i]
            label = labels[i]
            if token is None:
                f_out.write("\n")
            else:
                f_out.write("{} {}\n".format(token, label))
    print("\nWrote corrected data --> {}\n".format(fn))
