"""Step 4. data/results.json (every number quoted anywhere) and the page data (data/web/*.geojson).
Merges data/results_models.json with the data checks and a few descriptive facts used in the copy."""
import numpy as np, pandas as pd, geopandas as gpd
from shapely.geometry import mapping
from common import *

R = jload(f"{DATA}/results_models.json")
R["geo"] = jload(f"{DATA}/geo_checks.json")
R["lp"] = jload(f"{DATA}/allegiance_checks.json")
A = pd.read_csv(f"{DATA}/analysis.csv")
CA = pd.read_csv(f"{DATA}/county_allegiance.csv")
LP = pd.read_csv(f"{DATA}/lp1640_constituencies.csv")
EN = A[A.country == "England"]

# descriptive facts for the copy
R["lp"]["royalist_pc"] = 100 * R["lp"]["royalist"] / R["lp"]["seats"]
R["lp"]["wales_pc"] = 100 * R["lp"]["wales_excl_monmouth_royalist"] / R["lp"]["wales_excl_monmouth_seats"]
R["lp"]["counties_none"] = sorted(CA[CA.royalist == 0].county.tolist())
R["lp"]["counties_all"] = sorted(CA[CA.share == 1].county.tolist())
R["lp"]["n_counties_none"] = len(R["lp"]["counties_none"]); R["lp"]["n_counties_all"] = len(R["lp"]["counties_all"])
R["lp"]["n_counties_majority"] = int((CA.share > 0.5).sum())
R["lp"]["n_counties_england"] = int((CA.nation == "England").sum())
R["lp"]["n_counties_wales"] = int((CA.nation == "Wales").sum())
for c in ("Cornwall", "Somerset", "Yorkshire", "Middlesex", "Essex", "Shropshire", "Lancashire", "Kent"):
    r = CA[CA.county == c].iloc[0]
    R["lp"].setdefault("county", {})[c] = {"seats": int(r.seats), "royalist": int(r.royalist), "pc": float(100 * r.share)}
R["lp"]["eng_share"] = float(100 * CA[CA.nation == "England"].royalist.sum() / CA[CA.nation == "England"].seats.sum())
R["geo"]["line_points"] = len(LINE)
R["geo"]["scand_inside_pc"] = 100 * R["geo"]["scand_inside"] / R["geo"]["scand_england"]
R["geo"]["scand_pc_england"] = 100 * R["geo"]["scand_england"] / R["geo"]["settlements_england"]
R["desc1"]["london_dl_names"] = sorted(EN[(EN.region == "London") & (EN.danelaw == 1)].name.tolist())
R["desc1"]["n_regions_split"] = len(R["regions_split"])
R["desc1"]["regions_all_in"] = [r["region"] for r in R["by_region"] if r["nodl_n"] == 0]
R["desc1"]["regions_all_out"] = [r["region"] for r in R["by_region"] if r["dl_n"] == 0]
R["desc1"]["dl_n"] = int(EN.danelaw.sum()); R["desc1"]["nodl_n"] = int((EN.danelaw == 0).sum())
# raw Leave by side for the 15 shires (descriptive)
R["desc1"]["shire_gap"] = float(EN[EN.dane_shire == 1].leave.mean() - EN[EN.dane_shire == 0].leave.mean())
# composition differences, Danelaw minus other side (England, raw means)
R["desc1"]["comp"] = {v: float(EN[EN.danelaw == 1][v].mean() - EN[EN.danelaw == 0][v].mean())
                      for v in ["pct_65plus", "pct_whitebrit", "pct_degree", "density", "km_city", "pct_foreignborn"]}
# county means (Test 2 sample) and Middlesex after adjustment
import statsmodels.formula.api as smf
EW = A[A.share.notna()].copy()
EW["ldens"] = np.log(EW.density); EW["lcity"] = np.log1p(EW.km_city)
COMP = ["pct_65plus", "pct_degree", "pct_noqual", "pct_routine", "pct_whitebrit", "pct_foreignborn", "pct_social", "pct_manuf", "pct_agri", "pct_mining", "pct_sick"]
EW["ry"] = smf.ols("leave ~ C(region) + cr(ldens, df=4, constraints='center') + lcity + " + " + ".join(COMP), EW).fit().resid
cm = EW.groupby("hcounty").agg(leave=("leave", "mean"), ry=("ry", "mean"))
R["t2"]["county_min_leave"] = cm.leave.idxmin(); R["t2"]["county_min_leave_pc"] = float(cm.leave.min())
R["t2"]["middlesex_adj"] = float(cm.loc["Middlesex", "ry"])
# convenience: rounded headline items used in short copy
t1, t2 = R["t1"], R["t2"]
R["x"] = {"t1_raw": R["desc1"]["raw_gap"], "t1_main": t1["main"]["b"], "t1_lo": t1["main"]["lo"], "t1_hi": t1["main"]["hi"],
          "t2_main": t2["main"]["b"], "t2_lo": t2["main"]["lo"], "t2_hi": t2["main"]["hi"], "t2_sd": t2["main"]["b_sd"],
          "t2_raw": t2["ladder"]["M1"]["b"], "t2_wild_p": t2["wild"]["p"], "share_explained": 100 * (1 - t1["main"]["b"] / R["desc1"]["raw_gap"])}
# robustness counts
rb1 = {k: v for k, v in t1["robust"].items() if k != "main"}
R["t1"]["robust_summary"] = {"n": len(rb1), "n_sig": int(sum(v["p"] < 0.05 for v in rb1.values())),
                             "sig": [v["label"] for v in rb1.values() if v["p"] < 0.05]}
rdk = ["main", "bw25", "bw75", "tri", "noctrl", "region", "south"]
R["t1"]["rd_summary"] = {"n": len(rdk), "n_sig": int(sum(t1["rd"][k]["p"] < 0.05 for k in rdk)),
                         "min": min(t1["rd"][k]["b"] for k in rdk), "max": max(t1["rd"][k]["b"] for k in rdk)}
rb2 = {k: v for k, v in t2["robust"].items() if k != "main"}
R["t2"]["robust_summary"] = {"n": len(rb2), "n_sig": int(sum(v["p"] < 0.05 for v in rb2.values())),
                             "notsig": [v["label"] for v in rb2.values() if v["p"] >= 0.05]}
jsave(R, f"{DATA}/results.json", indent=1)

# ------------------------------------------------------------------ page data
W = f"{DATA}/web"; os.makedirs(W, exist_ok=True)
S = gpd.read_file(f"{SCR}/seats_27700.gpkg").to_crs(4326)
S["geometry"] = S.geometry.simplify(0.0012, preserve_topology=True)
S = S.merge(A, on="code")
rnd = lambda c: [round(c[0], 4), round(c[1], 4)] if isinstance(c[0], float) else [rnd(x) for x in c]
num = lambda v, k=1: None if pd.isna(v) else round(float(v), k)
feats = []
for r in S.itertuples():
    gm = mapping(r.geometry)
    feats.append({"type": "Feature", "geometry": {"type": gm["type"], "coordinates": rnd(gm["coordinates"])},
                  "properties": {"c": r.code, "n": r.name, "rg": r.region, "lv": num(r.leave), "lk": bool(r.leave_known),
                                 "dl": int(r.danelaw), "da": num(100 * r.dl_area_share, 0), "sd": num(r.sdist_km, 0),
                                 "hc": r.hcounty, "rs": num(100 * r.share, 0) if not pd.isna(r.share) else None,
                                 "cr": None if pd.isna(r.c_royalist) else int(r.c_royalist), "cs": None if pd.isna(r.c_seats) else int(r.c_seats),
                                 "ds": int(r.dane_shire), "sc": num(r.scand_share, 1), "ns": int(r.n_settle), "nk": int(r.n_scand),
                                 "uk": num(r.ukip15), "rf": num(r.reform24), "bn": None if pd.isna(r.b_names) else r.b_names}})
jsave({"type": "FeatureCollection", "features": feats}, f"{W}/seats.geojson")
H = gpd.read_file(f"{HC}/historic_counties.geojson")
H["geometry"] = H.geometry.simplify(0.002, preserve_topology=True)
H = H.merge(CA[["county", "seats", "royalist", "share", "constituencies"]], on="county", how="left")
hf = []
for r in H.itertuples():
    gm = mapping(r.geometry)
    hf.append({"type": "Feature", "geometry": {"type": gm["type"], "coordinates": rnd(gm["coordinates"])},
               "properties": {"n": r.county, "s": None if pd.isna(r.seats) else int(r.seats), "r": None if pd.isna(r.royalist) else int(r.royalist),
                              "p": None if pd.isna(r.share) else round(100 * float(r.share)), "k": None if pd.isna(r.constituencies) else int(r.constituencies),
                              "lx": r.lx, "ly": r.ly}})
jsave({"type": "FeatureCollection", "features": hf}, f"{W}/counties.geojson")
bf = []
for r in LP[LP.kind == "borough"].itertuples():
    bf.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [round(r.lon, 4), round(r.lat, 4)]},
               "properties": {"n": r.constituency, "c": r.county, "s": int(r.seats), "r": int(r.royalist),
                              "m": r.members if isinstance(r.members, str) else "", "t": (r.notes if isinstance(r.notes, str) else "")[:240]}})
jsave({"type": "FeatureCollection", "features": bf}, f"{W}/boroughs.geojson")
import shutil
shutil.copy(f"{DATA}/danelaw_line.geojson", f"{W}/line.geojson")
print("results.json keys", list(R)); print("x", {k: round(v, 3) for k, v in R["x"].items()})
print("robust1", R["t1"]["robust_summary"], "rd", R["t1"]["rd_summary"], "robust2", R["t2"]["robust_summary"])
print("lp", {k: v for k, v in R["lp"].items() if k != "county"})
print({f: os.path.getsize(f"{W}/{f}") // 1024 for f in os.listdir(W)})
