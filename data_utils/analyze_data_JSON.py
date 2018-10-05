import os, sys, argparse, json

doc = """
Count and analyze entity mentions in a dataset for fine-grained entity
typing (in JSON format).

"""

# Args
parser = argparse.ArgumentParser(description=doc)
parser.add_argument('path')
args = parser.parse_args()
path = os.path.abspath(args.path)

# Count mentions and compute tag frequency distribution
data = json.load(open(path))
nb_mentions = len(data)
tag_freqs = {}
for example in data:
    for tag in example['tags']:
        if tag not in tag_freqs:
            tag_freqs[tag] = 0
        tag_freqs[tag] += 1

# Print total number of entity mentions
print()
print("Total mention count: {}".format(nb_mentions))
                
# Print tag frequency distribution
print()
print("Tag frequencies:")
for k,v in sorted(tag_freqs.items(), key=lambda x:x[1], reverse=True):
    print("- {}\t{}".format(k,v))



