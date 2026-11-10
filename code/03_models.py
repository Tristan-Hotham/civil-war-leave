"""Step 3. The planned models (NOTES.md section 0): Test 1 (Danelaw) and Test 2 (Long Parliament allegiance), with every
planned robustness check, placebo and the boundary design. Writes data/analysis.csv (the analysis frame),
data/results_models.json and data/model_tables.json.
"""
import warnings
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from common import *

warnings.filterwarnings("ignore")
rng = np.random.default_rng(SEED)

# ------------------------------------------------------------------------------------------------ analysis frame
B = pd.read_csv(f"{BL}/constituencies.csv")
G = pd.read_csv(f"{DATA}/seat_geo.csv").drop(columns=["name", "country", "region"])
CA = pd.read_csv(f"{DATA}/county_allegiance.csv")
LP = pd.read_csv(f"{DATA}/lp1640_constituencies.csv")
D0 = B.merge(G, on="code", how="inner")
assert len(D0) == 573
D0 = D0.merge(CA[["county", "share", "share_4244", "share_mech", "seats", "royalist"]].rename(columns={"county": "hcounty", "seats": "c_seats", "royalist": "c_royalist"}), on="hcounty", how="left")
D0["ldens"] = np.log(D0.density)
D0["lcity"] = np.log1p(D0.km_city)
D0["dens_dec"] = pd.qcut(D0.density, 10, labels=False)
D0["side"] = (D0.sdist_km > 0).astype(int)
D0["x2"] = D0.share * 100
D0["x2_4244"] = D0.share_4244 * 100
D0["x2_mech"] = D0.share_mech * 100
D0["x2_maj"] = (D0.share > 0.5).astype(int)
D0["london"] = (D0.region == "London").astype(int)
D0["dl_area"] = D0.dl_area_share * 100

# seat-level (exploratory C2): boroughs of 1640 inside each 2010 seat
import geopandas as gpd
from shapely.geometry import Point
from pyproj import Transformer
TO_BNG = Transformer.from_crs(4326, 27700, always_xy=True)
SG = gpd.read_file(f"{SCR}/seats_27700.gpkg")
bor = LP[LP.kind == "borough"].copy()
bx, by = TO_BNG.transform(bor.lon.values, bor.lat.values)
BG = gpd.GeoDataFrame(bor[["constituency", "county", "seats", "royalist"]], geometry=gpd.points_from_xy(bx, by), crs=27700)
jb = gpd.sjoin(BG, SG, how="left", predicate="within")
miss = jb.code.isna()
for i in jb.index[miss]:
    jb.loc[i, "code"] = SG.loc[SG.distance(jb.geometry[i]).idxmin(), "code"]
sb = jb.groupby("code").agg(b_n=("constituency", "size"), b_seats=("seats", "sum"), b_roy=("royalist", "sum"), b_names=("constituency", lambda s: "; ".join(s)))
D0 = D0.join(sb, on="code")
D0["b_n"] = D0.b_n.fillna(0).astype(int)
D0["x3"] = np.where(D0.b_n > 0, 100 * D0.b_roy / D0.b_seats, np.nan)
D0.to_csv(f"{DATA}/analysis.csv", index=False)

COMP = ["pct_65plus", "pct_degree", "pct_noqual", "pct_routine", "pct_whitebrit", "pct_foreignborn", "pct_social",
        "pct_manuf", "pct_agri", "pct_mining", "pct_sick"]
RUR = "cr(ldens, df=4, constraints='center') + lcity"
CTRL = f"{RUR} + " + " + ".join(COMP)
FULL = f"C(region) + {CTRL}"
EN = D0[D0.country == "England"].copy()
EW = D0[D0.hcounty.notna() & D0.share.notna()].copy()
R = {"n": {"england": int(len(EN)), "ew": int(len(D0)), "ew_test2": int(len(EW)), "durham_missing": int(D0.share.isna().sum()),
           "lads_en": int(EN.lad.nunique()), "counties_test2": int(EW.hcounty.nunique()), "danelaw": int(EN.danelaw.sum()),
           "not_danelaw": int((EN.danelaw == 0).sum())}}
TAB = {}


def fit(formula, data, cluster="lad", weights=None):
    d = data.copy()
    m = smf.wls(formula, d, weights=d[weights]) if weights is not None else smf.ols(formula, d)
    res0 = m.fit()
    idx = res0.model.data.row_labels
    g = pd.factorize(d.loc[idx, cluster])[0]
    return m.fit(cov_type="cluster", cov_kwds={"groups": g}), len(idx), len(np.unique(g))


def coef(res, n, ng, var, scale=1.0, sd=None):
    b, se = res.params[var], res.bse[var]
    q = stats.t.ppf(0.975, ng - 1)
    out = {"b": b * scale, "se": se * scale, "lo": (b - q * se) * scale, "hi": (b + q * se) * scale,
           "p": float(2 * stats.t.sf(abs(b / se), ng - 1)), "n": int(n), "clusters": int(ng), "r2": float(res.rsquared)}
    if sd is not None:
        out.update(b_sd=b * sd, lo_sd=(b - q * se) * sd, hi_sd=(b + q * se) * sd)
    return out


def table(res, name, keep=None):
    rows = []
    for k in res.params.index:
        if keep and not any(k.startswith(p) for p in keep):
            continue
        rows.append({"term": k, "b": float(res.params[k]), "se": float(res.bse[k]), "p": float(res.pvalues[k])})
    TAB[name] = {"rows": rows, "n": int(res.nobs), "r2": float(res.rsquared), "r2_adj": float(res.rsquared_adj)}


def tost(c, sesoi, ng):
    b, se = c["b"], c["se"]
    q90 = stats.t.ppf(0.95, ng - 1)
    p = max(stats.t.sf((b + sesoi) / se, ng - 1), stats.t.cdf((b - sesoi) / se, ng - 1))
    return {"sesoi": sesoi, "lo90": b - q90 * se, "hi90": b + q90 * se, "p": float(p), "equivalent": bool(p < 0.05)}


def conley(res, data, var, kms=(50, 100), scale=1.0):
    X = res.model.exog; e = res.resid.values; ix = list(res.model.exog_names).index(var)
    xy = data.loc[res.model.data.row_labels, ["cx", "cy"]].values
    dist = np.sqrt(((xy[:, None, :] - xy[None, :, :]) ** 2).sum(-1))
    bread = np.linalg.inv(X.T @ X); u = X * e[:, None]
    out = {}
    for km in kms:
        K = (dist <= km * 1000).astype(float)
        V = bread @ (u.T @ K @ u) @ bread
        se = float(np.sqrt(V[ix, ix])); b = float(res.params[var])
        out[str(km)] = {"b": b * scale, "se": se * scale, "lo": (b - 1.96 * se) * scale, "hi": (b + 1.96 * se) * scale,
                        "p": float(2 * stats.norm.sf(abs(b / se))), "n": int(len(e))}
    return out


def wild(formula_full, formula_r, data, var, cluster, B=9999):
    """Wild cluster bootstrap p-value (restricted, Webb six-point weights) for var, CR1 t-statistics."""
    m = smf.ols(formula_full, data).fit()
    idx = m.model.data.row_labels
    X = m.model.exog; y = m.model.endog; n, k = X.shape
    g = pd.factorize(data.loc[idx, cluster])[0]; G_ = g.max() + 1
    mr = smf.ols(formula_r, data.loc[idx]).fit()
    fit_r, e_r = mr.fittedvalues.values, mr.resid.values
    XtXi = np.linalg.inv(X.T @ X); ix = list(m.model.exog_names).index(var)
    a = XtXi[ix]                                                     # row giving beta_var = a @ X' y
    h = X @ a                                                         # beta_var = h @ y
    S = np.zeros((G_, n)); S[g, np.arange(n)] = 1
    adj = G_ / (G_ - 1) * (n - 1) / (n - k)

    def tstat(Y):                                                     # Y: n x B
        bb = h @ Y
        E = Y - X @ (XtXi @ (X.T @ Y))
        sg = S @ (h[:, None] * E)
        return bb / np.sqrt(adj * (sg ** 2).sum(0))
    t0 = float(tstat(y[:, None])[0])
    W6 = np.array([-np.sqrt(1.5), -1, -np.sqrt(0.5), np.sqrt(0.5), 1, np.sqrt(1.5)])
    ts = []
    for chunk in range(0, B, 1000):
        nb = min(1000, B - chunk)
        w = W6[rng.integers(0, 6, (G_, nb))]
        Ys = fit_r[:, None] + e_r[:, None] * w[g]
        ts.append(tstat(Ys))
    ts = np.concatenate(ts)
    return {"t": t0, "p": float((np.abs(ts) >= abs(t0)).mean()), "draws": int(B), "clusters": int(G_)}


# ============================================================================================ TEST 1: Danelaw
SD = {"leave_en": float(EN.leave.std()), "leave_ew": float(EW.leave.std()), "x2": float(EW.x2.std()), "scand": float(EN.scand_share.std())}
R["sd"] = SD
R["desc1"] = {"leave_mean_en": float(EN.leave.mean()), "leave_dl": float(EN[EN.danelaw == 1].leave.mean()),
              "leave_nodl": float(EN[EN.danelaw == 0].leave.mean())}
R["desc1"]["raw_gap"] = R["desc1"]["leave_dl"] - R["desc1"]["leave_nodl"]
# by region: Danelaw and not (descriptive)
rg = EN.groupby(["region", "danelaw"]).leave.agg(["mean", "size"]).unstack()
R["by_region"] = [{"region": r, "dl_mean": None if pd.isna(rg.loc[r, ("mean", 1)]) else float(rg.loc[r, ("mean", 1)]),
                   "nodl_mean": None if pd.isna(rg.loc[r, ("mean", 0)]) else float(rg.loc[r, ("mean", 0)]),
                   "dl_n": int(0 if pd.isna(rg.loc[r, ("size", 1)]) else rg.loc[r, ("size", 1)]),
                   "nodl_n": int(0 if pd.isna(rg.loc[r, ("size", 0)]) else rg.loc[r, ("size", 0)])} for r in rg.index]
R["regions_split"] = [r["region"] for r in R["by_region"] if r["dl_n"] > 0 and r["nodl_n"] > 0]

L1 = {}
for name, rhs in (("M1", "danelaw"), ("M2", "danelaw + C(region)"), ("M3", f"danelaw + C(region) + {RUR}"), ("M4", f"danelaw + {FULL}")):
    res, n, ng = fit(f"leave ~ {rhs}", EN)
    L1[name] = coef(res, n, ng, "danelaw")
    table(res, "T1_" + name, keep=["danelaw", "cr(", "lcity"] + COMP)
    if name == "M4":
        RES1 = res
R["t1"] = {"ladder": L1, "main": L1["M4"], "tost": tost(L1["M4"], 1.0, L1["M4"]["clusters"])}
R["t1"]["conley"] = conley(RES1, EN, "danelaw")
R["t1"]["pretreat"] = coef(*fit("leave ~ danelaw + C(region) + lcity", EN), "danelaw")

# ---- boundary design
def rd(data, bw=BW_MAIN, ctrl=True, kernel="uniform", seg=True, region=False, run="sdist_km", treat="side", cluster="lad", y="leave"):
    d = data[data[run].abs() <= bw].copy()
    d["T"] = d[treat]; d["r"] = d[run]
    rhs = "T + r + T:r"
    if seg: rhs += " + C(segment)"
    if region: rhs += " + C(region)"
    if ctrl: rhs += f" + {CTRL}"
    w = None
    if kernel == "triangular":
        d["w"] = 1 - d.r.abs() / bw; w = "w"
    res, n, ng = fit(f"{y} ~ {rhs}", d, cluster=cluster, weights=w)
    c = coef(res, n, ng, "T")
    c["n_in"] = int(d["T"].sum()); c["n_out"] = int((1 - d["T"]).sum())
    return c

RD = {}
RD["main"] = rd(EN)
RD["bw25"] = rd(EN, 25); RD["bw75"] = rd(EN, 75)
RD["tri"] = rd(EN, kernel="triangular")
RD["noctrl"] = rd(EN, ctrl=False)
RD["region"] = rd(EN, region=True)
RD["south"] = rd(EN[EN.lat < LAT_CUT])
# placebo lines
ne = EN[EN.sdist_km > 0].copy(); ne["pside"] = (ne.pl_ne_sdist > 0).astype(int)
sw = EN[EN.sdist_km < 0].copy(); sw["pside"] = (sw.pl_sw_sdist > 0).astype(int)
RD["placebo_ne"] = rd(ne, run="pl_ne_sdist", treat="pside")
RD["placebo_sw"] = rd(sw, run="pl_sw_sdist", treat="pside")
# Scandinavian names: does the line mark a jump in place-names? (validation)
RD["scand"] = rd(EN[EN.scand_share.notna()], ctrl=False, y="scand_share")
# covariate balance at the line (no controls)
BAL = {}
for v in ["ldens", "lcity"] + COMP:
    BAL[v] = rd(EN, ctrl=False, y=v)
    BAL[v]["sd"] = float(EN[EN.dist_km <= BW_MAIN][v].std())
    BAL[v]["b_std"] = BAL[v]["b"] / BAL[v]["sd"]
RD["balance"] = BAL
RD["balance_n_sig"] = int(sum(v["p"] < 0.05 for v in BAL.values()))
R["t1"]["rd"] = RD
# binned means for the figure (5 km bins, residualised on segment FE only, and raw)
bins = np.arange(-BW_MAIN, BW_MAIN + 0.1, 10)
d = EN[EN.dist_km <= BW_MAIN].copy()
d["bin"] = pd.cut(d.sdist_km, bins)
R["t1"]["rd_bins"] = [{"mid": float(iv.mid), "leave": float(g.leave.mean()), "n": int(len(g)), "scand": float(g.scand_share.mean())}
                      for iv, g in d.groupby("bin", observed=True)]

# ---- measurement checks and robustness (Test 1)
RB = {}
def rb(key, label, data, var="danelaw", formula=None, cluster="lad", scale=1.0, sd=None):
    res, n, ng = fit(formula or f"leave ~ {var} + {FULL}", data, cluster=cluster)
    c = coef(res, n, ng, var, scale=scale, sd=sd); c["label"] = label; RB[key] = c
rb("main", "Main specification (M4)", EN)
rb("area", "Exposure: share of seat area on the Danelaw side (per 10 points)", EN, var="dl_area", scale=10)
rb("shires", "Exposure: the 15 Danelaw shires of the medieval shire lists", EN, var="dane_shire")
rb("scand", "Exposure: Scandinavian place-name share (per 10 points)", EN[EN.scand_share.notna()], var="scand_share", scale=10, sd=SD["scand"])
rb("south", f"Seats south of {LAT_CUT} N only", EN[EN.lat < LAT_CUT])
rb("known", "Counted ward results only", EN[EN.leave_known])
rb("nolondon", "Drop London", EN[EN.region != "London"])
rb("decile", "Density decile fixed effects", EN, formula="leave ~ danelaw + C(region) + C(dens_dec) + lcity + " + " + ".join(COMP))
rb("ew", "England and Wales (Wales outside the Danelaw)", D0)
infl = RES1.get_influence().cooks_distance[0]
keep = RES1.model.data.row_labels[infl <= np.quantile(infl, 0.99)]
rb("cooks", "Drop top 1% Cook's distance", EN.loc[keep])
rb("cl_county", "Cluster by historic county", EN, cluster="hcounty")
R["t1"]["robust"] = RB
LORO = {}
for r in sorted(EN.region.unique()):
    res, n, ng = fit(f"leave ~ danelaw + {FULL}", EN[EN.region != r])
    try:
        LORO[r] = coef(res, n, ng, "danelaw")
    except KeyError:
        pass
R["t1"]["loro"] = LORO
R["t1"]["loro_range"] = {"min": min(v["b"] for v in LORO.values()), "max": max(v["b"] for v in LORO.values()),
                         "n_sig": int(sum(v["p"] < 0.05 for v in LORO.values())), "n": len(LORO)}
O1 = {}
for y, lab, dat in (("ukip15", "UKIP 2015", EN), ("brexit_19", "Brexit Party 2019 (seats contested)", EN[EN.brexit_stood]),
                    ("reform24", "Reform UK 2024 (approximate)", EN)):
    res, n, ng = fit(f"{y} ~ danelaw + {FULL}", dat)
    c = coef(res, n, ng, "danelaw"); c["label"] = lab; c["mean"] = float(dat[y].mean())
    c["raw"] = coef(*fit(f"{y} ~ danelaw", dat), "danelaw")
    O1[y] = c
R["t1"]["outcomes"] = O1

# ============================================================================================ TEST 2: allegiance
R["desc2"] = {"x2_mean": float(EW.x2.mean()), "x2_sd": SD["x2"], "leave_mean": float(EW.leave.mean()),
              "seats_majority_royalist": int(EW.x2_maj.sum())}
L2 = {}
for name, rhs in (("M1", "x2"), ("M2", "x2 + C(region)"), ("M3", f"x2 + C(region) + {RUR}"), ("M4", f"x2 + {FULL}")):
    res, n, ng = fit(f"leave ~ {rhs}", EW, cluster="hcounty")
    L2[name] = coef(res, n, ng, "x2", scale=10, sd=SD["x2"])
    table(res, "T2_" + name, keep=["x2", "cr(", "lcity"] + COMP)
    if name == "M4":
        RES2 = res
R["t2"] = {"ladder": L2, "main": L2["M4"]}
R["t2"]["tost"] = tost({"b": L2["M4"]["b_sd"], "se": L2["M4"]["se"] / 10 * SD["x2"]}, 1.0, L2["M4"]["clusters"])
R["t2"]["wild"] = wild(f"leave ~ x2 + {FULL}", f"leave ~ {FULL}", EW, "x2", "hcounty")
R["t2"]["wild_m2"] = wild("leave ~ x2 + C(region)", "leave ~ C(region)", EW, "x2", "hcounty")
R["t2"]["conley"] = conley(RES2, EW, "x2", scale=10)
# permutation: shuffle county values across counties
idx = RES2.model.data.row_labels
Z = RES2.model.exog; names = list(RES2.model.exog_names); ix = names.index("x2")
Zo = np.delete(Z, ix, axis=1); y = RES2.model.endog
Q, _ = np.linalg.qr(Zo)
yr = y - Q @ (Q.T @ y)
cty = EW.loc[idx, "hcounty"].values
cv = EW.drop_duplicates("hcounty").set_index("hcounty").x2
ucty = np.array(sorted(set(cty)))
vals = cv.loc[ucty].values
pos = np.searchsorted(ucty, cty)
def bperm(v):
    x = v[pos]; xr = x - Q @ (Q.T @ x)
    return float(xr @ yr / (xr @ xr))
b0 = bperm(vals)
perm = np.array([bperm(rng.permutation(vals)) for _ in range(5000)])
R["t2"]["perm"] = {"b": b0 * 10, "p": float((np.abs(perm) >= abs(b0)).mean()), "draws": 5000, "counties": int(len(ucty)),
                   "lo95_null": float(np.percentile(perm, 2.5) * 10), "hi95_null": float(np.percentile(perm, 97.5) * 10)}
RB2 = {}
def rb2(key, label, data, var="x2", formula=None, cluster="hcounty", scale=10.0, sd=None):
    res, n, ng = fit(formula or f"leave ~ {var} + {FULL}", data, cluster=cluster)
    c = coef(res, n, ng, var, scale=scale, sd=sd if sd is not None else (float(data[var].std()) if scale == 10 else None)); c["label"] = label; RB2[key] = c
rb2("main", "Main specification (M4)", EW, sd=SD["x2"])
rb2("england", "England only", EW[EW.country == "England"])
rb2("nolondon", "Drop London (Middlesex and Surrey seats in London)", EW[EW.region != "London"])
rb2("known", "Counted ward results only", EW[EW.leave_known])
rb2("x_4244", "Exposure: disablements dated 1642 to 1644 only", EW, var="x2_4244")
rb2("x_mech", "Exposure: every disablement, no hand decisions", EW, var="x2_mech")
rb2("x_maj", "Exposure: majority of the county's members royalist (0/1)", EW, var="x2_maj", scale=1.0)
rb2("cl_lad", "Cluster by local authority", EW, cluster="lad", sd=SD["x2"])
rb2("danelaw", "Adding the Danelaw indicator", EW, formula=f"leave ~ x2 + danelaw + {FULL}", sd=SD["x2"])
R["t2"]["robust"] = RB2
LORO2 = {}
for r in sorted(EW.region.unique()):
    res, n, ng = fit(f"leave ~ x2 + {FULL}", EW[EW.region != r], cluster="hcounty")
    LORO2[r] = coef(res, n, ng, "x2", scale=10)
R["t2"]["loro"] = LORO2
R["t2"]["loro_range"] = {"min": min(v["b"] for v in LORO2.values()), "max": max(v["b"] for v in LORO2.values()),
                         "n_sig": int(sum(v["p"] < 0.05 for v in LORO2.values())), "n": len(LORO2)}
LOCO = []
for c_ in ucty:
    res, n, ng = fit(f"leave ~ x2 + {FULL}", EW[EW.hcounty != c_], cluster="hcounty")
    cc = coef(res, n, ng, "x2", scale=10); cc["county"] = c_; LOCO.append(cc)
R["t2"]["loco_range"] = {"min": min(v["b"] for v in LOCO), "max": max(v["b"] for v in LOCO),
                         "min_county": min(LOCO, key=lambda v: v["b"])["county"], "max_county": max(LOCO, key=lambda v: v["b"])["county"],
                         "n_sig": int(sum(v["p"] < 0.05 for v in LOCO)), "n": len(LOCO)}
O2 = {}
for y_, lab, dat in (("ukip15", "UKIP 2015", EW), ("brexit_19", "Brexit Party 2019 (seats contested)", EW[EW.brexit_stood]),
                     ("reform24", "Reform UK 2024 (approximate)", EW)):
    res, n, ng = fit(f"{y_} ~ x2 + {FULL}", dat, cluster="hcounty")
    c = coef(res, n, ng, "x2", scale=10); c["label"] = lab; c["mean"] = float(dat[y_].mean())
    c["raw"] = coef(*fit(f"{y_} ~ x2", dat, cluster="hcounty"), "x2", scale=10)
    O2[y_] = c
R["t2"]["outcomes"] = O2
# exploratory C2: seats containing a 1640 borough
E3 = EW[EW.x3.notna()].copy()
R["t2"]["c2"] = coef(*fit(f"leave ~ x3 + {FULL}", E3), "x3", scale=10)
R["t2"]["c2"]["seats_with_borough"] = int(len(E3))
R["t2"]["c2_raw"] = coef(*fit("leave ~ x3", E3), "x3", scale=10)
# county-level view (descriptive): county mean Leave vs county royalist share
cl = EW.groupby("hcounty").agg(leave=("leave", "mean"), x2=("x2", "first"), seats=("code", "size"), region=("region", lambda s: s.mode()[0])).reset_index()
R["t2"]["county_corr"] = float(cl[["leave", "x2"]].corr().iloc[0, 1])
R["t2"]["county_corr_wt"] = None
cl.to_csv(f"{DATA}/county_level.csv", index=False)

# ============================================================================================ multiple tests
ps = sorted([("t1", R["t1"]["main"]["p"]), ("t2", R["t2"]["main"]["p"])], key=lambda z: z[1])
holm = {}
for i, (k, p) in enumerate(ps):
    holm[k] = min(1.0, max(p * (2 - i), holm.get(ps[i - 1][0], 0) if i else 0))
R["holm"] = holm
# minimum detectable effects (80% power, two-sided 5%) for the two main estimates
for k in ("t1", "t2"):
    m = R[k]["main"]; q = stats.t.ppf(0.975, m["clusters"] - 1) + stats.t.ppf(0.80, m["clusters"] - 1)
    R[k]["mde80"] = float(q * m["se"])
R["t2"]["mde80_sd"] = float(R["t2"]["mde80"] / 10 * SD["x2"])

jsave(R, f"{DATA}/results_models.json", indent=1)
jsave(TAB, f"{DATA}/model_tables.json", indent=1)
pr = lambda k, c: print(f"{k:34s} b={c['b']:+.3f} [{c['lo']:+.3f},{c['hi']:+.3f}] p={c['p']:.3f} n={c['n']} g={c.get('clusters')}")
print("desc1", R["desc1"])
for k, c in L1.items(): pr("T1 " + k, c)
print("TOST1", R["t1"]["tost"]); print("conley1", R["t1"]["conley"])
for k, c in RD.items():
    if k not in ("balance", "balance_n_sig"): pr("RD " + k, c)
print("balance sig", RD["balance_n_sig"], {k: round(v["b_std"], 2) for k, v in BAL.items()})
for k, c in RB.items(): pr("RB1 " + k, c)
print("LORO1", R["t1"]["loro_range"])
for k, c in O1.items(): pr("O1 " + k, c)
for k, c in L2.items(): pr("T2 " + k, c)
print("TOST2", R["t2"]["tost"], "wild", R["t2"]["wild"], R["t2"]["wild_m2"], "perm", R["t2"]["perm"])
for k, c in RB2.items(): pr("RB2 " + k, c)
print("LORO2", R["t2"]["loro_range"], "LOCO", R["t2"]["loco_range"])
for k, c in O2.items(): pr("O2 " + k, c)
pr("C2", R["t2"]["c2"]); print("holm", holm, "county corr", R["t2"]["county_corr"])
