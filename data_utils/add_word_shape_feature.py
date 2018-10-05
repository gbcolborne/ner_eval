import os, sys, argparse
from collections import defaultdict
dir_text_utils = os.path.dirname(os.path.realpath(__file__))+"/../text_utils"
sys.path.append(dir_text_utils)
from text_utils import get_word_shape

doc = """ Given an NER dataset (text file with whitespace-separated columns
containing one token per line), get shape of tokens and add in a new
column following the tokens """
            
parser = argparse.ArgumentParser(description=doc)
msg = ("Path of dataset (text file with 2 whitespace-separated columns "
       "containing the words and labels respectively)")
parser.add_argument("input", help=msg)
parser.add_argument("output", help="Path of output file")
parser.add_argument("-d", "--diagnostic", action="store_true",
                    help="Print some info on the extracted word shapes")
parser.add_argument("-t", "--token_col", type=int, default=0,
                    help="Index of column containing tokens")
msg = ("Max repeated symbols in the word shape "
       "(-1 to keep all repeated symbols)")
parser.add_argument("-m", "--max_repeats", type=int, default=-1, help=msg)
args = parser.parse_args()
if os.path.exists(args.output):
    msg = "Error: there is already something at {}".format(args.output)
    raise ValueError(msg)


with open(args.input) as f_in, open(args.output, "w") as f_out:
    # Map words to their shape. This serves as a cache (to reduce the
    # number of times we call get_word_shape), but also to check the
    # various shapes that extracted, for diagnostic purposes.
    word2shape = {} 
    for line in f_in:
        elems = line.strip().split()
        if len(elems):
            word = elems[args.token_col]
            if word in word2shape:
                shape = word2shape[word]
            else:
                shape = get_word_shape(word, normalize=True, max_repeats=args.max_repeats)
                word2shape[word] = shape
            elems.insert(args.token_col+1, shape)
            f_out.write(" ".join(elems) + "\n")
        else:
            f_out.write("\n")
    shape2freq = defaultdict(int)
    for (word, shape) in word2shape.items():
        shape2freq[shape] += 1

        
if args.diagnostic:
    print("\nUNIQUE SHAPES:")
    for shape in sorted(shape2freq.keys(), key=shape2freq.get, reverse=True):
        print("{} ({})".format(shape, shape2freq[shape]))
