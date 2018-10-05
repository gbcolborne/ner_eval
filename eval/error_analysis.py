import sys, os, argparse
dir_data_utils = os.path.dirname(os.path.realpath(__file__))+"/../data_utils"
sys.path.append(dir_data_utils)
from data_utils import get_mentions_from_BIO_file

doc = """ Analyze errors made by a NER system and write analysis to
stdout. Input is a text file containing whitespace-separate columns,
with tokens in the first column, and gold and predicted labels in the
last 2 columns, and empty lines between sentences. Label encoding can
be BIO-1 or BIO-2."""

parser = argparse.ArgumentParser(description=doc)
msg = """Path of input text file (containing whitespace-separate columns, 
with tokens in the first column, and gold and predicted labels in 
the last 2 columns). Label encoding can be BIO-1 or BIO-2."""
parser.add_argument("input", help=msg)
parser.add_argument("-e", "--encoding", choices=["BIO-1", "BIO-2"], default="BIO-2")
args = parser.parse_args()

# Load data. We allow labeling inconsistencies in the predicted
# mentions, but not in the gold mentions.
gold_mentions = get_mentions_from_BIO_file(args.input, encoding=args.encoding, label_col=-2, ignore_boundaries=False, allow_prefix_errors=False, allow_type_errors=False)
sys.stdout.write("Nb gold mentions: {}\n".format(len(gold_mentions)))
pred_mentions = get_mentions_from_BIO_file(args.input, encoding=args.encoding, label_col=-1, ignore_boundaries=False, allow_prefix_errors=True, allow_type_errors=True)
sys.stdout.write("Nb pred mentions: {}\n".format(len(pred_mentions)))


# Remove predicted mentions whose initial label is invalid: if
# encoding is BIO-1, a mention can only start with a B if it
# immediately follows another mention; if encoding is BIO-2, a mention
# must start with a B. Predicted mentions that break these rules are
# considered invalid. They will not considered false positives, nor
# partial matches, and we won't check if their type is correct -- they
# are simply considered invalid mentions.
if args.encoding == "BIO-1":
    # Store end offset of all mentions (in case the mentions are not
    # sorted in the order in which they appear in the dataset for some
    # reason).
    end_offsets = set()
    for (offset, tokens, labels) in pred_mentions:
        end_offsets.add(offset + len(tokens) - 1)

    # Look for mentions that start with a B but do not immediately
    # follow another mention.
    tmp = []
    prefix_errors = []
    for (offset, tokens, labels) in pred_mentions:
        if labels[0][0] == "B" and offset-1 not in end_offsets:
            prefix_errors.append((offset, tokens, labels))
        else:
            tmp.append((offset, tokens, labels))
    pred_mentions = tmp
elif args.encoding == "BIO-2":
    # Look for mentions that don't start with a B
    tmp = []
    prefix_errors = []
    for (offset, tokens, labels) in pred_mentions:
        if labels[0][0] != "B":
            prefix_errors.append((offset, tokens, labels))
        else:
            tmp.append((offset, tokens, labels))
    pred_mentions = tmp

# Process gold mentions : join tokens, replace labels with a unique
# entity type
for i in range(len(gold_mentions)):
    (offset, tokens, labels) = gold_mentions[i]
    mention = " ".join(tokens)
    etype = labels[0][2:]
    gold_mentions[i] = (offset, mention, etype)

# Process predicted mentions: join tokens, replace labels with a
# unique entity type. If types are inconsistent, leave list of types
# instead of a unique type. Given the way the function
# get_mentions_from_BIO_file works, this should only happen if the
# encoding is BIO-2 -- see function documentation.
for i in range(len(pred_mentions)):
    (offset, tokens, labels) = pred_mentions[i]
    mention = " ".join(tokens)
    etypes = [label[2:] for label in labels]
    if len(set(etypes)) == 1:
        pred_mentions[i] = (offset, mention, etypes[0])
    else:
        if args.encoding == "BIO-1":
            msg = "Inconsistent types should only happen if encoding is BIO-2. Check code."
            raise ValueError(msg)
        pred_mentions[i] = (offset, mention, etypes)

# Map offsets of predicted mentions to index in list of predicted mentions
offset_to_pred_mention_ix = {}
for i in range(len(pred_mentions)):
    (offset, mention, etype) = pred_mentions[i]
    mention_size = len(mention.split())
    for j in range(mention_size):
        offset_to_pred_mention_ix[offset+j] = i

# Do same with gold mentions
offset_to_gold_mention_ix = {}
for i in range(len(gold_mentions)):
    (offset, mention, etype) = gold_mentions[i]
    mention_size = len(mention.split())
    for j in range(mention_size):
        offset_to_gold_mention_ix[offset+j] = i

# Go through gold mentions and look for the following:
# - true positives (correct span and type)
# - misclassifications (correct span but incorrect type)
# - partial matches (partially overlapping spans)
# - false negatives (no predicted mention in span)
true_positives = []
misclassifications = []
partial_matches = []
false_negatives = []
for gold_ix in range(len(gold_mentions)):
    (offset, mention, etype) = gold_mentions[gold_ix]
    mention_size = len(mention.split())
    hits = set()
    for i in range(mention_size):
        if offset+i in offset_to_pred_mention_ix:
            hits.add(offset_to_pred_mention_ix[offset+i])
    if len(hits) == 0:
        # We have a false negative
        false_negatives.append(gold_ix)
    elif len(hits) > 1:
        # We have multiple partial matches (multiple predicted
        # mentions whose span partially overlap that of this gold
        # mention).
        for pred_ix in hits:
            partial_matches.append((gold_ix, pred_ix))
    else:
        # We have one match, either partial or exact
        pred_ix = list(hits)[0]
        pred_offset, pred_mention, pred_etype = pred_mentions[pred_ix]
        pred_mention_size = len(pred_mention.split())
        if pred_offset == offset and pred_mention_size == mention_size:
            # We have an exact match. Check type.
            if etype == pred_etype:
                true_positives.append((gold_ix, pred_ix))
            else:
                misclassifications.append((gold_ix, pred_ix))                    
        else:
            # We have a partial match
            partial_matches.append((gold_ix, pred_ix))

# Count partially matching predicted mentions and partially matched
# gold mentions (these numbers can be different).
nb_partial_gold = len(set(g for g,p in partial_matches))
nb_partial_pred = len(set(p for g,p in partial_matches))

# Now go through predicted mentions and look for: 
# - false positives (no gold mention in span of a predicted mention)
# - type inconsistencies (more than one entity type within a predicted
# mention). Given the way the function get_mentions_from_BIO_file
# works, this should only happen if the encoding is BIO-2 -- see
# function documentation. If the encoding is BIO-1, we already
# enforced that there are no type inconsistencies above. Note that if
# we find type inconsistencies, some of them may have already been
# identified as misclassifications (if their span matched that of a
# gold mention), but we want to show all the cases where a predicted
# mention has inconsistent entity types.
false_positives = []
type_inconsistencies = []
for pred_ix in range(len(pred_mentions)):
    (offset, mention, etype) = pred_mentions[pred_ix]
    if type(etype) == list:
        # We have a type inconsistency
        type_inconsistencies.append(pred_ix)
    mention_size = len(mention.split())
    match_found = False
    for i in range(mention_size):
        if offset+i in offset_to_gold_mention_ix:
            match_found = True
            break
    if not match_found:
        # We have a false positive
        false_positives.append(pred_ix)

# Check if the numbers add up
nb_gold_mentions = len(gold_mentions)
nb_gold_classified = len(true_positives) + len(misclassifications)
nb_gold_classified += nb_partial_gold + len(false_negatives)
if nb_gold_mentions != nb_gold_classified:
    msg = "ERROR: numbers do not add up. Check the code."
    raise ValueError(msg)
nb_pred_mentions = len(pred_mentions)
# Add the invalid predicted mentions
nb_pred_mentions += len(prefix_errors)
nb_pred_classified = len(prefix_errors) + len(true_positives) + len(misclassifications)
nb_pred_classified += nb_partial_pred + len(false_positives)
if nb_pred_mentions != nb_pred_classified:
    msg = "ERROR: numbers do not add up. Check the code."
    raise ValueError(msg)
        

################### Print all errors ##########################

m = "INVALID PREDICTED MENTIONS (mentions with invalid initial prefix):"
sys.stdout.write("\n" + m + "\n")
if len(prefix_errors):
    for (offset, tokens, labels) in prefix_errors:
        sys.stdout.write("Line {}: '{}' --> {}\n".format(offset, " ".join(tokens), labels))
else:
    sys.stdout.write("[NONE]\n")

m = "FALSE POSITIVES (predicted mentions that do not overlap a gold mention):"
sys.stdout.write("\n" + m + "\n")
if len(false_positives):
    for ix in false_positives:
        offset, mention, etype = pred_mentions[ix]
        sys.stdout.write("Line {}: '{}' ({})\n".format(offset, mention, etype))
else:
    sys.stdout.write("[NONE]\n")

m = "FALSE NEGATIVES (gold mentions that do not overlap a predicted mention):"    
sys.stdout.write("\n" + m + "\n")
if len(false_negatives):
    for ix in false_negatives:
        offset, mention, etype = gold_mentions[ix]
        sys.stdout.write("Line {}: '{}' ({})\n".format(offset, mention, etype))
else:
    sys.stdout.write("[NONE]\n")

m = "PARTIAL MATCHES (partial overlap between gold and predicted mentions):"
sys.stdout.write("\n" + m + "\n")
if len(partial_matches):
    for (gold_ix, pred_ix) in partial_matches:
        gold_offset, gold_mention, gold_etype = gold_mentions[gold_ix]
        pred_offset, pred_mention, pred_etype = pred_mentions[pred_ix]
        msg = "Line {}: ".format(gold_offset)
        msg += "Gold mention '{}' ({}) --> ".format(gold_mention, gold_etype)
        msg += "'{}' ({})".format(pred_mention, pred_etype)
        sys.stdout.write(msg+ "\n")
else:
    sys.stdout.write("[NONE]\n")
   
m = "MISCLASSIFICATIONS (correct span, but incorrect type):"
sys.stdout.write("\n" + m + "\n")
if len(misclassifications):
    for (gold_ix, pred_ix) in misclassifications:
        gold_offset, gold_mention, gold_etype = gold_mentions[gold_ix]
        pred_offset, pred_mention, pred_etype = pred_mentions[pred_ix]
        # Check if misclassification is due to inconsistent entity
        # types in the predicted mention
        if type(pred_etype) == list:
            msg = "Line {}: ".format(pred_offset)
            msg += "Predicted mention '{}' ".format(pred_mention)
            msg += "has correct span, but inconsistent types {}".format(pred_etype)
        else:
            msg = "Line {}: ".format(gold_offset)
            msg += "Gold mention '{}' is a {} ".format(gold_mention, gold_etype)
            msg += "not a {}".format(pred_etype)
        sys.stdout.write(msg+"\n")
else:
    sys.stdout.write("[NONE]\n")

if args.encoding == "BIO-2":
    m = "TYPE INCONSISTENCIES (predicted mentions with inconsistent "
    m += "entity types, ignoring span):"
    sys.stdout.write("\n" + m + "\n")
    if len(type_inconsistencies):
        for (pred_ix) in type_inconsistencies:
            pred_offset, pred_mention, pred_etype = pred_mentions[pred_ix]
            msg = "Line {}: ".format(pred_offset)
            msg += "Predicted mention '{}' has types {}".format(pred_mention, pred_etype)
            sys.stdout.write(msg+"\n")
    else:
        sys.stdout.write("[NONE]\n")

    
################# Print summary of errors ######################

sys.stdout.write("\n------------------\n-----SUMMARY------\n------------------\n")
sys.stdout.write("Gold mentions\n")
sys.stdout.write("------------------\n")
width = len(str(nb_gold_mentions))
sys.stdout.write("  {: >{}} true positives\n".format(len(true_positives), width))
msg = "+ {: >{}} misclassifications".format(len(misclassifications), width)
if args.encoding == "BIO-2":
    msg += " (includes type inconsistencies assuming span is correct)"
sys.stdout.write(msg+"\n")
sys.stdout.write("+ {: >{}} partially matched\n".format(nb_partial_gold, width))
sys.stdout.write("+ {: >{}} false negatives\n".format(len(false_negatives), width))
sys.stdout.write("= {: >{}} total gold mentions\n".format(len(gold_mentions), width))
sys.stdout.write("------------------\n")
sys.stdout.write("Predicted mentions\n")
sys.stdout.write("------------------\n")
width = len(str(nb_pred_mentions))
sys.stdout.write("  {: >{}} true positives\n".format(len(true_positives), width))
msg = "+ {: >{}} misclassifications".format(len(misclassifications), width)
if args.encoding == "BIO-2":
    msg += " (includes type inconsistencies assuming span is correct)"
sys.stdout.write(msg+"\n")
sys.stdout.write("+ {: >{}} partially matching\n".format(nb_partial_pred, width))
sys.stdout.write("+ {: >{}} false positives\n".format(len(false_positives), width))
sys.stdout.write("+ {: >{}} invalid mentions (prefix errors)\n".format(len(prefix_errors), width))
msg = "= {: >{}} total predicted mentions".format(nb_pred_mentions, width)
sys.stdout.write(msg+"\n")
sys.stdout.write("------------------\n")      

            
