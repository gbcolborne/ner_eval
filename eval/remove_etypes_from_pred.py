import argparse

doc = """ Given a file containing gold and predicted NER labels in BIO
format (or BILOU or any simlar format where the entity type is
appended to a character representing mention boundaries), remove
entity types from labels in order to evaluate entity mention detection
only. Input is a text file containing whitespace-separate columns,
with tokens in the first column, and gold and predicted labels in the
last 2 columns."""

parser = argparse.ArgumentParser(description=doc)
msg = ("text file containing whitespace-separate columns, with tokens "
       "in the first column, and gold and predicted labels in the last "
       "2 columns")
parser.add_argument("input", help=msg)
parser.add_argument("output", help="path of output file")
args = parser.parse_args()

with open(args.input) as f_in, open(args.output, "w") as f_out:
    for line in f_in:
        line = line.strip()
        elems = line.split()
        if len(elems):
            elems[-2] = elems[-2][0]
            elems[-1] = elems[-1][0]
            f_out.write(" ".join(elems)+"\n")
        else:
            f_out.write("\n")
