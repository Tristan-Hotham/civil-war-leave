"""Step 7. The paper. Fills code/paper_template.tex from data/results.json and data/model_tables.json, adds booktabs tables,
compiles with xelatex + bibtex (code/refs.bib, plainnat author-year).
Output: release/paper/Hotham_Civil_War_Leave.pdf and .tex (+ refs.bib) beside the f_*.pdf figures.
The DOI stays a placeholder (https://doi.org/10.5281/zenodo.24104516 printed) unless DOI is set: DOI=10.5281/zenodo.N python3 code/07_paper.py"""
import shutil, subprocess
import numpy as np, pandas as pd
from common import *

R = jload(f"{DATA}/results.json")
TAB = jload(f"{DATA}/model_tables.json")
OUT = os.path.join(REL, "paper"); NAME = "Hotham_Civil_War_Leave"
tex = lambda s: str(s).replace("\\", "").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$")


def tfmt(v, f):
    if f == "int": return f"{int(round(float(v))):,}"
    if f in ("f0", "f1", "f2", "f3", "f4"): return f"{float(v):.{f[1]}f}"
    if f == "abs1": return f"{abs(float(v)):.1f}"
    if f == "pc": return f"{100 * float(v):.0f}\\%"
    return tex(str(v))


def star(p):
    return "^{***}" if p < 0.001 else "^{**}" if p < 0.01 else "^{*}" if p < 0.05 else ""


def tab(label, caption, cols, head, rows, note, size="\\footnotesize"):
    return (f"\\begin{{table}}[tbp]\\centering{size}\\caption{{{caption}}}\\label{{tab:{label}}}\\begin{{tabular}}{{{cols}}}\\toprule {head}\\\\\\midrule\n"
            + rows + f"\\bottomrule\\end{{tabular}}\\par\\vspace{{0.3em}}\\parbox{{0.92\\textwidth}}{{\\scriptsize {note}}}\\end{{table}}")


A = pd.read_csv(f"{DATA}/analysis.csv")
A["royal"] = A.share * 100; A["area"] = A.dl_area_share * 100
DV = [("leave", "Leave 2016, estimated (\\%)"), ("danelaw", "Danelaw side (0/1, England)"), ("area", "Seat area on the Danelaw side (\\%)"),
      ("sdist_km", "Signed distance to the line (km)"), ("dane_shire", "In the 15 Danelaw shires (0/1)"), ("scand_share", "Scandinavian name share (\\%)"),
      ("royal", "County members for the King (\\%)"), ("ukip15", "UKIP 2015 (\\%)"), ("reform24", "Reform UK 2024, mapped (\\%)"),
      ("density", "Persons per hectare"), ("km_city", "km to a city of 100,000+"), ("pct_65plus", "Aged 65+ (\\%)"), ("pct_degree", "Level 4 qualification (\\%)"),
      ("pct_noqual", "No qualifications (\\%)"), ("pct_routine", "Semi-routine and routine (\\%)"), ("pct_whitebrit", "White British (\\%)"),
      ("pct_foreignborn", "Born outside the UK (\\%)"), ("pct_social", "Social rented (\\%)"), ("pct_manuf", "Manufacturing (\\%)"),
      ("pct_agri", "Agriculture (\\%)"), ("pct_mining", "Mining (\\%)"), ("pct_sick", "Long-term sick (\\%)")]
EN = A[A.country == "England"]
rows = ""
for v, l in DV:
    d = EN if v in ("danelaw", "area", "sdist_km", "dane_shire", "scand_share") else A
    rows += f"{l} & {d[v].notna().sum():,} & {d[v].mean():.1f} & {d[v].std():.1f} & {d[v].min():.1f} & {d[v].max():.1f}\\\\\n"
T_DESC = tab("desc", "Descriptive statistics, 2010 constituencies of England and Wales (Danelaw measures: England).", "lrrrrr",
             "Variable & N & Mean & SD & Min & Max", rows, "Census variables from the 2011 census by 2010 constituency; Leave from Hanretty (2017). County members for the King: share of the historic county's members of 1640 later disabled for siding with the King (County Durham missing).")

lab = {"M1": "No controls", "M2": "Region FE", "M3": "Region FE + rurality", "M4": "+ composition (main)"}
L = R["t1"]["ladder"]
rows = "".join(f"{k} & {lab[k]} & ${L[k]['b']:.2f}{star(L[k]['p'])}$ & ({L[k]['se']:.2f}) & ({L[k]['lo']:.2f}, {L[k]['hi']:.2f}) & {L[k]['n']} & {L[k]['clusters']} & {L[k]['r2']:.2f}\\\\\n" for k in L)
T_T1 = tab("t1", "Test 1. Leave share and the Danelaw side of the line (England): model ladder.", "llrrrrrr",
           "Model & Controls & $\\beta$ (points) & SE & 95\\% CI & N & Clusters & $R^2$", rows,
           "OLS. Outcome: estimated Leave share (\\%). Exposure: at least half the seat's area on the Danelaw side. Rurality: natural cubic spline (4 df) of log density and log(1 + km to a city of 100,000+). Composition: the eleven census shares in Table~\\ref{tab:desc}. Standard errors clustered by local authority. $^{*}p<0.05$, $^{**}p<0.01$, $^{***}p<0.001$.")

RD = R["t1"]["rd"]
rl = [("main", "Main: 50 km, segment FE, controls"), ("bw25", "25 km"), ("bw75", "75 km"), ("tri", "Triangular kernel, 50 km"), ("noctrl", "No controls"),
      ("region", "Region FE in place of segment FE"), ("south", "South of 52.75 N only"), ("placebo_ne", "Placebo line 50 km north-east"),
      ("placebo_sw", "Placebo line 50 km south-west"), ("scand", "Outcome: Scandinavian name share (no controls)")]
rows = "".join(f"{l} & ${RD[k]['b']:.2f}{star(RD[k]['p'])}$ & ({RD[k]['lo']:.2f}, {RD[k]['hi']:.2f}) & {RD[k]['p']:.3f} & {RD[k]['n_in']} & {RD[k]['n_out']} & {RD[k]['clusters']}\\\\\n" for k, l in rl)
T_RD = tab("rd", "Boundary design: the jump in Leave share at the Danelaw line.", "lrrrrrr",
           "Specification & Jump & 95\\% CI & $p$ & Danelaw side & Other & Clusters", rows,
           "Local linear in signed distance with separate slopes each side, seats within the bandwidth of the land line (Lea to Chester), England. Line-segment fixed effects and the rurality and composition controls unless stated. Placebo lines: whole line translated 50 km perpendicular to its direction; only seats on the same side of the real line. Standard errors clustered by local authority.", size="\\scriptsize")

L = R["t2"]["ladder"]
rows = "".join(f"{k} & {lab[k]} & ${L[k]['b']:.3f}{star(L[k]['p'])}$ & ({L[k]['se']:.3f}) & ({L[k]['lo']:.2f}, {L[k]['hi']:.2f}) & {L[k]['b_sd']:.2f} & {L[k]['n']} & {L[k]['clusters']} & {L[k]['r2']:.2f}\\\\\n" for k in L)
w, w2, pm = R["t2"]["wild"], R["t2"]["wild_m2"], R["t2"]["perm"]
rows += f"\\midrule\\multicolumn{{9}}{{l}}{{Inference for the main model: wild cluster bootstrap $p$ = {w['p']:.3f} (M2: {w2['p']:.3f}); permutation $p$ = {pm['p']:.3f}; Holm-adjusted $p$ = {R['holm']['t2']:.3f}}}\\\\\n"
T_T2 = tab("t2", "Test 2. Leave share and the share of the county's members of 1640 who joined the King (England and Wales): model ladder.", "llrrrrrrr",
           "Model & Controls & $\\beta$ (per 10 pts) & SE & 95\\% CI & per SD & N & Clusters & $R^2$", rows,
           f"OLS, controls as in Table~\\ref{{tab:t1}} with Wales as a region. Standard errors clustered by historic county ({R['t2']['main']['clusters']} counties). Wild cluster bootstrap: Webb six-point weights, null imposed, {w['draws']:,} draws. Permutation: county values shuffled across counties, {pm['draws']:,} draws.", size="\\scriptsize")


def robtab(label, caption, RB, note, unit10=True):
    rows = ""
    for k, v in RB.items():
        rows += f"{tex(v['label'])} & ${v['b']:.3f}{star(v['p'])}$ & ({v['lo']:.2f}, {v['hi']:.2f}) & {v['p']:.3f} & {v['n']} & {v['clusters']}\\\\\n"
    return tab(label, caption, "p{7.4cm}rrrrr", "Specification & $\\beta$ & 95\\% CI & $p$ & N & Clusters", rows, note, size="\\scriptsize")

RB1 = dict(R["t1"]["robust"])
for k, v in R["t1"]["outcomes"].items():
    RB1["o_" + k] = dict(v, label="Outcome: " + v["label"])
T_ROB1 = robtab("rob1", "Test 1 robustness and measurement checks (all planned).", RB1,
                "Points of Leave for indicators; per 10 points for the area share and the Scandinavian name share. Standard errors clustered by local authority unless stated.")
RB2 = dict(R["t2"]["robust"])
RB2["c2"] = dict(R["t2"]["c2"], label="Exploratory: royalist share of a 1640 borough inside the seat (seats with one)")
for k, v in R["t2"]["outcomes"].items():
    RB2["o_" + k] = dict(v, label="Outcome: " + v["label"])
T_ROB2 = robtab("rob2", "Test 2 robustness checks (planned unless marked exploratory).", RB2,
                "Per 10 points of royalist share, except the majority indicator (points). Standard errors clustered by historic county unless stated; the exploratory borough measure by local authority.")

nm = {"danelaw": "Danelaw side (0/1)", "x2": "Royalist share (per point)", "lcity": "log(1 + km to city)", "pct_65plus": "Aged 65+", "pct_degree": "Level 4 qualification",
      "pct_noqual": "No qualifications", "pct_routine": "Semi-routine and routine", "pct_whitebrit": "White British", "pct_foreignborn": "Born outside UK",
      "pct_social": "Social rented", "pct_manuf": "Manufacturing", "pct_agri": "Agriculture", "pct_mining": "Mining", "pct_sick": "Long-term sick"}
term = lambda t: f"Density spline basis {t[-2]}" if t.startswith("cr(") else nm.get(t, tex(t))
cols = ["T1_M1", "T1_M2", "T1_M4", "T2_M1", "T2_M2", "T2_M4"]
terms = []
for c in ("T1_M4", "T2_M4"):
    for r in TAB[c]["rows"]:
        if r["term"] not in terms: terms.append(r["term"])
rows = ""
for t in terms:
    cells = []
    for m in cols:
        rr = {r["term"]: r for r in TAB[m]["rows"]}
        cells.append(f"${rr[t]['b']:.3f}{star(rr[t]['p'])}$ ({rr[t]['se']:.3f})" if t in rr else "")
    rows += f"{term(t)} & " + " & ".join(cells) + "\\\\\n"
rows += "\\midrule Region FE & no & yes & yes & no & yes & yes\\\\\n"
rows += "N & " + " & ".join(str(TAB[m]["n"]) for m in cols) + "\\\\\n"
rows += "$R^2$ & " + " & ".join(f"{TAB[m]['r2']:.3f}" for m in cols) + "\\\\\n"
T_FULL = tab("full", "Full coefficient tables (outcome: estimated Leave share, \\%).", "lrrrrrr", "Term & T1 M1 & T1 M2 & T1 M4 & T2 M1 & T2 M2 & T2 M4", rows,
             "Coefficients with clustered standard errors in brackets (Test 1 by local authority, Test 2 by historic county). The royalist share is per percentage point here. Census shares in percent. Intercept and region effects not shown.", size="\\tiny")
rows = ""
keys = sorted(set(R["t1"]["loro"]) | set(R["t2"]["loro"]))
for k in keys:
    a = R["t1"]["loro"].get(k); b = R["t2"]["loro"].get(k)
    ca = f"{a['b']:.2f} & ({a['lo']:.2f}, {a['hi']:.2f}) & {a['n']}" if a else "& &"
    cb = f"{b['b']:.3f} & ({b['lo']:.2f}, {b['hi']:.2f}) & {b['n']}" if b else "& &"
    rows += f"{tex(k)} & {ca} & {cb}\\\\\n"
T_LORO = tab("loro", "Leave-one-region-out: main specifications re-estimated without each region.", "lrrrrrr",
             "Region dropped & T1 $\\beta$ & 95\\% CI & N & T2 $\\beta$ (per 10 pts) & 95\\% CI & N", rows,
             "Test 1: England (regions without both sides still enter through the controls). Test 2: England and Wales.", size="\\scriptsize")
CA = pd.read_csv(f"{DATA}/county_allegiance.csv").sort_values("county")
cl = pd.read_csv(f"{DATA}/county_level.csv").set_index("hcounty")
rows = ""
for r in CA.itertuples():
    n10 = int(cl.loc[r.county, "seats"]) if r.county in cl.index else 0
    lv = f"{cl.loc[r.county, 'leave']:.1f}" if r.county in cl.index else ""
    rows += f"{tex(r.county)} & {r.nation} & {r.constituencies} & {r.seats} & {r.royalist} & {100 * r.share:.0f} & {r.royalist_4244} & {n10} & {lv}\\\\\n"
T_COUNTY = ("\\begin{scriptsize}\\begin{longtable}{llrrrrrrr}\\caption{Members of the Long Parliament elected in 1640 who joined the King, by historic county, and the 2010 seats in each county.}\\label{tab:county}\\\\\\toprule "
            "County & Nation & Constituencies & Seats & Royalist & \\% & 1642 to 1644 & Seats 2010 & Mean Leave\\\\\\midrule\\endhead\n" + rows +
            "\\bottomrule\\end{longtable}\\end{scriptsize}\n\\noindent{\\scriptsize Royalist: members disabled for siding with the King, with the hand decisions described in the text. County Durham returned no members in 1640. Seats 2010 and mean Leave: seats whose reference point lies in the rebuilt historic county.}")

t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
t = t.replace("{{AI}}", AI).replace("{{PAGE}}", PAGE).replace("{{REPO}}", REPO)
for k, v in (("TABLE_DESC", T_DESC), ("TABLE_T1", T_T1), ("TABLE_RD", T_RD), ("TABLE_T2", T_T2), ("TABLE_ROB1", T_ROB1), ("TABLE_ROB2", T_ROB2),
             ("TABLE_FULL", T_FULL), ("TABLE_LORO", T_LORO), ("TABLE_COUNTY", T_COUNTY)):
    t = t.replace("{{" + k + "}}", v)
t = re.sub(r"\{\{(?!TABLE_|DOI)([^}|]+)(\|(\w+))?\}\}", lambda m: tfmt(get(R, m.group(1)), m.group(3) or "raw"), t)
DOI = os.environ.get("DOI")
ph = f"\\url{{https://doi.org/{DOI}}}" if DOI else "\\{\\{DOI\\_URL\\}\\}"
t = t.replace("https://doi.org/10.5281/zenodo.00000000", ph)
assert "{{" not in t.replace("\\{\\{DOI", "") and "--" not in t and "—" not in t and "–" not in t, "placeholder or dash left"
assert "pre-registered" not in t.lower()
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
bib = open(os.path.join(ROOT, "code", "refs.bib"), encoding="utf-8").read().replace("--", "-")
open(os.path.join(OUT, "refs.bib"), "w", encoding="utf-8").write(bib)
run = lambda *a: subprocess.run(list(a), cwd=OUT, capture_output=True, text=True)
run("xelatex", "-interaction=nonstopmode", NAME + ".tex")
b = run("bibtex", NAME)
bbl = os.path.join(OUT, NAME + ".bbl")
s = open(bbl, encoding="utf-8").read().replace("--", "-")
open(bbl, "w", encoding="utf-8").write(s)
nref = s.count("\\bibitem")
for _ in range(2):
    r = run("xelatex", "-interaction=nonstopmode", NAME + ".tex")
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print("bibtex warnings:", [l for l in b.stdout.splitlines() if "Warning" in l][:10])
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l][:15])
for ext in (".aux", ".log", ".out", ".bbl", ".blg"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
body = txt.split("\nReferences\n")[0]
ab = re.search(r"Abstract\n(.*?)\nKeywords", txt, re.S)
print("paper", r.returncode, len(txt.split()), "words total;", len(body.split()), "before references;", [l for l in pages.splitlines() if l.startswith("Pages")],
      "refs", nref, "abstract words", len(ab.group(1).split()) if ab else None, "dashes:", txt.count("—") + txt.count("–"))
