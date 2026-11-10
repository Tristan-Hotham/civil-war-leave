"""Step 1. Geography: the Danelaw line and side, each seat's position relative to it, its historic county, and the share of
its settlements with Scandinavian name endings. No outcome is read here.

Writes data/seat_geo.csv (one row per 2010 seat in England and Wales), data/danelaw_line.geojson (line, Danelaw side,
placebo lines) and SCR/seats_27700.gpkg (simplified seat shapes for the figures and the page).
"""
import numpy as np, pandas as pd, geopandas as gpd
from shapely.geometry import LineString, Polygon, Point, mapping
from shapely.affinity import translate
from shapely.ops import unary_union
from pyproj import Transformer
from common import *

TO_BNG = Transformer.from_crs(4326, 27700, always_xy=True)
TO_LL = Transformer.from_crs(27700, 4326, always_xy=True)
bng = lambda pts: [TO_BNG.transform(x, y) for x, y in pts]

S = gpd.read_file(f"{RAW11}/wpc2010_gb.json")[["PCON13CD", "PCON13NM", "geometry"]].rename(columns={"PCON13CD": "code", "PCON13NM": "name"})
S = S[S.code.str[0].isin(["E", "W"])].to_crs(27700)
S["geometry"] = S.geometry.buffer(0)
C = pd.read_csv(f"{BL}/constituencies.csv", usecols=["code", "cx", "cy", "country", "region"]).rename(columns={"cx": "rx", "cy": "ry"})
S = S.merge(C, on="code", how="left")
assert S.rx.notna().all() and len(S) == 573, len(S)

# ---- the line and the Danelaw side
line_xy = bng([(p[0], p[1]) for p in LINE])
land_idx = [i for i, p in enumerate(LINE) if p[3] != "dee"] + [next(i for i, p in enumerate(LINE) if p[2].startswith("Chester"))]
land_idx = sorted(set(land_idx))
LAND = LineString([line_xy[i] for i in land_idx])                      # Lea mouth to Chester
FULL = LineString(line_xy)
side = Polygon(line_xy + bng(CLOSE)).buffer(0)          # line from the Lea mouth to the Dee, back round by sea
assert side.is_valid and side.area > 5e10
# check orientation: York must be inside, London Westminster (west of the Lea) and Oxford outside
for nm, lon, lat, want in (("York", -1.08, 53.96, True), ("Westminster", -0.13, 51.50, False), ("Oxford", -1.26, 51.75, False),
                           ("Colchester", 0.90, 51.89, True), ("Leicester", -1.13, 52.63, True), ("Coventry", -1.51, 52.41, False),
                           ("Stratford (east of the Lea)", 0.00, 51.54, True), ("Shrewsbury", -2.75, 52.71, False),
                           ("Stoke-on-Trent", -2.18, 53.00, True), ("Northampton", -0.90, 52.24, True), ("Daventry", -1.16, 52.26, False)):
    assert side.contains(Point(TO_BNG.transform(lon, lat))) == want, nm

# segments of the land line, for segment fixed effects in the boundary design
segs = {}
cur = None
for (lon, lat, nm, sg), xy in zip(LINE, line_xy):
    if sg == "dee" and not nm.startswith("Chester"):
        continue
    segs.setdefault(sg if sg != "dee" else "ws2", []).append(xy)
# make segments contiguous (share end points)
order = ["lea", "ouse", "ws1", "ws2"]
for a, b in zip(order[:-1], order[1:]):
    segs[b] = [segs[a][-1]] + segs[b]
SEG = {k: LineString(v) for k, v in segs.items()}

# ---- seat measures
ref = gpd.GeoSeries([Point(x, y) for x, y in zip(S.rx, S.ry)], crs=27700)
S["dl_area_share"] = [g.intersection(side).area / g.area for g in S.geometry]
S["danelaw"] = (S.dl_area_share >= 0.5).astype(int)
S["inside_ref"] = [side.contains(p) for p in ref]
S["dist_km"] = [LAND.distance(p) / 1000 for p in ref]
S["sdist_km"] = np.where(S.inside_ref, S.dist_km, -S.dist_km)
S["segment"] = [min(SEG, key=lambda k: SEG[k].distance(p)) for p in ref]
S["lat"] = [TO_LL.transform(x, y)[1] for x, y in zip(S.rx, S.ry)]
S["lon"] = [TO_LL.transform(x, y)[0] for x, y in zip(S.rx, S.ry)]
# England only for the Danelaw coding; Welsh seats are outside by construction (none should be inside)
assert (S[S.country == "Wales"].danelaw == 0).all()

# placebo lines: the whole line translated 50 km perpendicular to its general direction (Lea mouth to Chester)
a, b = np.array(line_xy[0]), np.array(line_xy[land_idx[-1]])
v = (b - a) / np.linalg.norm(b - a)
ne = np.array([-v[1], v[0]])
if ne[0] < 0:
    ne = -ne                                                             # point north-east (into the Danelaw)
assert side.contains(Point(*(np.array(LAND.interpolate(0.5, normalized=True).coords[0]) + 20000 * ne)))
PL = {}
for key, sgn in (("ne", 1), ("sw", -1)):
    dx, dy = sgn * SHIFT_KM * 1000 * ne
    side_p = translate(side, dx, dy)
    land_p = translate(LAND, dx, dy)
    ins = np.array([side_p.contains(p) for p in ref])
    d = np.array([land_p.distance(p) / 1000 for p in ref])
    S[f"pl_{key}_sdist"] = np.where(ins, d, -d)
    PL[key] = land_p

# ---- historic county of the seat reference point (rebuilt historic counties, enclosure study)
H = gpd.read_file(f"{HC}/historic_counties.geojson").to_crs(27700)
H["geometry"] = H.geometry.buffer(0)
pts = gpd.GeoDataFrame(S[["code"]].copy(), geometry=ref.values, crs=27700)
j = gpd.sjoin(pts, H[["county", "geometry"]], how="left", predicate="within").drop_duplicates("code")
S["hcounty"] = S.code.map(j.set_index("code").county)
miss = S.hcounty.isna()
for i in S.index[miss]:                                                 # coastal reference points just outside: nearest county
    p = ref[i] if i in ref.index else Point(S.rx[i], S.ry[i])
    S.loc[i, "hcounty"] = H.loc[H.distance(Point(S.rx[i], S.ry[i])).idxmin(), "county"]
n_hc_nearest = int(miss.sum())
# share of the seat's area in its main historic county (how cleanly the seat sits in one county)
ov = gpd.overlay(S[["code", "geometry"]].assign(geometry=S.geometry.simplify(50)), H[["county", "geometry"]], how="intersection", keep_geom_type=True)
ov["a"] = ov.area
tot = ov.groupby("code").a.sum()
best = ov.sort_values("a").groupby("code").tail(1).set_index("code")
S["hcounty_area"] = S.code.map(best.county)
S["hcounty_share"] = S.code.map(best.a / tot)
S["dane_shire"] = S.hcounty.isin(DANE_SHIRES).astype(int)
assert set(DANE_SHIRES) <= set(H.county), set(DANE_SHIRES) - set(H.county)

# ---- Scandinavian name endings among Wikidata settlements
g = pd.read_csv(f"{SETTLE}/uk_settlements.tsv", sep="\t", dtype=str, keep_default_na=False, quoting=3)
g.columns = ["item", "label", "coord", "pop", "type"]
g["label"] = g.label.str.replace(r'^"(.*)"@en$', r"\1", regex=True)
g["type"] = g.type.str.replace(r'^"(.*)"@en$', r"\1", regex=True)
KEEP_T = {"Village", "hamlet", "human settlement", "town", "market town", "city", "suburb", "locality", "deserted medieval village",
          "village", "civil parish", "big city", "cathedral city"}
g = g[g.type.isin(KEEP_T)]
xy = g.coord.str.extract(r"POINT\(([-\d.eE]+) ([-\d.eE]+)\)").astype(float)
g["lon"], g["lat"] = xy[0], xy[1]
g = g.dropna(subset=["lon"]).drop_duplicates("item")
NOT = {"abbey", "ruby", "lobby", "hobby", "baby", "derby road", "bobby"}


def scand(label):
    base = label.split(",")[0].split("(")[0].strip()
    for w in re.findall(r"[A-Za-z']+", base):
        lw = w.lower()
        if len(lw) < 4 or lw in NOT:
            continue
        if re.search(r"(thorpe|thorp|thwaite|thwaites|toft|tofts)$", lw):
            return 1
        if lw.endswith("by") and not lw.endswith("bby") and lw not in ("abby",):
            return 1
    return 0


g["scand"] = g.label.map(scand)
gx, gy = TO_BNG.transform(g.lon.values, g.lat.values)
G = gpd.GeoDataFrame(g[["item", "label", "scand"]], geometry=gpd.points_from_xy(gx, gy), crs=27700)
jj = gpd.sjoin(G, S[["code", "geometry"]], how="inner", predicate="within")
agg = jj.groupby("code").agg(n_settle=("scand", "size"), n_scand=("scand", "sum"))
S = S.join(agg, on="code")
S["n_settle"] = S.n_settle.fillna(0).astype(int)
S["n_scand"] = S.n_scand.fillna(0).astype(int)
S["scand_share"] = np.where(S.n_settle >= 5, 100 * S.n_scand / S.n_settle.clip(lower=1), np.nan)
eng = jj[jj.code.str[0] == "E"]
chk = {"seats": int(len(S)), "england": int((S.country == "England").sum()), "wales": int((S.country == "Wales").sum()),
       "danelaw_seats": int(S.danelaw.sum()), "danelaw_split_seats": int(((S.dl_area_share > 0.05) & (S.dl_area_share < 0.95)).sum()),
       "dane_shire_seats": int(S.dane_shire.sum()), "hc_nearest": n_hc_nearest,
       "hc_mismatch_ref_vs_area": int((S.hcounty != S.hcounty_area).sum()),
       "settlements_ew": int(len(jj)), "settlements_england": int(len(eng)), "scand_england": int(eng.scand.sum()),
       "scand_inside": int(eng[eng.code.isin(S[S.danelaw == 1].code)].scand.sum()),
       "seats_lt5_settle": int((S.n_settle < 5).sum()),
       "within_bw": int(((S.dist_km <= BW_MAIN) & (S.country == "England")).sum()),
       "line_km_land": round(LAND.length / 1000, 1), "line_km_treaty": round(LineString(line_xy[:19]).length / 1000, 1)}
print(chk)
print("examples of Scandinavian names:", eng[eng.scand == 1].label.sample(40, random_state=1).tolist())
jsave(chk, f"{DATA}/geo_checks.json", indent=1)
pd.DataFrame(eng[eng.scand == 1][["item", "label", "code"]]).to_csv(f"{SCR}/scand_names.csv", index=False)

# ---- outputs
cols = ["code", "name", "country", "region", "lon", "lat", "danelaw", "dl_area_share", "sdist_km", "dist_km", "segment",
        "pl_ne_sdist", "pl_sw_sdist", "hcounty", "hcounty_area", "hcounty_share", "dane_shire", "n_settle", "n_scand", "scand_share"]
out = S[cols].copy()
for c in ("dl_area_share", "hcounty_share"):
    out[c] = out[c].round(4)
for c in ("sdist_km", "dist_km", "pl_ne_sdist", "pl_sw_sdist", "scand_share"):
    out[c] = out[c].round(3)
out.lon, out.lat = out.lon.round(5), out.lat.round(5)
out.sort_values("code").to_csv(f"{DATA}/seat_geo.csv", index=False)
S[["code", "geometry"]].assign(geometry=S.geometry.simplify(60)).to_file(f"{SCR}/seats_27700.gpkg", driver="GPKG")

to_ll = lambda geom: __import__("shapely.ops", fromlist=["transform"]).transform(lambda x, y, z=None: TO_LL.transform(x, y), geom)
rnd = lambda c: [round(c[0], 4), round(c[1], 4)] if isinstance(c[0], float) else [rnd(x) for x in c]
feats = []
gm = mapping(to_ll(FULL)); feats.append({"type": "Feature", "properties": {"k": "line", "n": "The Danelaw line (treaty text, then Watling Street to Chester)"}, "geometry": {"type": gm["type"], "coordinates": rnd(gm["coordinates"])}})
for k, ln in PL.items():
    gm = mapping(to_ll(ln)); feats.append({"type": "Feature", "properties": {"k": f"placebo_{k}", "n": f"Placebo line, 50 km {k.upper()}"}, "geometry": {"type": gm["type"], "coordinates": rnd(gm["coordinates"])}})
ew = unary_union(list(S.geometry.simplify(200).buffer(300))).buffer(-300)
dl = to_ll(side.intersection(ew).simplify(400))
gm = mapping(dl); feats.append({"type": "Feature", "properties": {"k": "side", "n": "Danelaw side (England)"}, "geometry": {"type": gm["type"], "coordinates": rnd(gm["coordinates"])}})
pts_f = [{"type": "Feature", "properties": {"k": "pt", "n": p[2]}, "geometry": {"type": "Point", "coordinates": [p[0], p[1]]}} for p in LINE]
jsave({"type": "FeatureCollection", "features": feats + pts_f}, f"{DATA}/danelaw_line.geojson")
print("wrote seat_geo.csv", len(out))
