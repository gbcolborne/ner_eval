import sys, argparse

doc = """ Remove columns from a text file containing
whitespace-separated columns. Write result to standard output. 

"""

parser = argparse.ArgumentParser(description=doc)
parser.add_argument("input", help="Path of text file containing whitespace-separated columns")
parser.add_argument("columns", help="Comma separated list of indices (zero-indexed) of columns to remove.")
args = parser.parse_args()

# Determine number of columns (ignoring empty lines)
nb_cols_set = set()
with open(args.input) as f:
    for line in f:
        elems = line.strip().split()
        if len(elems):
            nb_cols_set.add(len(elems))
            
# If nb columns is inconsistent, take max
if len(nb_cols_set) == 1:
    nb_cols = list(nb_cols_set)[0]
else:
    nb_cols = max(nb_cols_set)
    msg = "WARNING: Nb cols is inconsistent ({}). Taking max ({}).\n".format(repr(list(nb_cols_set)), nb_cols)
    sys.stderr.write(msg)
    sys.stderr.flush()

# Get indices of columns that we keep
remove = set([int(i) for i in args.columns.split(",")])
keep = [i for i in range(nb_cols) if i not in remove]

# Remove columns and write result to stdout.
lines = open(args.input).readlines()
for line in lines:
    elems = line.strip().split()
    if len(elems):
        out_elems = []
        for ix in keep:
            if ix < len(elems):
                out_elems.append(elems[ix])
        sys.stdout.write(" ".join(out_elems) + "\n")
        sys.stdout.flush()            
    else:
        sys.stdout.write("\n")
        sys.stdout.flush()
