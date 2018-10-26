import argparse, os, sys, re, math
import numpy as np
from glob import glob
dir_data_utils = os.path.dirname(os.path.realpath(__file__))+"/../data_utils"
sys.path.append(dir_data_utils)
from matplotlib import pyplot as plt
from data_utils import stream_sents
from eval_utils import get_bio2_mention_offsets

doc=""" Given the predictions of an NER system on dev and test sets at
each epoch of training, check how well the dev set accuracy
approximates the test set accuracy, as a function of the size of the
dev set."""

parser = argparse.ArgumentParser(description=doc)
msg=("Path of directory containing files matching the pattern "
     "<epoch>_valid.txt and <epoch>_test.txt for each epoch, where "
     "<epoch> is zero-padded to a minimum width of 3. This format "
     "matches the files produced by NeuroNER during training. These "
     "files should contain whitespace-separated columns, with gold "
     "and predicted labels (in BIO-2 format) in the last 2 columns, "
     "and empty lines between sentences.")
parser.add_argument("pred_dir", help=msg)
args = parser.parse_args()

# Get paths of files
paths_dev = glob(os.path.join(args.pred_dir, "*_valid.txt"))
paths_test = glob(os.path.join(args.pred_dir, "*_test.txt"))
nb_epochs = len(paths_dev)
print("\nNb epochs: {}".format(nb_epochs))
if len(paths_dev) != len(paths_test):
    msg = "Nb files for dev set ({})".format(len(paths_dev))
    msg += " and test set ({}) do not match".format(len(paths_test))
    raise ValueError(msg)

# Get gold mentions in dev set (at any epoch)
gold_mentions = []
for sent in stream_sents(paths_dev[0]):
    gold_labels = []
    for line in sent:
        elems = line.split()
        gold_label = elems[-2]
        gold_labels.append(gold_label)
    offsets = get_bio2_mention_offsets(gold_labels)
    mentions = {}
    for (beg, end) in offsets:
        etype = gold_labels[beg][2:]
        mentions[(beg,end)] = etype
    gold_mentions.append(mentions)
nb_sents = len(gold_mentions)
nb_gold = np.asarray([len(x) for x in gold_mentions]).reshape(nb_sents, 1)
nb_nnz = sum(1 for x in gold_mentions if len(x))
print("Nb sents in dev set: {}".format(nb_sents))
print("Nb sents containing at least one gold mention: {}".format(nb_nnz))
print("Nb gold mentions in dev set: {}".format(nb_gold.sum()))


# Go through predictions on dev set at each epoch, and store number of
# predicted mentions and number of correct predicted mentions
nb_pred = np.zeros((nb_sents, nb_epochs))
nb_correct = np.zeros((nb_sents, nb_epochs))
print("\nEvaluating predicted mentions on dev set at each epoch...")
for path in paths_dev:
    # Get epoch from file name
    basename = os.path.basename(path)
    print("Processing {}...".format(basename))
    match = re.search("^(\d{3,})_", basename)
    if match:
        epoch = int(match.group(1))
    else:
        msg = "Filename {} does not match pattern <epoch>_valid.txt".format(basename)
        raise ValueError(msg)

    # Get predicted mentions and check how many are correct
    for sent_ix, sent in enumerate(stream_sents(path)):
        pred_labels = []
        for line in sent:
            elems = line.split()
            pred_label = elems[-1]
            pred_labels.append(pred_label)
        pred_mention_offsets = get_bio2_mention_offsets(pred_labels)
        nb_pred[sent_ix, epoch] = len(pred_mention_offsets)
        correct_count = 0
        for (beg, end) in pred_mention_offsets:
            etype = pred_labels[beg][2:]
            if (beg, end) in gold_mentions[sent_ix]:
                if etype == gold_mentions[sent_ix][(beg, end)]:
                    correct_count += 1
        nb_correct[sent_ix, epoch] = correct_count

# Compute f-score on entire dev set
p = nb_correct[:,:].sum(0) / nb_pred[:,:].sum(0) 
r = nb_correct[:,:].sum(0) / nb_gold[:,0].sum() 
f = 2 * p * r / (p + r)

# Get best epoch
best_epoch = np.argmax(f, axis=0)
f_score_dev = f[best_epoch]
print("\nBest epoch on dev set: {}".format(best_epoch))
print("F-score on dev set at best epoch: {:.4f}".format(f_score_dev))

# Compute f-score on test set at best epoch
test_nb_pred = 0
test_nb_gold = 0
test_nb_correct = 0
path = os.path.join(args.pred_dir, "{:03d}_test.txt".format(best_epoch))
for sent in stream_sents(path):
    pred_labels = []
    gold_labels = []
    for line in sent:
        elems = line.split()
        pred_labels.append(elems[-1])
        gold_labels.append(elems[-2])
    pred_mention_offsets = get_bio2_mention_offsets(pred_labels)
    test_nb_pred += len(pred_mention_offsets)
    gold_mention_offsets = get_bio2_mention_offsets(gold_labels)
    test_nb_gold += len(gold_mention_offsets)
    pred_mentions = {}
    for (beg, end) in pred_mention_offsets:
        etype = pred_labels[beg][2:]
        pred_mentions[(beg,end)] = etype
    for (beg, end) in gold_mention_offsets:
        etype = gold_labels[beg][2:]
        if (beg, end) in pred_mentions and etype == pred_mentions[(beg, end)]:
            test_nb_correct += 1
p = test_nb_correct / test_nb_pred
r = test_nb_correct / test_nb_gold
f_score_test = 2 * p * r / (p + r)
print("F-score on test set at best epoch: {:.4f}".format(f_score_test))


# Bootstrap best epoch and f-score (at globally best epoch) by
# resampling. Compute percentile confidence interval.
sentence_ids = list(range(nb_sents))
nb_resamples = 20000
sample_size_ratios = [2**-7, 2**-6, 2**-5, 2**-4, 2**-3, 2**-2, 2**-1, 2**0]
sample_sizes = [int(ratio*nb_sents) for ratio in sample_size_ratios]
conf_levels = [80,90,95]
f_scores_by_sample_size = {}
best_epochs_by_sample_size = {}
f_score_low_lims = {x:[] for x in conf_levels}
f_score_up_lims = {x:[] for x in conf_levels}
epoch_low_lims = {x:[] for x in conf_levels}
epoch_up_lims = {x:[] for x in conf_levels}
for sample_size in sample_sizes:
    f_scores = []
    best_epochs = []
    while len(f_scores) < nb_resamples: 
        sample = np.random.choice(sentence_ids, size=sample_size, replace=True)
        # Check if sample contains at least one gold mention
        sample_nb_gold = nb_gold[sample,0].sum()
        if sample_nb_gold == 0:
            continue

        # Compute f-scores at each epoch on sample
        sample_nb_correct = nb_correct[sample,:].sum(0)
        sample_nb_pred = nb_pred[sample,:].sum(0)
        p = np.zeros(nb_epochs, dtype=float)
        for ix in np.nonzero(sample_nb_pred):
            p[ix] = sample_nb_correct[ix] / sample_nb_pred[ix]
        r = np.zeros(nb_epochs, dtype=float)
        if sample_nb_gold != 0:
            r = sample_nb_correct / sample_nb_gold
        f = np.zeros(nb_epochs, dtype=float)
        for ix in np.nonzero(p+r):
            f[ix] = 2 * p[ix] * r[ix] / (p[ix] + r[ix])

        # Get best epoch for this bootstrap sample
        best_epochs.append(np.argmax(f))
        
        # Store difference f-score on this bootstrap sample at
        # (globally) best epoch.
        f_scores.append(f[best_epoch])
    f_scores_by_sample_size[sample_size] = f_scores
    best_epochs_by_sample_size[sample_size] = best_epochs

    print("\nResults for sample size={}".format(sample_size))
    for conf_level in conf_levels:
        low_pctl = (100-conf_level)//2
        high_pctl = 100-(100-conf_level)//2

        # Compute percentile confidence intervals
        f_score_low_lim = np.percentile(f_scores, low_pctl, interpolation="midpoint")
        f_score_up_lim = np.percentile(f_scores, high_pctl, interpolation="midpoint")
        f_score_low_lims[conf_level].append(f_score_low_lim)
        f_score_up_lims[conf_level].append(f_score_up_lim)
        epoch_low_lim = np.percentile(best_epochs, low_pctl, interpolation="midpoint")
        epoch_up_lim = np.percentile(best_epochs, high_pctl, interpolation="midpoint")
        epoch_low_lims[conf_level].append(epoch_low_lim)
        epoch_up_lims[conf_level].append(epoch_up_lim)

        # Print confidence intervals for this confidence level
        msg = "{}% conf. interval of f-score at globally best epoch ({}):".format(conf_level, best_epoch) 
        msg += " [{:.4f},{:.4f}]".format(f_score_low_lim, f_score_up_lim)
        print(msg)
        msg = "{}% conf. interval of best epoch:".format(conf_level) 
        msg += " [{},{}]".format(epoch_low_lim, epoch_up_lim)
        print(msg)


# Make box plot of f-scores (at globally best epoch) with respect to
# sample size
flierprops = {"alpha":0.1, "markerfacecolor":"w", "fillstyle":"none"}
plt.boxplot([f_scores_by_sample_size[size] for size in sample_sizes], flierprops=flierprops, showmeans=True)
xtick_labels = ["1/{}".format(int(2**-math.log(ratio, 2))) for ratio in sample_size_ratios]
plt.xticks(range(1,len(sample_sizes)+1), xtick_labels)
plt.axhline(f_score_dev, linewidth=1, color='k', linestyle="--", label="dev f-score")
plt.xlabel("Resample size (fraction of total dev set size)")
plt.ylabel("F-score")
#plt.legend()
plt.show()

# Plot confidence interval of f-score (at globally best epoch) with
# respect to sample size
for conf_level in conf_levels:
    f_score_err_pos = [f-f_score_dev for f in f_score_up_lims[conf_level]]
    f_score_err_neg = [f_score_dev-f for f in f_score_low_lims[conf_level]]
    plt.errorbar(sample_size_ratios, [f_score_dev]*len(sample_size_ratios), yerr=[f_score_err_neg, f_score_err_pos], fmt="none", ecolor="k", capsize=3, capthick=1)
    plt.axhline(f_score_dev, linewidth=1, color='k', linestyle=":")
    plt.xscale("log", basex=2)
    xtick_labels = ["1/{}".format(int(2**-math.log(ratio, 2))) for ratio in sample_size_ratios]
    plt.xticks(sample_size_ratios, xtick_labels)
    plt.xlabel("Resample size (fraction of total dev set size)")
    plt.ylabel("F-score ({}% confidence interval)".format(conf_level))
    plt.show()

# Make box plot of best epochs with respect to sample size
plt.boxplot([best_epochs_by_sample_size[size] for size in sample_sizes], flierprops=flierprops, showmeans=True)
xtick_labels = ["1/{}".format(int(2**-math.log(ratio, 2))) for ratio in sample_size_ratios]
plt.xticks(range(1,len(sample_size_ratios)+1), xtick_labels)
plt.axhline(best_epoch, linewidth=1, color='k', linestyle=":")
plt.xlabel("Resample size (fraction of total dev set size)")
plt.ylabel("Best epoch")
plt.show()

# Plot confidence interval of best epoch with respect to sample size
for conf_level in conf_levels:
    epoch_err_pos = [e-best_epoch for e in epoch_up_lims[conf_level]]
    epoch_err_neg = [best_epoch-e for e in epoch_low_lims[conf_level]]
    plt.errorbar(sample_size_ratios, [best_epoch]*len(sample_size_ratios), yerr=[epoch_err_neg, epoch_err_pos], fmt="none", ecolor="k", capsize=3, capthick=1)
    plt.axhline(best_epoch, linewidth=1, color='k', linestyle=":")
    plt.xscale("log", basex=2)
    xtick_labels = ["1/{}".format(int(2**-math.log(ratio, 2))) for ratio in sample_size_ratios]
    plt.xticks(sample_size_ratios, xtick_labels)
    plt.xlabel("Resample size (fraction of total dev set size)")
    plt.ylabel("Best epoch ({}% confidence interval)".format(conf_level))
    plt.show()

