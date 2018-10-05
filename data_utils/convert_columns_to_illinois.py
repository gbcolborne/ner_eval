import argparse, sys


doc = """ Convert a NER dataset containing 2, 4 or 5 columns to the
9-column format used by Illinois NER. The 2-column format contains the
word and its NER label. The 4-column format contains the word, its POS
tag, its chunk label and its NER label. The 5-column format, which is
used by NeuroNER, contains the word, its document ID, its character
offsets and its NER label. The 9-column format, which is used by
Illinois NER, contains: the label, the sentence number (presumably),
the token number within the sentence (presumably), the chunk tag, the
POS tag, the token itself, and then 3 other fields which I have not
been able to identify so far."""

parser = argparse.ArgumentParser(description=doc)
parser.add_argument("input")
parser.add_argument("output")
args = parser.parse_args()

# Check if input contains 2, 4 or 5 columns
with open(args.input) as f:
    nb_cols = len(f.readline().strip().split())
    if nb_cols not in [2,4,5]:
        msg = "Expected 2, 4 or 5 columns, found {}".format(nb_cols)
        sys.exit(msg)
    
# Convert 
with open(args.input) as input_file, open(args.output, "w") as output_file:
    sent_ix = 0
    word_ix = 0
    line_count = 0
    for line in input_file:
        #sys.stdout.write("{}: {}\n".format(line_count, repr(line)))
        #sys.stdout.flush()
        line_count += 1
        elems = line.strip().split()
        if not len(elems):
            output_file.write("\n")
            if prev_word != "-DOCSTART-":
                sent_ix += 1
            word_ix = 0
            continue
        word = elems[0]
        # The 2-column format contains the word and its NER label. 
        if nb_cols == 2:
            label = elems[1]
            chunk = "?"
            pos = "?"
        # The 4-column format contains the word, its POS tag, its
        # chunk label and its NER label.
        elif nb_cols == 4:
            pos = elems[1]
            chunk = elems[2]
            label = elems[3]
        # The 5-column format, which is used by NeuroNER, contains the
        # word, its document ID, its character offsets and its NER
        # label.
        elif nb_cols == 5:
            label = elems[4]
            pos = "?"
            chunk = "?"
        # The 9-column format, which is used by Illinois NER,
        # contains: the label, the sentence number (I think), the
        # token number within the sentence (I think), the chunk tag,
        # the POS tag, the token itself, and then 3 other columns
        # which I have not been able to identify so far.
        output_file.write("{}\t{}\t{}\t{}\t{}\t{}\tx\tx\t0\n".format(label, sent_ix, word_ix, chunk, pos, word))
        if word != "-DOCSTART-":
            word_ix += 1
        prev_word = word

