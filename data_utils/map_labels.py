import os, argparse

doc = """ Given an NER dataset, map all of the label types (entity
types) to the 4 CoNLL-2003 entity types. Dataset should be a text file
in white-space separated columns with a token in the first column and
an label in the last column, and empty lines separating
sentences. Labels can be BIO-1 or BIO-2. The mapping of labels is
hard-coded."""

# Parse args
parser = argparse.ArgumentParser(description=doc)
msg = """Path of input dataset (text file in white-space separated
columns with the token in the first column and the label in the last
column, and empty lines separating sentences)."""
parser.add_argument("input", help=msg)
msg = """Path of output file. """
parser.add_argument("output", help=msg)
parser.add_argument("-v", "--verbose", action="store_true")
args = parser.parse_args()
args.input = os.path.abspath(args.input) 
args.output = os.path.abspath(args.output)
if args.input == args.output:
    raise ValueError("Output must be different from input.")

# Map input labels to output labels. Any input labels not in this map
# will be discarded. 
label_map = {"PER": "PER",
             "person": "PER",
             "PERSON": "PER",
             "DOCTOR": "PER",
             "PATIENT": "PER",
             "LOC": "LOC",
             "location": "LOC",
             "GPE": "LOC",
             "FAC": "LOC",
             "HOSPITAL": "LOC", 
             "CITY": "LOC",
             "STATE": "LOC",
             "COUNTRY": "LOC",
             "LOCATION_OTHER": "LOC",
             "ORG": "ORG",
             "corporation": "ORG",
             "group": "ORG",
             "ORGANIZATION": "ORG",
             "MISC": "MISC",
             "product": "MISC",
             "creative-work": "MISC",
             "PRODUCT": "MISC", 
             "NORP": "MISC",
             "EVENT": "MISC",
             "LANGUAGE": "MISC",
             "LAW": "MISC",
             "WORK_OF_ART": "MISC"}

# Transform labels using map, and write. Collect input labels that
# aren't found in the map.
unk_labels = set()
with open(args.input) as f_in, open(args.output, "w") as f_out:
    for line in f_in:
        elems = line.strip().split()
        if len(elems):
            label = elems[-1]
            if label != "O":
                iob_prefix = label[:2]
                etype = label[2:]
                if etype in label_map:
                    elems[-1] = iob_prefix + label_map[etype]
                else:
                    elems[-1] = "O"
                    unk_labels.add(etype)
            f_out.write(" ".join(elems))
        f_out.write("\n")

if args.verbose:
    print("Wrote {}.".format(args.output))
    if len(unk_labels):
        print("Labels discarded because not in map: {}".format(unk_labels))

