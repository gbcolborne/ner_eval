import sys, argparse

doc = """ Convert dataset from IO label encoding to BIO (1 or 2)
encoding. Input should be whitespace-separated columns with label in
last column."""

parser = argparse.ArgumentParser(description=doc)
parser.add_argument("-e", "--encoding", choices=["BIO-1", "BIO-2"], default="BIO-2") 
parser.add_argument("input", help=("Path of input text file (whitespace-separated columns "
                                   "with label in last column)"))
parser.add_argument("output", help="Path of output file.")
args = parser.parse_args()

BIO2 = args.encoding == "BIO-2"

# Convert IO to BIO
with open(args.input) as f_in, open(args.output, "w") as f_out:
    inside = False # Was the previous token part of a mention?
    prev_label = None # What is the label of the previous token?
    for line in f_in:
        elems = line.strip().split()
        if len(elems):
            label = elems[-1]
            if label == "O":
                # Mark this token as not part of a mention
                inside = False
            else:
                # Strip I prefix
                if label[:2] == "I-":
                    label = label[2:]
                # Check if we are inside a mention
                if inside and label == prev_label:
                    # This token is within a mention, but is not the
                    # first token of that mention.
                    elems[-1] = "I-" + label
                else:
                    # Either the previous token was not part of a
                    # mention or the entity type of the previous token
                    # does not match that of this mention. In either
                    # case, this token is the first token of a
                    # mention.
                    if BIO2:
                        elems[-1] = "B-" + label
                    else:
                        # BIO-1
                        elems[-1] = "I-" + label
                # Label was not "O", so mark this token as part of a mention.
                inside=True
            f_out.write(" ".join(elems) + "\n")
            prev_label = label
        else:
            f_out.write("\n")
            # Assume entity mentions never cross sentence boundaries
            inside = False
            prev_label = None
