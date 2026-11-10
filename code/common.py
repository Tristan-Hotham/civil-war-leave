"""Shared paths, constants and helpers for the civil-war-leave study
("Roundhead or Cavalier, Leave or Remain? Old fault lines and the 2016 vote").

Inputs (read in place, never modified):
  BL/constituencies.csv     2010 Westminster constituencies (Great Britain) with Hanretty's (2017) estimated Leave share,
                            2011 census composition, region, LAD, UKIP 2015, Brexit Party 2019, Reform UK 2024 and the
                            seat reference point in British National Grid (cx, cy). Built and documented by the
                            beeching-leave study (Hotham 2026, doi:10.5281/zenodo.24091898).
  RAW11/wpc2010_gb.json     Westminster constituency boundaries, 2010 (PCON13), GeoJSON (ONS/OS, Open Government Licence v3.0)
  HC/historic_counties.geojson  historic counties of England and Wales rebuilt from about 40,000 Wikidata places (P7959)
                            by the enclosure study (Hotham 2026, doi:10.5281/zenodo.23873003); approximate, Yorkshire undivided
  RAW13/wiki_pages.json     wikitext (CC BY-SA 4.0) of "List of MPs elected to the English Parliament in 1640 (November)"
                            (key lp1640) and "List of MPs in the English parliament in 1645 and after" (lp1645), retrieved 2026
  SETTLE/uk_settlements.tsv Wikidata settlements in the UK with point and type (CC0), used for Scandinavian name endings
  GEO/counties_uk.geojson   modern county outlines (coast of England and Wales, for figures)
"""
import json, os, re, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BL = os.environ.get("CW_BL", "/home/claude/studies/beeching-leave/data")
RAW11 = os.environ.get("CW_RAW11", "/home/claude/newdata/raw_new11")
RAW13 = os.environ.get("CW_RAW13", "/home/claude/newdata/raw_new13")
HC = os.environ.get("CW_HC", "/home/claude/studies/enclosure/data")
SETTLE = os.environ.get("CW_SETTLE", "/home/claude/newdata/raw_new8")
GEO = os.environ.get("CW_GEO", "/home/claude/newdata/raw/geo")
FONTS = os.environ.get("CW_FONTS", "/home/claude/ref/fonts")
SCR = os.environ.get("CW_SCRATCH", "/home/claude/scratch/civil-war-leave")
DATA = os.path.join(ROOT, "data")
IMG = os.path.join(ROOT, "img")
REL = os.path.join(ROOT, "release")
for d in (DATA, IMG, SCR):
    os.makedirs(d, exist_ok=True)

SLUG = "civil-war-leave"
TITLE = "Roundhead or Cavalier, Leave or Remain?"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")
BYLINE = "Dr Tristan Hotham · Independent researcher · 2026"
SEED = 8781642

# ------------------------------------------------------------------------------------------------ the Danelaw line
# (lon, lat, what the point is). Treaty of Alfred and Guthrum, clause 1 (Attenborough 1922; Keynes and Lapidge 1983):
# "up the Thames, and then up the Lea, and along the Lea unto its source, then straight to Bedford, then up the Ouse
# unto Watling Street". Beyond the treaty text the boundary is conventionally drawn along Watling Street (the Roman
# road, today's A5) to Wroxeter and on along the Roman road through Whitchurch to Chester and the Dee estuary.
# Points follow the river or road course at roughly 5 to 15 km spacing (read from OpenStreetMap; approximate).
LINE = [
    (0.0080, 51.5085, "Mouth of the Lea (Bow Creek) on the Thames", "lea"),
    (-0.0215, 51.5390, "Lea at Old Ford", "lea"),
    (-0.0570, 51.5890, "Lea at Tottenham Hale", "lea"),
    (-0.0170, 51.6850, "Lea at Enfield Lock and Waltham Abbey", "lea"),
    (-0.0100, 51.7470, "Lea at Broxbourne", "lea"),
    (-0.0300, 51.8110, "Lea at Ware", "lea"),
    (-0.0780, 51.7960, "Lea at Hertford", "lea"),
    (-0.2150, 51.7960, "Lea at Lemsford (Welwyn Garden City)", "lea"),
    (-0.2920, 51.8120, "Lea at Wheathampstead", "lea"),
    (-0.3500, 51.8200, "Lea at Harpenden", "lea"),
    (-0.4170, 51.8790, "Lea at Luton", "lea"),
    (-0.4620, 51.9050, "Source of the Lea (Leagrave)", "ouse"),
    (-0.4660, 52.1360, "Bedford", "ouse"),
    (-0.5300, 52.1480, "Ouse at Bromham", "ouse"),
    (-0.6250, 52.1600, "Ouse at Turvey", "ouse"),
    (-0.7010, 52.1530, "Ouse at Olney", "ouse"),
    (-0.7220, 52.0870, "Ouse at Newport Pagnell", "ouse"),
    (-0.8100, 52.0650, "Ouse at Wolverton", "ouse"),
    (-0.8530, 52.0570, "Watling Street crosses the Ouse (Stony Stratford)", "ws1"),
    (-0.9890, 52.1330, "Watling Street at Towcester (Lactodurum)", "ws1"),
    (-1.0830, 52.2330, "Watling Street at Weedon Bec", "ws1"),
    (-1.1500, 52.3350, "Watling Street near Crick", "ws1"),
    (-1.1950, 52.4030, "Watling Street at Dove Bridge", "ws1"),
    (-1.2840, 52.4960, "High Cross (Venonis)", "ws2"),
    (-1.5300, 52.5700, "Watling Street at Mancetter (Manduessedum)", "ws2"),
    (-1.7000, 52.6130, "Watling Street at Fazeley", "ws2"),
    (-1.8550, 52.6560, "Wall (Letocetum)", "ws2"),
    (-2.1150, 52.6930, "Watling Street at Gailey", "ws2"),
    (-2.2850, 52.7000, "Watling Street at Weston-under-Lizard", "ws2"),
    (-2.4300, 52.7000, "Watling Street at Redhill (Uxacona)", "ws2"),
    (-2.6450, 52.6740, "Wroxeter (Viroconium)", "ws2"),
    (-2.6830, 52.9690, "Whitchurch (Mediolanum)", "ws2"),
    (-2.7650, 53.0190, "Roman road at Malpas", "ws2"),
    (-2.8920, 53.1910, "Chester (Deva)", "dee"),
    (-3.0250, 53.2100, "Dee at Queensferry", "dee"),
    (-3.1500, 53.2900, "Dee estuary", "dee"),
    (-3.2500, 53.3700, "Mouth of the Dee", "dee"),
]
SEG_NAMES = {"lea": "River Lea", "ouse": "Lea source to Bedford and the Ouse", "ws1": "Watling Street, Stony Stratford to High Cross",
             "ws2": "Watling Street and the Roman road, High Cross to Chester"}
# closing the Danelaw side of the polygon through the sea and the Thames estuary (north bank = Danelaw side)
CLOSE = [(-3.6, 53.45), (-6.5, 55.2), (-6.5, 60.9), (3.0, 60.9), (3.0, 51.45), (1.0, 51.47), (0.62, 51.50), (0.36, 51.455),
         (0.12, 51.50)]
# the 15 shires assigned to Danish law in the medieval shire lists of the threefold division of English law
DANE_SHIRES = ["Yorkshire", "Nottinghamshire", "Derbyshire", "Leicestershire", "Lincolnshire", "Northamptonshire",
               "Huntingdonshire", "Cambridgeshire", "Bedfordshire", "Norfolk", "Suffolk", "Essex", "Hertfordshire",
               "Middlesex", "Buckinghamshire"]
SHIFT_KM = 50.0       # placebo line translation
BW_MAIN = 50.0        # boundary design bandwidth, km
LAT_CUT = 52.75       # robustness: seats south of this latitude only


def jload(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def nonan(v):
    if isinstance(v, float) and (v != v or v in (float("inf"), float("-inf"))):
        return None
    if isinstance(v, (list, tuple)):
        return [nonan(x) for x in v]
    if isinstance(v, dict):
        return {str(k): nonan(x) for k, x in v.items()}
    if hasattr(v, "item"):
        return nonan(v.item())
    return v


def jsave(obj, path, indent=None):
    obj = nonan(obj)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, allow_nan=False, indent=indent, separators=None if indent else (",", ":"))


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f=None):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "pc1": return f"{float(v):.1f}%"
    if f == "f0": return f"{float(v):.0f}"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f == "f3": return f"{float(v):.3f}"
    if f == "abs1": return f"{abs(float(v)):.1f}"
    if f == "abs2": return f"{abs(float(v)):.2f}"
    if f == "p100": return f"{100 * float(v):.0f}"
    raise ValueError(f)


def wl(s):
    """strip wiki links and markup to plain text"""
    s = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"<ref[^>]*/>|<ref.*?</ref>", "", s, flags=re.S)
    s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    s = re.sub(r"'''?", "", s)
    return s.replace("&nbsp;", " ").strip()
