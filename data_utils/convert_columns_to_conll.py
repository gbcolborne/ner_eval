import argparse, sys, os


doc = """ Convert a NER dataset containing 2, 5 or 9 columns to the
4-column CoNLL format expected by SpaCy's IOB converter, among other
things. This 4-column CoNLL format contains the word, its POS tag, its
chunk label and its NER label. The 2-column format contains the word
and its NER label. The 5-column format, which is used by NeuroNER,
contains the word, its document ID, its character offsets and its NER
label. The 9-column format, which is used by Illinois NER, contains:
the label, the sentence number (presumably), the token number within the
sentence (presumably), the chunk tag, the POS tag, the token itself, and
then 3 other fields which I have not been able to identify so far."""

parser = argparse.ArgumentParser(description=doc)
parser.add_argument("input")
parser.add_argument("output")
args = parser.parse_args()
args.input = os.path.abspath(args.input)
args.output = os.path.abspath(args.output)
if (args.input == args.output):
    msg = "Input and output paths are the same."
    raise ValueError(msg)

# Check if input contains 2, 5 or 9 columns
with open(args.input) as f:
    nb_cols = len(f.readline().strip().split())
    if nb_cols not in [2,5,9]:
        msg = "Expected 2, 5 or 9 columns, found {}".format(nb_cols)
        raise ValueError(msg)
    
# Convert 
with open(args.input) as input_file, open(args.output, "w") as output_file:
    for line in input_file:
        #sys.stdout.write("{}: {}\n".format(line_count, repr(line)))
        #sys.stdout.flush()
        elems = line.strip().split()
        if not len(elems):
            output_file.write("\n")
            continue
        # The 2-column format contains the word and its NER label. 
        if nb_cols == 2:
            word = elems[0]
            label = elems[1]
            chunk = "?"
            pos = "?"
        # The 5-column format, which is used by NeuroNER, contains the
        # word, its document ID, its character offsets and its NER
        # label.
        elif nb_cols == 5:
            word = elems[0]
            label = elems[4]
            chunk = "?"
            pos = "?"
        # The 9-column format, which is used by Illinois NER,
        # contains: the label, the sentence number (I think), the
        # token number within the sentence (I think), the chunk tag,
        # the POS tag, the token itself, and then 3 other columns
        # which I have not been able to identify so far.
        elif nb_cols == 9:
            word = elems[5]
            label = elems[0]
            chunk = elems[3]
            pos = elems[4]
        # The 4-column CoNLL format contains the word, its POS tag,
        # its chunk label and its NER label.
        output_file.write("{} {} {} {}\n".format(word, pos, chunk, label))

