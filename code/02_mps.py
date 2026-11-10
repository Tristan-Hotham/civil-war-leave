"""Step 2. Civil War allegiance from the Long Parliament member lists (no outcome is read here).

From the wikitext of "List of MPs elected to the English Parliament in 1640 (November)" (lp1640): one row per
constituency with its county section, the members returned in 1640, and the notes column. A member is coded as having
joined the King when the notes say he was "disabled" (the Commons' term for members barred from sitting for adhering to
the King, 1642 to 1644 in most cases), counting replacements elected before the war; hand exceptions are in
code/allegiance_overrides.csv (members disabled for reasons other than royalism). Pre-war expulsions (monopolists, the
Army Plot) are not counted as royalist; a sensitivity version counts only disablements dated 1642 to 1644.

Writes data/lp1640_constituencies.csv (one row per 1640 constituency, with every parsing decision) and
data/county_allegiance.csv (per historic county: seats, royalist members, share).
"""
import numpy as np, pandas as pd
from common import *

W = jload(f"{RAW13}/wiki_pages.json")
t = W["lp1640"]
body = t[t.find('{| class="wikitable"'):]

SEC = {"Kent (see also Cinque Ports)": "Kent", "Sussex - see also Cinque Ports": "Sussex", "Salop": "Shropshire",
       "Westmorland": "Westmorland"}
CINQUE = {"Hastings": "Sussex", "Rye": "Sussex", "Winchelsea": "Sussex", "Seaford": "Sussex", "Sandwich": "Kent", "Dover": "Kent",
          "Hythe": "Kent", "Romney": "Kent", "New Romney": "Kent"}
WALES = {"Anglesey": "Anglesey", "Beaumaris": "Anglesey", "Brecknockshire": "Brecknockshire", "Brecknock": "Brecknockshire",
         "Brecon": "Brecknockshire", "Cardiganshire": "Cardiganshire", "Cardigan": "Cardiganshire", "Carmarthenshire": "Carmarthenshire",
         "Carmarthen": "Carmarthenshire", "Carnarvonshire": "Caernarfonshire", "Caernarvonshire": "Caernarfonshire",
         "Carnarvon": "Caernarfonshire", "Caernarvon": "Caernarfonshire", "Denbighshire": "Denbighshire", "Denbigh": "Denbighshire",
         "Denbigh Boroughs": "Denbighshire", "Flintshire": "Flintshire", "Flint": "Flintshire", "Flint Boroughs": "Flintshire",
         "Glamorgan": "Glamorgan", "Glamorganshire": "Glamorgan", "Cardiff": "Glamorgan", "Merioneth": "Merionethshire",
         "Merionethshire": "Merionethshire", "Montgomeryshire": "Montgomeryshire", "Montgomery": "Montgomeryshire",
         "Pembrokeshire": "Pembrokeshire", "Pembroke": "Pembrokeshire", "Haverfordwest": "Pembrokeshire", "Haverford West": "Pembrokeshire",
         "Radnorshire": "Radnorshire", "Radnor": "Radnorshire", "New Radnor": "Radnorshire"}
OV = pd.read_csv(os.path.join(ROOT, "code", "allegiance_overrides.csv"), comment="#")
ov_minus = OV.groupby("constituency").minus.sum().to_dict()
ov_plus = OV.groupby("constituency").plus.sum().to_dict()

rows, sec = [], None
for chunk in body.split("\n|-"):
    m = re.search(r"===([^=]+)===", chunk)
    if m:
        sec = m.group(1).strip()
        continue
    if "!Constituency" in chunk or not chunk.strip() or chunk.strip().startswith("|}"):
        continue
    cells = [c for c in re.split(r"\n\|(?!\})", "\n" + chunk.strip("\n")) if c.strip()]
    cells = [c.strip() for c in cells]
    if len(cells) < 2:
        continue
    raw_name = cells[0]
    lk = re.search(r"\[\[([^|\]]+)", raw_name)
    target = re.sub(r"\s*\((UK|English|England)?\s*Parliament constituency\)", "", lk.group(1)).strip() if lk else wl(raw_name)
    name = wl(raw_name).split("|")[-1].strip()
    members = [wl(x) for x in re.split(r"<br\s*/?>", cells[1], flags=re.I) if wl(x).strip(" .")]
    notes_raw = cells[2] if len(cells) > 2 else ""
    notes = wl(re.sub(r"<br\s*/?>", "; ", notes_raw, flags=re.I)).replace("\n", " ")
    # count disabled members: clause by clause
    n_dis, n_dis_4244, n_dis_late = 0, 0, 0
    for cl in re.split(r";|\.\s|:|(?<=\d{4})\s+(?=[A-Z])", notes):
        if "disabled" not in cl.lower():
            continue
        pre = cl.lower().split("disabled")[0]
        k = 2 if (re.search(r"\bboth\b", cl.lower()) or re.search(r"\w \band\b \w", pre)) else 1
        n_dis += k
        yrs = [int(y) for y in re.findall(r"\b(16[4-5]\d)\b", cl.lower().split("disabled", 1)[1][:40])]
        if not yrs or yrs[0] <= 1644:
            n_dis_4244 += k
        else:
            n_dis_late += k
    county = SEC.get(sec, sec)
    if sec == "Cinque Ports":
        county = CINQUE.get(name, CINQUE.get(target, "Kent"))
    if sec == "Wales":
        county = WALES.get(name, WALES.get(target))
    rows.append({"section": sec, "county": county, "constituency": name, "link": target, "n_members": len(members),
                 "members": "; ".join(members), "notes": notes, "n_disabled_raw": n_dis, "n_disabled_4244_raw": n_dis_4244,
                 "n_disabled_late_raw": n_dis_late})
D = pd.DataFrame(rows)
assert D.county.notna().all(), D[D.county.isna()]
D["override_minus"] = D.constituency.map(ov_minus).fillna(0).astype(int)
D["override_plus"] = D.constituency.map(ov_plus).fillna(0).astype(int)
assert set(OV.constituency) <= set(D.constituency), set(OV.constituency) - set(D.constituency)
D["seats"] = D.n_members.clip(lower=1)
D["royalist"] = (D.n_disabled_raw - D.override_minus + D.override_plus).clip(lower=0).clip(upper=D.seats)
# sensitivity 1: disablements dated 1642 to 1644 (or undated) only, same hand decisions
D["royalist_4244"] = (D.n_disabled_4244_raw - D.override_minus.where(D.n_disabled_late_raw == 0, 0) + D.override_plus).clip(lower=0).clip(upper=D.seats)
# sensitivity 2: purely mechanical (every "disabled", no hand decisions)
D["royalist_mech"] = D.n_disabled_raw.clip(upper=D.seats)
D["share"] = D.royalist / D.seats
D.to_csv(f"{DATA}/lp1640_constituencies.csv", index=False)

C = D.groupby("county").agg(constituencies=("constituency", "size"), seats=("seats", "sum"), royalist=("royalist", "sum"),
                            royalist_4244=("royalist_4244", "sum"), royalist_mech=("royalist_mech", "sum")).reset_index()
C["share"] = C.royalist / C.seats
C["share_4244"] = C.royalist_4244 / C.seats
C["share_mech"] = C.royalist_mech / C.seats
C["nation"] = np.where(C.county.isin(set(WALES.values())) | (C.county == "Monmouthshire"), "Wales", "England")
C.sort_values("share").to_csv(f"{DATA}/county_allegiance.csv", index=False)
wal = C[C.nation == "Wales"]
chk = {"rows": int(len(D)), "seats": int(D.seats.sum()), "royalist": int(D.royalist.sum()), "royalist_4244": int(D.royalist_4244.sum()),
       "rows_with_notes": int((D.notes.str.len() > 0).sum()), "rows_disabled": int((D.n_disabled_raw > 0).sum()),
       "counties": int(len(C)), "overrides_minus": int(OV.minus.sum()), "overrides_plus": int(OV.plus.sum()), "royalist_mech": int(D.royalist_mech.sum()), "capped": int((D.n_disabled_raw - D.override_minus > D.seats).sum()),
       "wales_seats": int(wal.seats.sum()), "wales_royalist": int(wal.royalist.sum()),
       "wales_excl_monmouth_seats": int(wal[wal.county != "Monmouthshire"].seats.sum()),
       "wales_excl_monmouth_royalist": int(wal[wal.county != "Monmouthshire"].royalist.sum()),
       "share_mean_county": float(C.share.mean()), "share_min": float(C.share.min()), "share_max": float(C.share.max())}
jsave(chk, f"{DATA}/allegiance_checks.json", indent=1)
pd.set_option("display.width", 250, "display.max_colwidth", 110, "display.max_rows", 400)
if os.environ.get("SHOW"):
    print(D[["county", "constituency", "n_members", "n_disabled_raw", "n_disabled_4244_raw", "override_minus", "royalist", "notes"]].to_string())
print(C.to_string())
print(chk)

# ------------------------------------------------------------------ borough points (for the map and the exploratory C2)
# Each borough or university constituency is placed at its town, from the Wikidata settlements list (largest match
# inside the right historic county), with hand spellings for old names. County constituencies have no point.
import geopandas as gpd
from shapely.geometry import Point
from pyproj import Transformer
TO_BNG = Transformer.from_crs(4326, 27700, always_xy=True)
SPELL = {"Eastlow": "East Looe", "Westlow": "West Looe", "Mitchel": "Mitchell", "Clifton Dartmouth Hardness": "Dartmouth",
         "Newport alias Medina": "Newport, Isle of Wight", "Wenlock": "Much Wenlock", "Bletchingly": "Bletchingley",
         "Higham Ferrars": "Higham Ferrers", "Newburgh": "Newborough", "Tregoney": "Tregony", "Haverford West": "Haverfordwest",
         "Denbigh Boroughs": "Denbigh", "Plympton Erle": "Plympton", "Melcombe": "Weymouth", "Old Sarum": "Salisbury",
         "Cambridge University": "Cambridge", "Oxford University": "Oxford", "City of London": "City of London",
         "City of Chester": "Chester", "Kingston upon Hull": "Kingston upon Hull", "Berwick upon Tweed": "Berwick-upon-Tweed",
         "Newcastle": "Newcastle upon Tyne", "Newcastle under Lyme": "Newcastle-under-Lyme", "Bishops Castle": "Bishop's Castle",
         "Grimsby": "Grimsby", "Brecknock": "Brecon", "Carnarvon": "Caernarfon", "Montgomery": "Montgomery", "Radnor": "New Radnor",
         "Romney": "New Romney", "Bere Alston": "Bere Alston", "Wycombe": "High Wycombe", "Marlow": "Marlow", "Lynn": "King's Lynn",
         "Clitheroe": "Clitheroe", "Aldborough": "Aldborough", "Hedon": "Hedon", "East Retford": "Retford", "Dunwich": "Dunwich",
         "Newtown": "Newtown, Isle of Wight", "Yarmouth": None, "Newport": None, "Whitchurch": "Whitchurch, Hampshire",
         "Southwark": "Southwark", "Westminster": "Westminster", "Bury St Edmunds": "Bury St Edmunds", "Flint": "Flint"}
SPECIAL = {("Hampshire", "Yarmouth"): (-1.4980, 50.7060), ("Norfolk", "Yarmouth"): (1.7290, 52.6080), ("Cornwall", "Newport"): (-4.3600, 50.6400),
           ("Middlesex", "City of London"): (-0.0920, 51.5140), ("Middlesex", "Westminster"): (-0.1270, 51.4990),
           ("Surrey", "Southwark"): (-0.0900, 51.5030), ("Wiltshire", "Old Sarum"): (-1.8050, 51.0930),
           ("Hampshire", "Newtown"): (-1.4050, 50.7180), ("Hampshire", "Newport alias Medina"): (-1.2900, 50.7000),
           ("Suffolk", "Dunwich"): (1.6260, 52.2770), ("Cornwall", "Bossiney"): (-4.7430, 50.6650), ("Surrey", "Gatton"): (-0.1950, 51.2620),
           ("Hampshire", "Whitchurch"): (-1.3380, 51.2300), ("Sussex", "New Shoreham"): (-0.2740, 50.8340), ("Westmorland", "Appleby"): (-2.4920, 54.5770),
           ("Wiltshire", "Wootton Bassett"): (-1.9050, 51.5390), ("Worcestershire", "Droitwich"): (-2.1500, 52.2680),
           ("Lancashire", "Newton"): (-2.6330, 53.4530), ("Yorkshire", "Richmond"): (-1.7370, 54.4030)}
COUNTY_SEAT = set(C.county) | {"Westmoreland", "Salop", "Carnarvonshire", "Merioneth", "Glamorgan", "Anglesey", "Brecknockshire", "Cardiganshire",
                               "Carmarthenshire", "Denbighshire", "Flintshire", "Montgomeryshire", "Pembrokeshire", "Radnorshire", "Monmouthshire"}
g = pd.read_csv(f"{SETTLE}/uk_settlements.tsv", sep="\t", dtype=str, keep_default_na=False, quoting=3)
g.columns = ["item", "label", "coord", "pop", "type"]
g["label"] = g.label.str.replace(r'^"(.*)"@en$', r"\1", regex=True)
xy = g.coord.str.extract(r"POINT\(([-\d.eE]+) ([-\d.eE]+)\)").astype(float)
g["lon"], g["lat"] = xy[0], xy[1]
g["popn"] = pd.to_numeric(g["pop"], errors="coerce").fillna(0)
g = g.dropna(subset=["lon"]).sort_values("popn", ascending=False).drop_duplicates("item")
H = gpd.read_file(f"{HC}/historic_counties.geojson").to_crs(27700)
hpoly = {r.county: r.geometry.buffer(3000) for r in H.itertuples()}
pts = []
for r in D.itertuples():
    if r.constituency in COUNTY_SEAT or r.constituency == r.county:
        pts.append((None, None, "county")); continue
    if (r.county, r.constituency) in SPECIAL:
        lon, lat = SPECIAL[(r.county, r.constituency)]; pts.append((lon, lat, "hand")); continue
    nm = SPELL.get(r.constituency, r.constituency) or r.constituency
    cand = g[(g.label == nm) | (g.label.str.startswith(nm + ","))]
    ok = [c for c in cand.itertuples() if hpoly.get(r.county) is not None and hpoly[r.county].contains(Point(*TO_BNG.transform(c.lon, c.lat)))]
    if ok:
        pts.append((ok[0].lon, ok[0].lat, "wikidata"))
    else:
        pts.append((None, None, "unplaced"))
D["lon"] = [p[0] for p in pts]; D["lat"] = [p[1] for p in pts]; D["placed"] = [p[2] for p in pts]
D["kind"] = np.where(D.placed == "county", "county", "borough")
D.to_csv(f"{DATA}/lp1640_constituencies.csv", index=False)
print(D.placed.value_counts().to_dict())
print("UNPLACED:", D[D.placed == "unplaced"][["county", "constituency"]].values.tolist())
chk.update({"boroughs": int((D.kind == "borough").sum()), "boroughs_placed": int(D.placed.isin(["wikidata", "hand"]).sum()),
            "county_seats_rows": int((D.kind == "county").sum())})
jsave(chk, f"{DATA}/allegiance_checks.json", indent=1)
