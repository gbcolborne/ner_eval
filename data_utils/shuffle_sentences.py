import argparse, random


dsc = """ Shuffle the sentences in a NER dataset containg one token per line
and empty lines between sentences. Assumes tokens are in the first
column and columns are separated by whitespace. -DOCSTART- tokens are
simply deleted. """

parser = argparse.ArgumentParser(description=dsc)
parser.add_argument("input")
parser.add_argument("output")
args = parser.parse_args()

# Read sentences. Discard -DOCSTART- tokens.
with open(args.input) as input_file:
    sents = []
    current_sent = []
    for line in input_file:
        if not len(line.strip()):
            if len(current_sent):
                sents.append(current_sent[:])
                current_sent = []
        else:
            token = line.split()[0]
            if token != "-DOCSTART-":
                current_sent.append(line)
    # Append last sentence if there wasn't an empty line at the end of the file.
    if len(current_sent):
        sents.append(current_sent[:])

# Shuffle sentences
random.shuffle(sents)

# Write shuffled sentences
with open(args.output, "w") as output_file:
    for sent in sents:
        for line in sent:
            output_file.write(line)
        output_file.write("\n")
        
