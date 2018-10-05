from __future__ import division
import argparse, copy
from matplotlib import pyplot as plt
from matplotlib import cycler
from math import pi
import numpy as np


doc = """Given a CSV file containing the scores of different systems
(e.g. WER and TER, as computed by new_eval.py), make plots to compare
the system scores."""

def minmax_normalize(matrix):
    """ Apply min-max normalization to the columns in a 2-D numpy array. """
    mn = matrix.min(0)
    mx = matrix.max(0)
    spread = mx-mn
    # Replace 0 with 1 to avoid dividing by 0, which would happen if
    # max-min=0, which means that all values in the column are
    # identical. In this case, the end result will be 0, as we
    # subtract the minimum in the numerator.
    spread[spread==0] = 1
    normalized = (matrix-mn)/spread
    return normalized

def max_normalize(matrix):
    """ Apply max normalization to the columns in a 2-D numpy array. """
    mx = matrix.max(0)
    normalized = matrix/mx
    return normalized

def show_radar_chart(data, row_names, col_names, yticks):
    """Make radar chart (based on
https://python-graph-gallery.com/391-radar-chart-with-several-individuals/).

    Args:
    
    - data: a 2-D numpy array in which each column represents a
    variable and each row represents a data point.

    - col_names: list of column names (i.e. names of variables)

    - row_names: list of row names (i.e. names for each data point)

    - yticks: ordered list of ticks on the y axis. The first will be
      the lower limit of the y axis and the last will be the upper
      limit.

    """

    # Set angles between axes
    N = data.shape[1]
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    ax = plt.subplot(111, polar=True)

    # If you want the first axis to be on top:
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)

    # Draw one axe per variable + add labels
    plt.xticks(angles[:-1], col_names)

    # Set ticks and limits of y axis
    labels = [str(x) for x in ticks]
    ax.set_rlabel_position(0)
    plt.yticks(yticks, labels, color="grey", size=7)
    plt.ylim(yticks[0], yticks[-1])

    # Plot lines for each system
    colors = ['b', 'r', 'g', 'm', 'y']
    for (row_name, vals, color) in zip(row_names, data.tolist(), colors):
        vals.append(vals[0])
        ax.plot(angles, vals, linewidth=1, linestyle='solid', label=row_name)
        ax.fill(angles, vals, color, alpha=0.1)

    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    plt.show()

parser = argparse.ArgumentParser(description=doc)
msg = """Path of a CSV file containing system scores. First column should
contain the system names, and the header should contain the name of
the scores in each column."""
parser.add_argument("input", help=msg)
args = parser.parse_args()

# Load scores
with open(args.input) as f:
    header = f.readline().strip().split(",")
    if len(header) < 2:
        msg = "Error: header contains less than 2 columns"
        raise ValueError(msg)
    score_names = header[1:]
    system_names = []
    scores = []
    nb_cols = len(header)
    for line in f:
        line = line.strip()
        if not len(line):
            continue
        cols = line.split(",")
        if len(cols) != nb_cols:
            msg = "Error: expected {} columns, found {}".format(nb_cols, len(cols))
            msg += ": {}".format(line)
            raise ValueError(msg)
        system_name = cols[0]
        system_names.append(system_name)
        system_scores = cols[1:]
        system_scores = [float(x) for x in system_scores]
        scores.append(system_scores)
print(system_names)
print(scores)
        
# Print scores
col_widths = []
col_widths.append(max([len(n) for n in system_names] + [len("System")]))
for col in range(len(score_names)):
    width = len(score_names[col])
    for row in range(len(scores)):
        score = scores[row][col]
        score_str_len = len(str(score))
        if score_str_len > width:
            width = score_str_len
    width += 2
    col_widths.append(width)
out = "{msg: <{fill}}".format(msg="System", fill=col_widths[0])
for col in range(len(score_names)):
    out += "{msg: >{fill}}".format(msg=score_names[col], fill=col_widths[col])
print(out)
for row in range(len(scores)):
    out = "{msg: <{fill}}".format(msg=system_names[row], fill=col_widths[0])
    for col in range(len(scores[row])):
        out += "{msg: >{fill}}".format(msg=scores[row][col], fill=col_widths[col])
    print(out)


# Make bar plot
scores = np.asarray(scores)
fig, ax = plt.subplots()

# Set limits of y axis
step=0.02 # Step between ticks on the y axis
low = 0.0
high = (np.ceil(scores.max()/step) + 1) * step
ax.set_ylim([low, high])

# Plot bars
index = np.arange(len(score_names))
bar_width = 1 / (len(system_names) + 2)
bar_cycle = (cycler('hatch', ['///', '--', '...', '\\\\\\', '++', 'xxx', '\\', '\///']))
styles = bar_cycle()
for sys_ix in range(len(system_names)):
    pos = index + (sys_ix * bar_width)
    sys_scores = scores[sys_ix]
    rects = ax.bar(pos, sys_scores, bar_width, label=system_names[sys_ix],
                   edgecolor="k", **next(styles))
ax.set_xlabel('Metric')
ax.set_ylabel('Scores')
ax.set_title('Scores by system')
dist_to_middle = (len(system_names) / 2 - 0.5) * bar_width
ax.set_xticks(index + dist_to_middle)
ax.set_xticklabels(score_names)
ax.legend()
fig.tight_layout()
plt.show()

  

# Make radar chart with normalized data
scores = max_normalize(scores)
#scores = minmax_normalize(scores)
low = 0.0
step=0.2 # Step between ticks on the y axis
high=1.
ticks = np.around(np.arange(low, high+step, step=step), decimals=1)
show_radar_chart(scores, system_names, score_names, ticks)


# Make radar chart with un-normalized data
low = 0.0
step=0.05 # Step between ticks on the y axis
high = (np.ceil(scores.max()/step) + 1) * step
ticks = np.around(np.arange(low, high+step, step=step), decimals=2)
print(ticks)
show_radar_chart(scores, system_names, score_names, ticks)
