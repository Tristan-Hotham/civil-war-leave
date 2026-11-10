"""Reddit collage (r/dataisbeautiful style, light background).
Run from anywhere: python3 reddit/collage.py   Writes reddit/civil-war-leave_collage.png (2700 px wide)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
import numpy as np, pandas as pd, geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib import font_manager as fm
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from PIL import Image
from common import *

for f in ("SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf", "IBMPlexMono-Regular.ttf", "FrauncesVar.ttf"):
    fm.fontManager.addfont(f"{FONTS}/{f}")
INK, MUT, PAPER, SEA = "#22201c", "#6b655c", "#fbf8f2", "#e6ecec"
KING, PARL, OCHRE = "#9B2D30", "#4E7A63", "#B5651D"
plt.rcParams.update({"font.family": "Source Serif 4", "axes.unicode_minus": False})
DISP = fm.FontProperties(fname=f"{FONTS}/FrauncesVar.ttf", weight="black")
MONO = fm.FontProperties(fname=f"{FONTS}/IBMPlexMono-Regular.ttf")
LEAVE = LinearSegmentedColormap.from_list("lv", ["#1F4E79", "#7EA6C9", "#EEEAE2", "#E3A26B", "#9C4A12"])
ROY = LinearSegmentedColormap.from_list("ry", [PARL, "#A9C0B1", "#EFE7D6", "#D9958F", KING])
HALO = [pe.withStroke(linewidth=4, foreground=SEA)]
R = jload(f"{DATA}/results.json")
A = pd.read_csv(f"{DATA}/analysis.csv")
S = gpd.read_file(f"{SCR}/seats_27700.gpkg").merge(A[["code", "leave", "danelaw"]], on="code")
S["geometry"] = S.geometry.simplify(300)
L = gpd.read_file(f"{DATA}/danelaw_line.geojson").to_crs(27700)
LN = L[L.k == "line"]
CA = pd.read_csv(f"{DATA}/county_allegiance.csv")
H = gpd.read_file(f"{HC}/historic_counties.geojson").to_crs(27700).merge(CA, on="county", how="left")
H["geometry"] = H.geometry.simplify(400)
t1, t2, d1, lp, g = R["t1"], R["t2"], R["desc1"], R["lp"], R["geo"]

fig = plt.figure(figsize=(18, 13.5), dpi=150)
fig.patch.set_facecolor(PAPER)
fig.text(0.035, 0.955, "Roundhead or Cavalier, Leave or Remain?", fontproperties=DISP, fontsize=40, color=INK, va="top")
fig.text(0.035, 0.898, "Two old fault lines of England set against the 2016 referendum, by 2010 constituency in England and Wales",
         fontsize=17, color=MUT, va="top")

# --- big map: Leave + line
ax = fig.add_axes([0.02, 0.09, 0.47, 0.78]); ax.set_facecolor(SEA)
S.plot(ax=ax, column="leave", cmap=LEAVE, norm=Normalize(25, 75), edgecolor="white", linewidth=0.12)
LN.plot(ax=ax, color="white", linewidth=6); LN.plot(ax=ax, color=INK, linewidth=2.8)
ax.set_xlim(130000, 660000); ax.set_ylim(5000, 670000); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
for s_ in ax.spines.values(): s_.set_visible(False)
ax.set_xlabel(""); ax.set_ylabel("")
ax.text(140000, 655000, "The Danelaw line", fontproperties=DISP, fontsize=20, color=INK, va="top", path_effects=HALO)
ax.text(140000, 622000, "Treaty of Alfred and Guthrum: up the\nThames and the Lea, straight to Bedford,\nup the Ouse to Watling Street; then\nthe usual line on to Chester", fontsize=12.5, color=INK, va="top", linespacing=1.4, path_effects=HALO)
ax.text(655000, 545000, f"Danelaw side\n{d1['leave_dl']:.1f}% Leave\n({d1['dl_n']} seats)", fontsize=14, color=INK, ha="right", va="center", fontweight="bold", path_effects=HALO)
ax.text(140000, 145000, f"Other side\n{d1['leave_nodl']:.1f}% Leave\n({d1['nodl_n']} seats)", fontsize=14, color=INK, ha="left", va="center", fontweight="bold", path_effects=HALO)
cax = fig.add_axes([0.035, 0.635, 0.15, 0.014])
cb = fig.colorbar(plt.cm.ScalarMappable(norm=Normalize(25, 75), cmap=LEAVE), cax=cax, orientation="horizontal", ticks=[25, 50, 75])
cb.ax.set_xticklabels(["25%", "50%", "75%"], fontsize=11); cb.outline.set_edgecolor(MUT)
cb.ax.set_title("Estimated Leave share, 2016", fontsize=12, color=INK, loc="left")

# --- Danelaw estimates
def bars(axb, rows, title, unit, xlim):
    axb.set_facecolor(PAPER)
    for i, (lab, c, col) in enumerate(rows):
        y = len(rows) - 1 - i
        axb.barh(y, c["b"], color=col, height=0.55)
        if "lo" in c:
            axb.plot([c["lo"], c["hi"]], [y, y], color=INK, lw=2)
        axb.text(max(c.get("hi", c["b"]), 0) + (xlim[1] - xlim[0]) * 0.02, y, f"{c['b']:+.2f}", va="center", fontsize=13, color=INK, fontweight="bold")
        axb.text(xlim[0], y + 0.42, lab, fontsize=12.5, color=INK, va="bottom", path_effects=[pe.withStroke(linewidth=5, foreground=PAPER)], zorder=5)
    axb.axvline(0, color=MUT, lw=1)
    axb.set_xlim(*xlim); axb.set_ylim(-0.6, len(rows) - 0.1); axb.set_yticks([])
    for s_ in ("top", "right", "left"): axb.spines[s_].set_visible(False)
    axb.tick_params(labelsize=11, colors=MUT); axb.set_xlabel(unit, fontsize=11.5, color=MUT)
    axb.set_title(title, loc="left", fontproperties=DISP, fontsize=19, color=INK, pad=12)

ab1 = fig.add_axes([0.53, 0.60, 0.42, 0.24])
bars(ab1, [("Raw gap, Danelaw side minus other side", {"b": d1["raw_gap"]}, OCHRE),
           ("Within the same region", t1["ladder"]["M2"], "#D9A066"),
           ("Same region, density and 2011 census profile", t1["main"], INK)],
     "Danelaw: the gap vanishes like for like", "points of Leave (lines: 95% intervals)", (-3, 14))
fig.text(0.53, 0.535, f"Yet the line is real: {g['scand_inside_pc']:.0f}% of the {g['scand_england']:,} English villages ending\n-by, -thorpe, -thwaite or -toft lie on the Danelaw side.",
         fontsize=13, color=INK, va="top", linespacing=1.4)

# --- Civil War: small map + estimates
am = fig.add_axes([0.53, 0.07, 0.19, 0.38]); am.set_facecolor(SEA)
H.plot(ax=am, column="share", cmap=ROY, vmin=0, vmax=1, edgecolor="white", linewidth=0.4, missing_kwds={"color": "#ddd8cc"})
am.set_xlim(150000, 660000); am.set_ylim(5000, 670000); am.set_aspect("equal"); am.set_xticks([]); am.set_yticks([])
for s_ in am.spines.values(): s_.set_visible(False)
am.set_xlabel(""); am.set_ylabel("")
am.text(160000, 655000, "Members of 1640\nwho joined the King", fontsize=12, color=INK, va="top", fontweight="bold", path_effects=HALO)
cax2 = fig.add_axes([0.545, 0.085, 0.15, 0.011])
cb2 = fig.colorbar(plt.cm.ScalarMappable(norm=Normalize(0, 100), cmap=ROY), cax=cax2, orientation="horizontal", ticks=[0, 50, 100])
cb2.ax.set_xticklabels(["none", "half", "all"], fontsize=10.5); cb2.outline.set_edgecolor(MUT)
ab2 = fig.add_axes([0.75, 0.12, 0.22, 0.22])
bars(ab2, [("Raw", t2["ladder"]["M1"], "#D9958F"), ("Same region", t2["ladder"]["M2"], "#C9A9A6"), ("Like for like (main)", t2["main"], INK)],
     "Civil War: small and fragile", "points of Leave per 10 points\nmore royalist members", (-1.6, 2.9))
fig.text(0.75, 0.47, f"{lp['royalist']} of {lp['seats']} seats elected in 1640\nhad members who later sided\nwith the King. Main estimate:\nwild bootstrap p = {t2['wild']['p']:.2f}.",
         fontsize=12.5, color=INK, va="top", linespacing=1.4)

fig.text(0.035, 0.022, "Data: Leave estimates by 2010 constituency, Hanretty (2017); 2011 census (ONS, OGL); boundaries ONS/OS (OGL); List of MPs elected to the English Parliament in 1640, Wikipedia (CC BY-SA 4.0);\n"
         "Wikidata (CC0). Like for like: OLS with region fixed effects, density and 11 census measures; plan written before the analysis.  Dr Tristan Hotham  ·  maps.tristanhotham.com/civil-war-leave",
         fontproperties=MONO, fontsize=10.5, color=MUT, va="bottom", linespacing=1.5)
out = os.path.join(ROOT, "reddit", f"{SLUG}_collage.png")
fig.savefig(out, dpi=150, facecolor=PAPER)
plt.close(fig)
im = Image.open(out); print(out, im.size)
assert im.size[0] >= 2400
