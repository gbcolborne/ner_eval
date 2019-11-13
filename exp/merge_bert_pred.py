import argparse

""" Merge predictions file produced by run_transformers_ner.py with the input file. The sentences in the predictions file will have been shortened where a sentence is longer than the max seq length of the transformer. We want a prediction for every single token, so we map the predictions on to the original input."""

parser = argparse.ArgumentParser()
parser.add_argument("path_input")
parser.add_argument("path_predictions")
parser.add_argument("path_output")
args = parser.parse_args()

def stream_sents(path):
  with open(path) as f:
    sent = []
    for line in f:
      if line.startswith("-DOCSTART-"):
        continue
      if line == "" or line == "\n":
        if len(sent):
          yield sent	
          sent = []
      else:
        sent.append(line.strip())
    if len(sent):
      yield sent

sents_input = stream_sents(args.path_input)
sents_pred = stream_sents(args.path_predictions)


with open(args.path_output, 'w') as f:
  for sent,pred in zip(sents_input, sents_pred):
    tokens = []
    gold_labels = []
    for line in sent:
      elems = line.split(" ")
      token = elems[0]
      label = elems[1]
      tokens.append(token)
      gold_labels.append(label)
    pred_labels = []
    for i,line in enumerate(pred):
      elems = line.split(" ")
      token = elems[0]
      label = elems[-1]
      pred_labels.append(label)
      if token != tokens[i]:
        print("Warning: token mismatch: {} != {}".format(token, tokens[i]))
    if len(sent) > len(pred):
      print("Warning: found an input sentence with {} tokens but {} predictions".format(len(sent), len(pred)))
      pred_labels += ['O' for _ in range(len(sent)-len(pred))]
    for t,g,p in zip(tokens,gold_labels,pred_labels):
      f.write("{} {} {}\n".format(t,g,p)) 
    f.write("\n")
