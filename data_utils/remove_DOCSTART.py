import os, argparse

doc = """ Given an NER dataset in text column format (one token per
line, empty lines between sentences, whitespace-separated columns,
tokens in the first, labels in the last), remove -DOCSTART-
tokens. 

"""

parser = argparse.ArgumentParser(description=doc)
parser.add_argument("input", help="path of input file")
parser.add_argument("output", help="path of output file")
args = parser.parse_args()
args.input = os.path.abspath(args.input)
args.output = os.path.abspath(args.output)
if os.path.exists(args.output):
    raise ValueError("Output path already exists")

with open(args.input) as input_file, open(args.output, "w") as output_file:
    for line in input_file:
        elems = line.strip().split()
        if len(elems):
            token = elems[0]
            if token != "-DOCSTART-":
                output_file.write(" ".join(elems)+"\n")
        else:
            output_file.write("\n")
