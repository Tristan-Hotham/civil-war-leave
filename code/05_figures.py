"""Step 5. Figures for the page (img/*.jpg), the blog (release/blog/b_*.png, 1800 px), the paper (release/paper/f_*.pdf,
vector) and header.png (1200 x 630). Light paper background. Leave share: blue (low) to ochre (high), a neutral scale with
no party colours; royalist share of a county's members: green (Parliament) to crimson (King)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib import font_manager as fm
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np, pandas as pd, geopandas as gpd
import statsmodels.formula.api as smf
from PIL import Image
from common import *

for f in ("FrauncesVar.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf", "SourceSerif4-It.ttf", "IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf"):
    fm.fontManager.addfont(f"{FONTS}/{f}")
SERIF = "Source Serif 4"; DISP = fm.FontProperties(fname=f"{FONTS}/FrauncesVar.ttf").get_name(); MONO = "IBM Plex Mono"
PAPER, INK, MUT, RULE = "#F6EED8", "#2B2119", "#6E604E", "#D9C9A3"
SEA = "#E4E9E6"
BLUE, OCHRE, GREY = "#2F6A9E", "#B5651D", "#9C9384"
KING, PARL = "#9B2D30", "#4E7A63"
LEAVE = LinearSegmentedColormap.from_list("lv", ["#1F4E79", "#7EA6C9", "#EEEAE2", "#E3A26B", "#9C4A12"])
LNORM = Normalize(25, 75)
ROY = LinearSegmentedColormap.from_list("ry", [PARL, "#A9C0B1", "#EFE7D6", "#D9958F", KING])
plt.rcParams.update({"font.family": SERIF, "font.size": 12, "axes.edgecolor": MUT, "axes.labelcolor": INK, "xtick.color": MUT,
                     "ytick.color": MUT, "axes.facecolor": PAPER, "figure.facecolor": PAPER, "axes.unicode_minus": False,
                     "pdf.fonttype": 42, "axes.spines.top": False, "axes.spines.right": False})
HALO = [pe.withStroke(linewidth=3, foreground=PAPER)]
R = jload(f"{DATA}/results.json")
A = pd.read_csv(f"{DATA}/analysis.csv")
CA = pd.read_csv(f"{DATA}/county_allegiance.csv")
LP = pd.read_csv(f"{DATA}/lp1640_constituencies.csv")
S = gpd.read_file(f"{SCR}/seats_27700.gpkg").merge(A, on="code")
L = gpd.read_file(f"{DATA}/danelaw_line.geojson").to_crs(27700)
LINE_G = L[L.k == "line"]
H = gpd.read_file(f"{HC}/historic_counties.geojson").to_crs(27700).merge(CA, on="county", how="left")
BLOG, PAPD = f"{REL}/blog", f"{REL}/paper"
for d_ in (BLOG, PAPD):
    os.makedirs(d_, exist_ok=True)
SRC = ("Data: Leave estimates Hanretty (2017); 2011 census (ONS, OGL); boundaries ONS/OS (OGL); Long Parliament list, Wikipedia (CC BY-SA 4.0);\n"
       "historic counties rebuilt from Wikidata (CC0). maps.tristanhotham.com/civil-war-leave")
X0, X1, Y0, Y1 = 130000, 660000, 5000, 670000


def out(fig, name, page=True, blog=True, paper=True):
    if paper:
        fig.savefig(f"{PAPD}/f_{name}.pdf", facecolor=fig.get_facecolor())
    fig.savefig(f"{SCR}/{name}.png", dpi=220, facecolor=fig.get_facecolor())
    plt.close(fig)
    im = Image.open(f"{SCR}/{name}.png").convert("RGB")
    if page:
        w = min(1500, im.size[0]); im.resize((w, round(im.size[1] * w / im.size[0])), Image.LANCZOS).save(f"{IMG}/{name}.jpg", quality=85, optimize=True)
    if blog:
        im.resize((1800, round(im.size[1] * 1800 / im.size[0])), Image.LANCZOS).save(f"{BLOG}/b_{name}.png", optimize=True)
    os.remove(f"{SCR}/{name}.png")


def title(fig, t, sub, y=0.965):
    fig.text(0.04, y, t, fontsize=21, fontweight="bold", family=DISP, color=INK, va="top")
    fig.text(0.04, y - 0.058, sub, fontsize=12, color=MUT, va="top")


def foot(fig, s=SRC):
    fig.text(0.04, 0.012, s, fontsize=8.3, family=MONO, color=MUT, va="bottom", linespacing=1.4)


def mapax(ax):
    ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1); ax.set_aspect("equal"); ax.set_axis_off()
    ax.add_patch(plt.Rectangle((X0, Y0), X1 - X0, Y1 - Y0, color=SEA, zorder=0))


def cbar(fig, rect, cmap, norm, ticks, labels, lab):
    cax = fig.add_axes(rect)
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax, orientation="horizontal", ticks=ticks)
    cb.ax.set_xticklabels(labels, fontsize=9.5); cb.outline.set_edgecolor(MUT); cb.ax.set_title(lab, fontsize=10, color=INK, loc="left")


EN = S[S.country == "England"]
WAL = S[S.country == "Wales"]
x = R["x"]; t1, t2 = R["t1"], R["t2"]

# ---------- 1. three maps
fig = plt.figure(figsize=(15, 9.8))
title(fig, "Two old fault lines and the 2016 vote", "England and Wales, 2010 constituencies. Left: estimated Leave share. Middle: the Danelaw line. Right: Long Parliament members who joined the King, by county")
axs = [fig.add_axes([0.02 + i * 0.325, 0.215, 0.31, 0.665]) for i in range(3)]
for ax in axs:
    mapax(ax)
S.plot(ax=axs[0], column="leave", cmap=LEAVE, norm=LNORM, edgecolor="white", linewidth=0.15)
LINE_G.plot(ax=axs[0], color=INK, linewidth=1.6)
S.plot(ax=axs[1], color=np.where(S.danelaw == 1, "#D8B98C", "#C9D3D6"), edgecolor="white", linewidth=0.15)
EN[(EN.dl_area_share > 0.05) & (EN.dl_area_share < 0.95)].plot(ax=axs[1], facecolor="none", edgecolor=MUT, linewidth=0.6, hatch="////")
dsh = H[H.county.isin(DANE_SHIRES)].dissolve()
dsh.boundary.plot(ax=axs[1], color=OCHRE, linewidth=1.3, linestyle=(0, (3, 2)))
LINE_G.plot(ax=axs[1], color=INK, linewidth=2.0)
H.plot(ax=axs[2], column="share", cmap=ROY, vmin=0, vmax=1, edgecolor="white", linewidth=0.5, missing_kwds={"color": "#DDD6C8", "hatch": "...", "edgecolor": "white"})
bo = LP[LP.kind == "borough"]
from pyproj import Transformer
TB = Transformer.from_crs(4326, 27700, always_xy=True)
bx, by = TB.transform(bo.lon.values, bo.lat.values)
axs[2].scatter(bx, by, s=9 + 4 * bo.seats, c=bo.share, cmap=ROY, vmin=0, vmax=1, edgecolor=INK, linewidth=0.35, zorder=5)
axs[0].text(X0 + 15000, Y1 - 30000, "Leave share", fontsize=13, family=DISP, fontweight="bold", color=INK, path_effects=HALO)
axs[1].text(X0 + 15000, Y1 - 30000, "The Danelaw line", fontsize=13, family=DISP, fontweight="bold", color=INK, path_effects=HALO)
axs[2].text(X0 + 15000, Y1 - 30000, "Members for the King", fontsize=13, family=DISP, fontweight="bold", color=INK, path_effects=HALO)
axs[1].text(X0 + 15000, Y1 - 62000, f"Danelaw side: {R['desc1']['dl_n']} seats\nOther side: {R['desc1']['nodl_n']} seats", fontsize=9.5, color=INK, va="top", path_effects=HALO)
axs[2].text(X0 + 15000, Y1 - 62000, f"{R['lp']['royalist']} of {R['lp']['seats']} members\nof 1640 joined the King", fontsize=9.5, color=INK, va="top", path_effects=HALO)
cbar(fig, [0.05, 0.16, 0.2, 0.016], LEAVE, LNORM, [25, 50, 75], ["25%", "50%", "75%"], "Estimated Leave share, 2016")
axs[1].legend(handles=[Patch(facecolor="#D8B98C", label="Danelaw side (half the seat or more)"), Patch(facecolor="#C9D3D6", label="Other side, and Wales"),
                       Patch(facecolor="none", edgecolor=MUT, hatch="////", label="Seat split by the line"),
                       Line2D([], [], color=INK, lw=2, label="Treaty line, Watling Street to Chester"),
                       Line2D([], [], color=OCHRE, lw=1.3, ls=(0, (3, 2)), label="The 15 Danelaw shires (medieval lists)")],
              loc="upper left", bbox_to_anchor=(0.0, -0.005), frameon=False, fontsize=8.6, ncol=1)
cbar(fig, [0.70, 0.16, 0.2, 0.016], ROY, Normalize(0, 1), [0, 0.5, 1], ["none", "half", "all"], "Share of a county's members who joined the King")
axs[2].text(X1 - 8000, Y0 + 12000, "Dots: boroughs (size = seats)\nDotted: no members (Durham)", fontsize=8.6, color=MUT, ha="right", va="bottom", path_effects=HALO)
foot(fig)
out(fig, "maps")

# ---------- 2. model ladders
fig = plt.figure(figsize=(12, 6.2))
title(fig, "Compared like with like, neither old line says much", "Estimates with 95% intervals as controls are added (main model in bold)")
lab = ["No controls", "+ region", "+ density", "+ composition\n(main)"]
for i, (T, unit, nm) in enumerate(((t1, "points of Leave, Danelaw minus other side", "Test 1: the Danelaw"),
                                   (t2, "points of Leave per 10 points of royalist share", "Test 2: members for the King"))):
    ax = fig.add_axes([0.12 + 0.47 * i, 0.2, 0.36, 0.58])
    L_ = T["ladder"]
    for j, k in enumerate(["M1", "M2", "M3", "M4"]):
        c = L_[k]; col = INK if k == "M4" else MUT
        ax.plot([c["lo"], c["hi"]], [3 - j, 3 - j], color=col, lw=2.4 if k == "M4" else 1.6)
        ax.plot(c["b"], 3 - j, "o", color=col, ms=8 if k == "M4" else 6)
        ax.text(c["hi"], 3 - j + 0.22, f"{c['b']:+.2f}", fontsize=10.5, color=col, ha="right", fontweight="bold" if k == "M4" else None)
    ax.axvline(0, color=RULE, lw=1.2, zorder=0)
    ax.set_yticks(range(4)); ax.set_yticklabels(lab[::-1], fontsize=10.5)
    ax.set_xlabel(unit, fontsize=10.5); ax.set_title(nm, loc="left", fontsize=14, family=DISP, fontweight="bold", color=INK)
    ax.set_ylim(-0.6, 3.6)
foot(fig, f"Test 1: England, {t1['main']['n']} seats, errors clustered by council. Test 2: England and Wales, {t2['main']['n']} seats, clustered by historic county.\n"
          "OLS. Composition: 2011 census age, education, class, ethnicity, birthplace, housing, industry, health. maps.tristanhotham.com/civil-war-leave")
out(fig, "ladder")

# ---------- 3. the line profile
rb = pd.DataFrame(t1["rd_bins"])
fig = plt.figure(figsize=(12, 7.4))
title(fig, "Crossing the Danelaw line", f"Seats within {BW_MAIN:.0f} km of the line, by distance from it (10 km bins). Left: Leave share. Right: Scandinavian village names")
ax1 = fig.add_axes([0.07, 0.17, 0.4, 0.6]); ax2 = fig.add_axes([0.57, 0.17, 0.4, 0.6])
d = A[(A.country == "England") & (A.dist_km <= BW_MAIN)]
for ax, col, ylab, c_ in ((ax1, "leave", "Estimated Leave share (%)", OCHRE), (ax2, "scand_share", "Settlements with -by, -thorpe, -thwaite, -toft names (%)", PARL)):
    ax.scatter(d.sdist_km, d[col], s=10, color=GREY, alpha=0.45, lw=0)
    ax.plot(rb.mid, rb["leave" if col == "leave" else "scand"], "o", color=c_, ms=8, zorder=4)
    for sgn in (-1, 1):
        dd = d[(np.sign(d.sdist_km) == sgn) & d[col].notna()]
        m = np.polyfit(dd.sdist_km, dd[col], 1); xx = np.array([0, sgn * BW_MAIN])
        ax.plot(xx, np.polyval(m, xx), color=c_, lw=2)
    ax.axvline(0, color=INK, lw=1.2, ls=(0, (4, 2)))
    ax.set_xlabel("km from the line (negative: English side; positive: Danelaw side)", fontsize=10.5); ax.set_ylabel(ylab, fontsize=10.5)
rd = t1["rd"]
ax1.text(0.02, 0.97, f"Jump at the line, with controls: {rd['main']['b']:+.1f} points\n(95% interval {rd['main']['lo']:.1f} to {rd['main']['hi']:+.1f})\nwithout controls: {rd['noctrl']['b']:+.1f}",
         transform=ax1.transAxes, va="top", fontsize=10, color=INK, path_effects=HALO)
ax2.text(0.02, 0.97, f"Jump at the line: {rd['scand']['b']:+.1f} points\n(95% interval {rd['scand']['lo']:.1f} to {rd['scand']['hi']:.1f})", transform=ax2.transAxes, va="top", fontsize=10, color=INK, path_effects=HALO)
foot(fig, f"Lines: straight-line fits on each side (raw). Jumps: local linear models with line-segment effects; Leave with 2011 census controls. N = {rd['main']['n']} seats.\n"
          "Place names: Wikidata settlements (CC0). maps.tristanhotham.com/civil-war-leave")
out(fig, "line")

# ---------- 4. balance at the line
B_ = rd["balance"]
NM = {"ldens": "log density", "lcity": "log km to a city", "pct_65plus": "aged 65+", "pct_degree": "degree-level qualification", "pct_noqual": "no qualifications",
      "pct_routine": "routine jobs", "pct_whitebrit": "White British", "pct_foreignborn": "born abroad", "pct_social": "social renting",
      "pct_manuf": "manufacturing", "pct_agri": "agriculture", "pct_mining": "mining", "pct_sick": "long-term sick"}
fig = plt.figure(figsize=(9.5, 7))
title(fig, "The two sides of the line are different places today", "Jump at the line in each 2011 census measure, in standard deviations, 95% intervals")
ax = fig.add_axes([0.3, 0.13, 0.64, 0.66])
ks = sorted(B_, key=lambda k: B_[k]["b_std"])
for j, k in enumerate(ks):
    c = B_[k]; s = c["sd"]; col = INK if c["p"] < 0.05 else GREY
    ax.plot([c["lo"] / s, c["hi"] / s], [j, j], color=col, lw=1.8); ax.plot(c["b_std"], j, "o", color=col, ms=6)
ax.axvline(0, color=RULE, lw=1.2, zorder=0)
ax.set_yticks(range(len(ks))); ax.set_yticklabels([NM[k] for k in ks], fontsize=10.5)
ax.set_xlabel("Danelaw side minus English side at the line (SD)", fontsize=10.5)
foot(fig, f"Dark: 95% interval excludes zero ({rd['balance_n_sig']} of {len(B_)}). Local linear, {BW_MAIN:.0f} km, segment effects, no controls.\nmaps.tristanhotham.com/civil-war-leave")
out(fig, "balance", blog=False)

# ---------- 5. robustness forests
fig = plt.figure(figsize=(13, 9.6))
title(fig, "Every planned check", "Estimates with 95% intervals. Test 1 in points of Leave; Test 2 per 10 points of royalist share (binary rows in points)")
ax1 = fig.add_axes([0.27, 0.1, 0.22, 0.75]); ax2 = fig.add_axes([0.76, 0.1, 0.22, 0.75])
rows1 = [("Main (M4)", t1["main"])] + [(v["label"], v) for k, v in t1["robust"].items() if k != "main"] + \
        [(f"Line design, {lab_}", t1["rd"][k]) for k, lab_ in (("main", "50 km"), ("bw25", "25 km"), ("bw75", "75 km"), ("tri", "triangular"), ("region", "region effects"), ("south", "south only"))] + \
        [("Placebo line 50 km north-east", t1["rd"]["placebo_ne"]), ("Placebo line 50 km south-west", t1["rd"]["placebo_sw"])]
rows2 = [("Main (M4)", t2["main"])] + [(v["label"], v) for k, v in t2["robust"].items() if k != "main"] + \
        [("Exploratory: boroughs inside the seat", t2["c2"])] + [(f"Other outcome: {v['label']}", v) for v in t2["outcomes"].values()]
SHORT = lambda s: (s.replace("Exposure: ", "").replace(" (per 10 points)", "").replace("the 15 Danelaw shires of the medieval shire lists", "15 Danelaw shires")
                   .replace("share of seat area on the Danelaw side", "area on the Danelaw side").replace("Scandinavian place-name share", "Scandinavian names")
                   .replace("England and Wales (Wales outside the Danelaw)", "England and Wales").replace("Drop London (Middlesex and Surrey seats in London)", "Drop London")
                   .replace("every disablement, no hand decisions", "mechanical coding").replace("majority of the county's members royalist (0/1)", "majority royalist (0/1)")
                   .replace("disablements dated 1642 to 1644 only", "dated 1642 to 1644 only").replace(" (seats contested)", "").replace(" (approximate)", ""))
for ax, rows, nm in ((ax1, rows1, "Test 1: the Danelaw"), (ax2, rows2, "Test 2: members for the King")):
    n_ = len(rows)
    for j, (lab_, c) in enumerate(rows):
        y = n_ - 1 - j; col = INK if c["p"] < 0.05 else GREY
        ax.plot([c["lo"], c["hi"]], [y, y], color=col, lw=1.8); ax.plot(c["b"], y, "o", color=col, ms=5.5)
    ax.axvline(0, color=RULE, lw=1.2, zorder=0)
    ax.set_yticks(range(n_)); ax.set_yticklabels([(lambda z: z[0].upper() + z[1:])(SHORT(l)) for l, _ in rows][::-1], fontsize=9.6)
    ax.set_title(nm, loc="left", fontsize=14, family=DISP, fontweight="bold", color=INK)
    ax.set_ylim(-0.7, n_ - 0.3)
foot(fig, "Dark: 95% interval excludes zero. Errors clustered by council (Test 1) or historic county (Test 2) unless stated. maps.tristanhotham.com/civil-war-leave")
out(fig, "forest")

# ---------- 6. county scatter: raw and adjusted
EW = A[A.share.notna()].copy()
COMP = ["pct_65plus", "pct_degree", "pct_noqual", "pct_routine", "pct_whitebrit", "pct_foreignborn", "pct_social", "pct_manuf", "pct_agri", "pct_mining", "pct_sick"]
EW["ldens"] = np.log(EW.density); EW["lcity"] = np.log1p(EW.km_city)
fl = "C(region) + cr(ldens, df=4, constraints='center') + lcity + " + " + ".join(COMP)
EW["ry"] = smf.ols(f"leave ~ {fl}", EW).fit().resid
EW["rx"] = smf.ols(f"x2 ~ {fl}", EW).fit().resid
cl = EW.groupby("hcounty").agg(leave=("leave", "mean"), x2=("x2", "first"), ry=("ry", "mean"), rx=("rx", "mean"), n=("code", "size"),
                               wales=("country", lambda s: (s == "Wales").mean() > 0.5)).reset_index()
fig = plt.figure(figsize=(12.5, 6.8))
title(fig, "Royalist counties and the Leave vote", "Each dot is a historic county (size = seats today). Left: raw. Right: after region, density and 2011 census composition")
for i, (xc, yc, xl, yl) in enumerate((("x2", "leave", "Members of 1640 who joined the King (%)", "Mean estimated Leave share (%)"),
                                      ("rx", "ry", "Royalist share, adjusted (points)", "Leave share, adjusted (points)"))):
    ax = fig.add_axes([0.07 + 0.49 * i, 0.19, 0.41, 0.59])
    ax.scatter(cl[xc], cl[yc], s=12 + 5 * cl.n, c=np.where(cl.wales, PARL, OCHRE), alpha=0.75, edgecolor="white", lw=0.6)
    m = np.polyfit(cl[xc], cl[yc], 1, w=np.sqrt(cl.n)); xx = np.linspace(cl[xc].min(), cl[xc].max(), 10)
    ax.plot(xx, np.polyval(m, xx), color=INK, lw=1.5)
    for r in cl.itertuples():
        labs = ("Middlesex", "Essex", "Cornwall", "Somerset", "Westmorland", "Yorkshire", "Lincolnshire", "Kent", "Lancashire") if i == 0 else ("Lincolnshire", "Somerset", "Westmorland", "Cornwall")
        if r.hcounty in labs:
            xv = getattr(r, xc); right = xv > cl[xc].quantile(0.9)
            ax.annotate(r.hcounty, (xv, getattr(r, yc)), xytext=(-6 if right else 5, 4), textcoords="offset points", fontsize=9, color=INK, ha="right" if right else "left", path_effects=HALO)
    ax.set_xlabel(xl, fontsize=10.5); ax.set_ylabel(yl, fontsize=10.5)
fig.legend(handles=[Line2D([], [], marker="o", ls="", color=OCHRE, label="English county"), Line2D([], [], marker="o", ls="", color=PARL, label="Welsh county")],
           loc="upper right", bbox_to_anchor=(0.97, 0.86), frameon=False, fontsize=10, ncol=2)
foot(fig, f"Seat-level model (main): {t2['main']['b']:+.2f} points of Leave per 10 points of royalist share, 95% interval {t2['main']['lo']:.2f} to {t2['main']['hi']:.2f};\n"
          f"wild cluster bootstrap p = {t2['wild']['p']:.2f}. Lines: weighted fits through the county means. maps.tristanhotham.com/civil-war-leave")
out(fig, "county")

# ---------- header 1200 x 630
fig = plt.figure(figsize=(12, 6.3), dpi=100)
ax = fig.add_axes([0.52, 0.02, 0.46, 0.96]); mapax(ax)
S.plot(ax=ax, column="leave", cmap=LEAVE, norm=LNORM, edgecolor="white", linewidth=0.12)
LINE_G.plot(ax=ax, color=INK, linewidth=2.6)
bo_k = bo[bo.share >= 0.5]
fig.text(0.05, 0.86, "DATA STUDY · 2026", fontsize=12, family=MONO, color=MUT)
fig.text(0.05, 0.80, "Roundhead or Cavalier,", fontsize=33, family=DISP, fontweight="bold", color=INK, va="top")
fig.text(0.05, 0.69, "Leave or Remain?", fontsize=33, family=DISP, fontweight="bold", color=KING, va="top")
fig.text(0.05, 0.53, "The Danelaw line and the sides of 1642\nset against the 2016 vote, seat by seat,\nonce today's places are compared like with like.",
         fontsize=15, color=INK, va="top", linespacing=1.45)
fig.text(0.05, 0.25, f"Danelaw gap: {x['t1_raw']:+.1f} points raw, {x['t1_main']:+.1f} adjusted", fontsize=13, family=MONO, color=INK)
fig.text(0.05, 0.19, f"Royalist counties: {x['t2_main']:+.2f} per 10 points, fragile", fontsize=13, family=MONO, color=INK)
fig.text(0.05, 0.07, "Dr Tristan Hotham · maps.tristanhotham.com/civil-war-leave", fontsize=10.5, family=MONO, color=MUT)
fig.savefig(f"{ROOT}/header.png", dpi=100, facecolor=PAPER)
plt.close(fig)
assert Image.open(f"{ROOT}/header.png").size == (1200, 630)
print("figures done", sorted(os.listdir(IMG)), sorted(f for f in os.listdir(BLOG) if f.startswith("b_")))
