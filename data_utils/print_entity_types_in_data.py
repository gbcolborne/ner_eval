import sys, os, argparse

doc = """ Given the path of a file containing named entity annotations
    in column text format (tokens in the first column, BIO-1 or BIO-2
    labels in the last column), get entity types present in the
    dataset, and print to stdout."""

parser = argparse.ArgumentParser(description=doc)
parser.add_argument("input", help="path of dataset")
args = parser.parse_args()
args.input = os.path.abspath(args.input)

with open(args.input) as f:
    labels = set()
    for line in f:
        elems = line.strip().split()
        if len(elems):
            labels.add(elems[-1])
label_types = set([label[2:] for label in labels if label != "O"])
sys.stdout.write(" ".join(sorted(label_types)))

