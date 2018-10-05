import os, sys, argparse, json

doc = """ Given the path of a directory where the `spacy train`
command wrote models for a certain number of epochs, return the path
of the model that achieved the highest score according to a given
metric. This seems to be necessary because, as far as I can tell,
`spacy train` does not allow for early stopping at the moment."""

parser = argparse.ArgumentParser(description=doc)
parser.add_argument("models_dir", help="path of directory containing the models for each epoch")
metrics = ["ents_p", "ents_r", "ents_f", "tags_acc", "token_acc", "uas", "las"]
parser.add_argument("-m", "--metric", choices=metrics, default="ents_f")
parser.add_argument("-d", "--debug", action="store_true")
args = parser.parse_args()
args.models_dir = (os.path.abspath(args.models_dir))

model_names = os.listdir(args.models_dir)
model_names = filter(lambda x:x!="model-final", model_names)
max_score = float("-inf")
best_model_path = None
for model_name in model_names:
    model_path = "{}/{}".format(args.models_dir, model_name)
    scores_path = "{}/accuracy.json".format(model_path)
    with open(scores_path) as f:
        scores = json.load(f)
        score = float(scores[args.metric])
        if score > max_score:
            if args.debug:
                print("New best model: {} ({}={})".format(model_name, args.metric, score))
            max_score = score
            best_model_path = model_path
sys.stdout.write("{}".format(best_model_path))
