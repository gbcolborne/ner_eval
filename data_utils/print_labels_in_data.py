import sys, os, argparse

doc = """ Given the path of a file containing named entity annotations
    in column text format, with labels in the last column, get all
    unique labels present in the dataset, and print to stdout."""

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
sys.stdout.write("\n".join(sorted(labels)))

