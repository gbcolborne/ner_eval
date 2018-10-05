import sys, os, argparse

dsc = """ Make the FIN dataset harder by changing the annotations of
"borrower" and "lender" so that they are not considered named
entities. Assumes the token is in the first column, the label is in the
last, and columns are separated by one or more whitespace.  """

parser = argparse.ArgumentParser(description=dsc)
parser.add_argument("input", help="path of dataset")
parser.add_argument("output", help="path of output file")
args = parser.parse_args()

with open(args.input) as f_in, open(args.output, "w") as f_out:
    for line in f_in:
        elems = line.strip().split()
        if len(elems):
            token = elems[0]
            label = elems[-1]
            # Change label of "borrower" and "lender", all occurrences
            # of which have been labeled PER according to Salinas
            # Alvarado et al. (2015)
            if token.lower() in ["borrower", "lender"]:
                if label[-3:] == "PER":
                    # Change label to 'O'
                    elems[-1] = "O"
                else:
                    msg = "WARNING: ignoring an occurrence of '{}'".format(token)
                    msg += " because its type is not PER"
                    pring(msg)
            f_out.write(" ".join(elems) + "\n")
        else:
            f_out.write("\n")
