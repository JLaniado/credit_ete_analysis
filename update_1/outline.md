# Update 1 — Presentation Outline & Design Spec

Screening Peer-Lending Loans · ExCo Update 1 (Diagnostic & Descriptive Models)
Target length: **~8 minutes**, 8 slides.

## Narrative spine

Every ExCo goal — CEO (ROIC), CFO (interest profit), CMO (market share) — rises or falls
on the same two levers: **who gets approved**, and **how they're priced**. Update 1's job
is to show, with data, that both levers are currently miscalibrated, and that the borrower
population isn't one blob but a handful of distinct, recoverable segments — setting up
Update 2/3 (a predictive model + threshold/pricing optimization) as the obvious next step.

## Key numbers (verified against `data/loanskpi.csv`, 9,578 loans)

- Overall default rate: **16.0%**
- `credit.policy` splits the base 80.5% (pass) / 19.5% (fail)
- Default rate: **13.2%** within policy=1 vs **27.8%** within policy=0 (2.1x)
- Of the 19.5% rejected by policy, 72.2% never default → **14.1% of all applicants**
  are "good" loans the current rule turns away (false negatives)
- `purpose` default rate range: major_purchase/credit_card ≈ 11–12% (lowest) →
  small_business ≈ 27.8% (highest)
- fico and int.rate are strongly negatively correlated (r = −0.71) — LendingClub's own
  pricing already leans on fico, which is why the heatmap needs a *second*, less-priced
  axis to show a real gap, not just restate int.rate ≈ f(fico). Tested dti, revol.util,
  log.annual.inc, and inq.last.6mths as the second axis; **inq.last.6mths** (recent credit
  inquiries) gave the cleanest, most monotonic gradient on both axes: even top-FICO
  borrowers (742–827) go from **5.6% → 16.3%** default just by having 3+ recent inquiries
  vs. none — a risk signal pricing largely misses
- K-means (k=4, 8 standardized application-time variables, int.rate excluded): 4 named
  segments, most notably a small (~2%) "high-income jumbo revolver" segment with the
  *highest* default rate (28.2%) — a pricing gap example
- PCA: PC1 = scale/establishment axis, PC2 = safety axis (fico +, revol.util −, dti −);
  biplot clusters line up with K-means — two independent methods, same segmentation

## Slide-by-slide

**1. Title (30s)**
"Screening Peer-Lending Loans" — Update 1. No chart. One line: three executives, one
shared problem.

**2. The business, as one diagram (60s)**
CEO / CFO / CMO goals converge onto two controllable levers: *who we approve* and
*how we price*. Conceptual diagram (3 boxes → 2 boxes), no bullets.

**3. The data, in one line (45s)**
One row = one funded loan. 9,578 loans, 16% default, no missing data, 2007–2010 vintage.
Visual: a simple split of "known at application time" (13 fields) vs. "known only after
the loan plays out" (3 fields — must be excluded from any future model). Not a column list.

**4. Lever 1 — Policy: are we rejecting the right people? (90s)**
Confusion-matrix-style visual: `credit.policy` × `default`. Headline: rejected loans are
still 72% good loans → **14% of all applicants** are false negatives under the current
rule. The rule is blunt, not targeted.

**5. Lever 2 — Pricing: are riskier segments priced up? (90s)**
2D binned default-rate heatmap: fico × recent credit inquiries (int.rate deliberately not
used as an axis — it's already a near-mirror of fico, r=−0.71, so it would just repeat the
fico story). Default rate climbs sharply with inquiry count *within every fico band*
(5.6% → 16.3% for top-tier borrowers alone); tie to the K-means jumbo-revolver segment as
a concrete instance where pricing doesn't track risk.

**6. Segments exist, and two methods agree (90s)**
Cleaned K-means parallel-coordinates + one-line PCA callout (safety axis, scale axis).
Point: two independent techniques converge on the same 3–4 borrower archetypes —
de-risks building a model on top of them.

**7. So what — the bridge to Update 2/3 (45s)**
One slide: policy gap + pricing gap + validated segments → next step is a predictive
model and a threshold/pricing optimization. No new data, just the pivot.

**8. Close (15s)**
Questions.

## Aesthetic & build spec

**Palette** (small, consistent, colorblind-safe; same hex values in every chart and in
the deck's own CSS):

| Role | Color | Hex |
|---|---|---|
| Background | warm near-white | `#FAFAF8` |
| Ink / text | charcoal (never pure black) | `#1F2430` |
| Primary / "good" (non-default) | muted slate blue | `#3866A8` |
| Risk / "bad" (default) — reserved exclusively for default signal | muted brick red | `#B04A44` |
| Neutral / de-emphasized | warm gray | `#C9C4BA` |
| Gridlines / hairlines | pale gray | `#E4E1DA` |

**Principles**
- Every slide leads with a visual. Title ≤ 6 words, at most one supporting line — no
  bullet walls.
- Charts: transparent background (so they sit flush on the slide), large legible
  sans-serif type matching the deck font, minimal gridlines, direct data labels instead
  of legends wherever possible, titles state the takeaway ("Rejected loans are mostly
  good loans"), not the variable name.
- Crimson is used *only* to mean "default" — never decoratively — so it stays meaningful
  every time the eye lands on it.
- Charts are rebuilt from the underlying data/logic (this repo's notebook as reference),
  not screenshotted from `output/`.

**Charts to (re)build**
1. Policy vs. default confusion-matrix / 100%-stacked view — rebuilt from the logic in
   `categorical_normalized_by_default.png`, restyled
2. New fico × recent-inquiries binned default-rate heatmap — does not exist in the repo, built fresh
3. Cleaned K-means parallel-coordinates — rebuilt from `kmeans_parallel_coordinates.png` logic
4. Two small conceptual diagrams (slide 2 goals→levers, slide 3 data split) — hand-built
   shapes, not data charts
