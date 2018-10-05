import os, sys, argparse, json

doc = """Given the path of a directory where NeuroNER dumped its output
(model checkpoints, predictions, evaluation results, etc.), find the path of the
predictions at the best epoch. Write this path to stdout.

"""

parser = argparse.ArgumentParser(description=doc)
parser.add_argument("neuroner_output", help="Path of directory containing output of NeuroNER")
parser.add_argument("partition", choices=["train", "valid", "test"])
args = parser.parse_args()
args.neuroner_output = os.path.abspath(args.neuroner_output)

# Parse results file and get best epoch
path_results = args.neuroner_output + "/results.json"
with open(path_results) as f:
    res = json.load(f)
    early_stop = res['execution_details']['early_stop']
    nb_epochs_effective = res['execution_details']['num_epochs']
best_epoch = nb_epochs_effective
if early_stop:
    best_epoch -= res['model_options']['patience']

# Infer name of file containing conlleval results for best epoch. The
# epoch number is zero-padded to a width of 3.
predictions_file_name = "{:03d}_{}.txt".format(best_epoch, args.partition)
predictions_path = args.neuroner_output + "/" + predictions_file_name
sys.stdout.write(predictions_path)
