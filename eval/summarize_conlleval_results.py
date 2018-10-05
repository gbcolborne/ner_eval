import sys, os, argparse, re
import numpy as np
from mimetypes import guess_type

doc = """ Given the path of a directory containing conlleval results
files, extract a metric from each of the files (accuracy, precision,
recall or FB1, where the last 3 are weighted averages over all entity
types) and output a table that summarizes these results in 2 rows. """

parser = argparse.ArgumentParser(description=doc)
parser.add_argument("input_dir", help="path of directory containing results files")
parser.add_argument("-m", "--metric", choices=["accuracy", "precision", "recall", "FB1"], default="FB1")
parser.add_argument("-d", "--delimiter", default="\t", help="column delimiter for output table")
args = parser.parse_args()

# Define regex that matches the second line of the output of conlleval. 
regex = "^accuracy:\s{1,3}(\d{1,3}\.\d{2})%"
regex += "; precision:\s{1,3}(\d{1,3}\.\d{2})%"
regex += "; recall:\s{1,3}(\d{1,3}\.\d{2})%"
regex += "; FB1:\s{1,3}(\d{1,3}\.\d{2})$"
summary_line = re.compile(regex)

# Get paths of files
file_names = os.listdir(args.input_dir)
list.sort(file_names)

# Loop over files, get scores
header = []
scores = []
max_lines_checked = 100
for file_name in file_names:
    file_path = "{}/{}".format(args.input_dir, file_name)

    # Check if it's a text file
    file_type, file_encoding = guess_type(file_path)
    if file_type != "text/plain":
        msg = "WARNING: file '{}' does not seem to be a text file.".format(file_path)
        print(msg)
        continue
    
    summary_line_found=False
    line_count=0
    with open(file_path) as f:
        # Search for that summary line. It should be the second, but
        # we will scan a bunch of lines just in case some empty lines
        # were added or something.
        for line in f:
            match = summary_line.match(line)
            line_count += 1
            if line_count >= max_lines_checked:
                break
            if match:
                accuracy = match.group(1)
                precision = match.group(2)
                recall = match.group(3)
                FB1 = match.group(4)
                if args.metric == "accuracy":
                    scores.append(accuracy)
                elif args.metric == "precision":
                    scores.append(precision)
                elif args.metric == "recall":
                    scores.append(recall)
                elif args.metric == "FB1":
                    scores.append(FB1)
                header.append(file_name)
                summary_line_found = True
                break
    if not summary_line_found:
        msg = "WARNING: file '{}' does not appear to contain conlleval results.".format(file_path)
        print(msg)

# Convert scores to floats
scores = [float(x) for x in scores]
        
# Add average
avg_score = np.mean(scores)
scores.append(avg_score)
header.append("AVERAGE")
        
# Write results
score_strings = ["{:.2f}".format(x) for x in scores]
msg = "SUMMARY (metric={})".format(args.metric)
border = "=" * len(msg)
sys.stdout.write("\n{}\n{}\n{}\n".format(border, msg, border))
delimiter = " {} ".format(args.delimiter)
sys.stdout.write(delimiter.join(header) + "\n")
sys.stdout.write(delimiter.join(score_strings) + "\n")
sys.stdout.flush()
