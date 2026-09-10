"""Regenerate Update 1 presentation charts from data/loanskpi.csv.

Rebuilds (not screenshots of) the notebook's policy/default view plus a new
fico x dti default-rate heatmap and a restyled K-means parallel-coordinates
chart, all using the palette in update_1/outline.md.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

INK = "#1F2430"
PRIMARY = "#3866A8"   # good / non-default
RISK = "#B04A44"      # default
NEUTRAL = "#C9C4BA"
GRID = "#E4E1DA"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "text.color": INK,
    "axes.edgecolor": GRID,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "axes.titlecolor": INK,
    "savefig.transparent": True,
    "figure.facecolor": "none",
    "axes.facecolor": "none",
})

df = pd.read_csv("data/loanskpi.csv")

# ---------------------------------------------------------------------------
# 1. Policy x default confusion-style grid
# ---------------------------------------------------------------------------
n = len(df)
cells = {}
for policy in (1, 0):
    for default in (0, 1):
        cells[(policy, default)] = ((df["credit.policy"] == policy) & (df["default"] == default)).sum()

fig, ax = plt.subplots(figsize=(7.2, 5.4))
ax.set_xlim(0, 2)
ax.set_ylim(0, 2)
ax.axis("off")

row_order = [1, 0]  # top row = policy pass, bottom = policy fail
col_order = [0, 1]  # left col = non-default, right = default
row_labels = {1: "Approved\n(credit.policy = 1)", 0: "Rejected\n(credit.policy = 0)"}
col_labels = {0: "Non-default", 1: "Default"}

for i, policy in enumerate(row_order):
    for j, default in enumerate(col_order):
        count = cells[(policy, default)]
        pct_of_total = count / n * 100
        x, y = j, 1 - i
        is_risk_cell = default == 1
        is_fn_cell = (policy == 0 and default == 0)
        face = RISK if is_risk_cell else PRIMARY
        alpha = 0.92 if is_fn_cell else (0.85 if is_risk_cell else 0.55)
        rect = plt.Rectangle((x, y), 1, 1, facecolor=face, alpha=alpha,
                              edgecolor="white", linewidth=3)
        ax.add_patch(rect)
        ax.text(x + 0.5, y + 0.60, f"{pct_of_total:.1f}%", ha="center", va="center",
                fontsize=26, fontweight="bold", color="white")
        ax.text(x + 0.5, y + 0.30, f"{count:,} loans", ha="center", va="center",
                fontsize=11, color="white", alpha=0.9)
        if is_fn_cell:
            ax.text(x + 0.5, y - 0.14, "false negatives", ha="center", va="center",
                     fontsize=11.5, color=RISK, fontweight="bold")

for j, default in enumerate(col_order):
    ax.text(j + 0.5, 2.08, col_labels[default], ha="center", va="bottom",
             fontsize=13, color=INK, fontweight="bold")
for i, policy in enumerate(row_order):
    ax.text(-0.08, (1 - i) + 0.5, row_labels[policy], ha="right", va="center",
             fontsize=12, color=INK, linespacing=1.5)

ax.set_ylim(-0.28, 2.2)
ax.set_xlim(-0.85, 2.05)
plt.tight_layout()
plt.savefig("update_1/assets/policy_confusion.png", dpi=200, bbox_inches="tight")
plt.close()

# ---------------------------------------------------------------------------
# 2. fico x inq.last.6mths binned default-rate heatmap
#    (inq.last.6mths chosen over dti/int.rate: it shows a clean, near-monotonic
#    gradient on both axes, and int.rate barely prices for it -> real pricing gap)
# ---------------------------------------------------------------------------
fico_bins = pd.qcut(df["fico"], 5, duplicates="drop")
inq_bins = pd.cut(df["inq.last.6mths"], bins=[-0.5, 0.5, 1.5, 2.5, df["inq.last.6mths"].max()],
                   labels=["0", "1", "2", "3+"])
pivot = df.groupby([fico_bins, inq_bins], observed=True)["default"].mean().unstack() * 100
pivot = pivot.sort_index(ascending=False)  # highest fico at top

fico_labels = [f"{iv.left:.0f}–{iv.right:.0f}" for iv in pivot.index]
inq_labels = list(pivot.columns)

from matplotlib.colors import LinearSegmentedColormap
cmap = LinearSegmentedColormap.from_list("risk", ["#FBEFEE", RISK])

fig, ax = plt.subplots(figsize=(7.6, 5.6))
vals = pivot.values
im = ax.imshow(vals, cmap=cmap, vmin=np.nanmin(vals), vmax=np.nanmax(vals), aspect="auto")

ax.set_xticks(range(len(inq_labels)))
ax.set_xticklabels(inq_labels, fontsize=11.5)
ax.set_yticks(range(len(fico_labels)))
ax.set_yticklabels(fico_labels, fontsize=11)
ax.set_xlabel("Credit inquiries, last 6 months", fontsize=12.5, labelpad=10)
ax.set_ylabel("FICO score", fontsize=12.5, labelpad=10)
ax.tick_params(length=0)
for spine in ax.spines.values():
    spine.set_visible(False)

thresh = (np.nanmin(vals) + np.nanmax(vals)) / 2
for i in range(vals.shape[0]):
    for j in range(vals.shape[1]):
        v = vals[i, j]
        color = "white" if v > thresh else INK
        ax.text(j, i, f"{v:.0f}%", ha="center", va="center", fontsize=12, color=color)

# annotate the worst cell: lowest fico row (last row), highest inquiry col (last col)
ax.add_patch(plt.Rectangle((vals.shape[1] - 1 - 0.5, vals.shape[0] - 1 - 0.5), 1, 1,
                            fill=False, edgecolor=INK, linewidth=2.5))

cbar = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.03)
cbar.ax.tick_params(labelsize=9.5, length=0)
cbar.outline.set_visible(False)
cbar.set_label("Default rate", fontsize=10.5)

plt.tight_layout()
plt.savefig("update_1/assets/fico_inq_heatmap.png", dpi=200, bbox_inches="tight")
plt.close()

print(f"Best cell (top fico, 0 inquiries): {vals[0, 0]:.1f}%")
print(f"Worst cell (bottom fico, 3+ inquiries): {vals[-1, -1]:.1f}%")
print(f"Within top fico band, 0 vs 3+ inquiries: {vals[0, 0]:.1f}% -> {vals[0, -1]:.1f}%")

# ---------------------------------------------------------------------------
# 3. K-means parallel coordinates (k=4, same 8 variables as notebook)
# ---------------------------------------------------------------------------
cluster_vars = ["installment", "log.annual.inc", "dti", "fico",
                 "days.with.cr.line", "revol.bal", "revol.util", "inq.last.6mths"]
X = StandardScaler().fit_transform(df[cluster_vars])
km = KMeans(n_clusters=4, n_init=10, random_state=42).fit(X)
centers = pd.DataFrame(km.cluster_centers_, columns=cluster_vars)
sizes = pd.Series(km.labels_).value_counts(normalize=True).sort_index() * 100
default_rates = df.groupby(km.labels_)["default"].mean() * 100

# order clusters by default rate (ascending) for a clean visual story
order = default_rates.sort_values().index.tolist()

short_labels = {
    "installment": "Installment",
    "log.annual.inc": "Income (log)",
    "dti": "DTI",
    "fico": "FICO",
    "days.with.cr.line": "Credit history",
    "revol.bal": "Revolving balance",
    "revol.util": "Revolving util.",
    "inq.last.6mths": "Recent inquiries",
}

cluster_colors = ["#3866A8", "#7FA0C9", "#D89A8B", "#B04A44"]  # blue -> red ramp by risk

Y_MAX = 2.0
fig, ax = plt.subplots(figsize=(11, 5.8))
x = np.arange(len(cluster_vars))
end_vals = []
for rank, cl in enumerate(order):
    y_raw = centers.loc[cl].values
    y = np.clip(y_raw, -2.0, Y_MAX)
    color = cluster_colors[rank]
    ax.plot(x, y, marker="o", markersize=5, linewidth=2.6, color=color, alpha=0.95, zorder=3)
    # mark any clipped (off-chart) point with an arrow + true value
    for xi, (yr, yc) in enumerate(zip(y_raw, y)):
        if yr > Y_MAX:
            ax.annotate("", xy=(xi, Y_MAX), xytext=(xi, Y_MAX - 0.28),
                        arrowprops=dict(arrowstyle="-|>", color=color, lw=2))
            ax.text(xi, Y_MAX + 0.08, f"{yr:.1f}", ha="center", va="bottom",
                     fontsize=9, color=color, fontweight="bold")
    end_vals.append((y[-1], rank, cl))

# stagger end-of-line labels vertically so they never overlap
end_vals.sort(key=lambda t: -t[0])
min_gap = 0.16
for i in range(1, len(end_vals)):
    if end_vals[i - 1][0] - end_vals[i][0] < min_gap:
        end_vals[i] = (end_vals[i - 1][0] - min_gap, end_vals[i][1], end_vals[i][2])
for y_pos, rank, cl in end_vals:
    color = cluster_colors[rank]
    label = f"{sizes[cl]:.0f}% of loans · {default_rates[cl]:.0f}% default"
    ax.text(x[-1] + 0.15, y_pos, label, va="center", fontsize=10.5, color=color, fontweight="bold")

ax.axhline(0, color=GRID, linewidth=1, zorder=1)
ax.set_xticks(x)
ax.set_xticklabels([short_labels[v] for v in cluster_vars], fontsize=11, rotation=12, ha="right")
ax.set_ylabel("Standardized value (z-score)", fontsize=11.5)
ax.set_xlim(-0.3, len(cluster_vars) + 2.0)
ax.set_ylim(-1.6, Y_MAX + 0.35)
for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(length=0)
ax.grid(axis="y", color=GRID, linewidth=0.8, alpha=0.6)
plt.tight_layout()
plt.savefig("update_1/assets/kmeans_parallel.png", dpi=200, bbox_inches="tight")
plt.close()

print("Cluster sizes (%):", sizes.to_dict())
print("Cluster default rates (%):", default_rates.round(1).to_dict())
print("Saved charts to update_1/assets/")
