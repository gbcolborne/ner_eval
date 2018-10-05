import sys, argparse

doc = """Given a text file containing word embeddings in GloVe's text
format (without a header), print number and dimension of embeddings,
as we would find in the first line of word2vec's text format.

"""



def get_glove_shape(path):
    """Given a text file containing word embeddings (without a
    header), return number and dimension of embeddings."""

    with open(path) as f:
        dim = len(f.readline().rstrip().split(" ")) - 1
        if dim == 2:
            msg = "File seems to contain a header"
            raise ValueError(msg)
        nb_vecs = 1 # We've already read one.
        nb_vecs += sum(1 for line in f if len(line.rstrip()))
    return nb_vecs, dim

parser = argparse.ArgumentParser(description=doc)
parser.add_argument("input", help="path of word embeddings in GloVe's text format (without header)")
args = parser.parse_args()

nb_vecs, dim = get_glove_shape(args.input)
sys.stdout.write("{} {}\n".format(nb_vecs, dim))
sys.stdout.flush()
