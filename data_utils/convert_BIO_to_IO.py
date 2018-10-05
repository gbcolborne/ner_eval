import sys, argparse

doc = """ Convert dataset from BIO (1 or 2) label encoding to IO
encoding. Input should be whitespace-separated columns with label in
last column. """

parser = argparse.ArgumentParser(description=doc)
parser.add_argument("input", help=("Path of input text file (whitespace-separated columns "
                                   "with label in last column)"))
parser.add_argument("output", help="Path of output file.")
args = parser.parse_args()

# Convert BIO to IO
with open(args.input) as f_in, open(args.output, "w") as f_out:
    for line in f_in:
        elems = line.strip().split()
        if len(elems):
            label = elems[-1]
            if label != "O":
                # Remove prefix ("B-" or "I-")
                elems[-1] = label[2:]
            f_out.write(" ".join(elems) + "\n")
        else:
            f_out.write("\n")

