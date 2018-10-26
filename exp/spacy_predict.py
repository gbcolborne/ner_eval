import sys, os, argparse
import spacy
from spacy.tokens import Doc

doc = """Given the path of a SpaCy NER model and the path of an NER
dataset (in whitespace-separated column text format with tokens in the
first column and empty lines between sentences), predict
labels. Output a file compatible with the conlleval script, containing
all the columns in the original dataset plus an extra column
containing the predicted labels in BIO-2 format."""

def add_predictions(nlp, sent):
    """ Given a SpaCy model (nlp) and a sentence (list of lines
    containing whitespace separated columns of text, with the token in
    the first column), predict NER labels and a column containing the
    predicted labels in BIO-2 format. """
    rows = []
    for line in sent:
        row = line.split()
        rows.append(row)
    words = [row[0] for row in rows]
    spaces = [True for word in words]
    doc = Doc(nlp.vocab, words=words, spaces=spaces)
    doc = nlp.get_pipe("ner")(doc)
    for (i,token) in enumerate(doc):
        if token.ent_iob_ == "O":
            label = "O"
        else:
            label = "{}-{}".format(token.ent_iob_, token.ent_type_)
        rows[i].append(label)
    return list(" ".join(row) for row in rows)

parser = argparse.ArgumentParser(description=doc)
parser.add_argument("model_dir", help="path of directory containing the model")
parser.add_argument("dataset", help="path of dataset")
parser.add_argument("output", help="path of output file")
parser.add_argument("-v", "--verbose", action="store_true")
args = parser.parse_args()
args.model_dir = os.path.abspath(args.model_dir)
args.dataset = os.path.abspath(args.dataset)
args.output = os.path.abspath(args.output)
if args.dataset == args.output:
    msg = "Dataset path and output path are the same."
    raise ValueError(msg)

# Load model
if args.verbose:
    print("Loading model from {}...".format(args.model_dir))
nlp = spacy.load(args.model_dir)

# Go through dataset, extract sentences, predict NER labels, and write to output
if args.verbose:
    print("Computing predictions on {}...".format(args.dataset))
with open(args.dataset) as f_in, open(args.output, 'w') as f_out:
    sent = []
    for line in f_in:
        line = line.strip()
        if len(line):
            sent.append(line)
        else:
            f_out.write("\n")
            if len(sent):
                # Compute predictions on sentence and add a column
                # containing the predicted labels
                output = add_predictions(nlp, sent)
                for line in output:
                    f_out.write(line + "\n")
                # Re-initialize sentence
                sent = []
    # In case there wasn't an empty line at the end, check if sent is empty
    if len(sent):
        output = add_predictions(nlp, sent)
        for line in output:
            f_out.write(line + "\n")

if args.verbose:
    print("Predictions written in {}...".format(args.output))
