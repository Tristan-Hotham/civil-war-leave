"""Step 8. Blog post and meta (release/blog), Zenodo files and metadata (release/zenodo).
10.5281/zenodo.24104516, https://doi.org/10.5281/zenodo.24104516 and https://blog.tristanhotham.com/2026/10/31/civil-war-leave/ stay as placeholders for the publisher. Run after 07_paper.py and 09_readme.py."""
import json as _json, shutil, zipfile
from PIL import Image
from common import *

R = jload(f"{DATA}/results.json")
NAME = "Hotham_Civil_War_Leave"
KEEP = {"DOI", "DOI_URL", "BLOG_URL"}
# facts stated in words in the post, checked against the data
assert R["lp"]["counties_none"] == ["Bedfordshire", "Denbighshire", "Essex", "Middlesex"]
assert sorted(R["lp"]["counties_all"]) == sorted(["Caernarfonshire", "Cardiganshire", "Carmarthenshire", "Flintshire", "Merionethshire", "Montgomeryshire", "Radnorshire", "Westmorland"])
assert R["lp"]["wales_excl_monmouth_royalist"] == 17 and R["lp"]["wales_excl_monmouth_seats"] == 24
assert R["t1"]["rd"]["placebo_sw"]["p"] < 0.05 and R["t1"]["rd"]["scand"]["p"] < 0.05
assert R["t2"]["robust"]["england"]["p"] > 0.05 and R["t2"]["robust"]["x_4244"]["p"] > 0.05 and R["t2"]["robust"]["x_maj"]["p"] > 0.05
assert R["t2"]["robust_summary"]["n"] - R["t2"]["robust_summary"]["n_sig"] == 3 and R["t2"]["ladder"]["M1"]["p"] > 0.05
post = open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read()
post = re.sub(r"\{\{(?!IMG)([^}|]+)(\|(\w+))?\}\}", lambda m: m.group(0) if m.group(1) in KEEP else fmt(get(R, m.group(1)), m.group(3)), post)
post = re.sub(r"\{\{IMG\|([^|]+)\|(.*?)\|(.*?)\}\}", lambda m: "{{IMG|" + m.group(1) + "|" + re.sub(r"\{\{([^}|]+)\|(\w+)\}\}", lambda q: fmt(get(R, q.group(1)), q.group(2)), m.group(2)) + "|" + m.group(3) + "}}", post)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
assert 5 <= len(used) <= 8, len(used)
assert all(re.search(r"^\{\{IMG\|" + re.escape(u_), post, re.M) for u_ in used) and "wp:image" not in post
for img in used:
    assert Image.open(f"{REL}/blog/{img}").size[0] == 1800, img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{REL}/blog/{fn}")
assert set(re.findall(r"\{\{([^|}]+)\}\}", post)) <= KEEP, set(re.findall(r"\{\{([^|}]+)\}\}", post))
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS", "civil serv", "pre-registered"):
    assert bad not in vis, bad
assert AI in post
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
meta = {"title": "Roundhead or Cavalier, Leave or Remain?",
        "slug": "civil-war-leave",
        "excerpt": f"Seats on the Danelaw side of Alfred and Guthrum's line voted Leave by {R['x']['t1_raw']:.1f} points more. Compared like with like, the gap is {R['x']['t1_main']:.1f}. Counties whose members sided with the King: a small, fragile link the other way.",
        "seo_description": "Does the Danelaw or the Civil War predict the 2016 Leave vote? Constituencies in England and Wales tested, comparing like with like.",
        "tags": ["maps", "data visualisation", "Brexit", "Danelaw", "English Civil War", "history", "elections", "England"],
        "header_alt": "Title card reading 'Roundhead or Cavalier, Leave or Remain?' beside a map of England and Wales shaded by the estimated Leave share, with the Danelaw line drawn from London to Chester."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
for v in meta.values():
    assert "\u2014" not in str(v) and "\u2013" not in str(v)
_json.dump(meta, open(f"{REL}/blog/meta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
for fn in os.listdir(Z):
    os.remove(os.path.join(Z, fn))
shutil.copy(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/{SLUG}_data_and_code.zip"
OWN = ["analysis.csv", "seat_geo.csv", "lp1640_constituencies.csv", "county_allegiance.csv", "county_level.csv", "danelaw_line.geojson",
       "results.json", "results_models.json", "model_tables.json", "geo_checks.json", "allegiance_checks.json"]
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir(os.path.join(ROOT, "code"))):
        if fn.endswith((".pyc", ".png")) or fn == "__pycache__":
            continue
        z.write(os.path.join(ROOT, "code", fn), f"{SLUG}/code/{fn}")
    for fn in OWN:
        z.write(os.path.join(DATA, fn), f"{SLUG}/data/{fn}")
    for fn in ("README.md", "LICENSE", "NOTES.md"):
        z.write(os.path.join(ROOT, fn), f"{SLUG}/{fn}")
    z.write(os.path.join(ROOT, "reddit", "collage.py"), f"{SLUG}/reddit/collage.py")
    z.write(os.path.join(REL, "paper", "cover_note.md"), f"{SLUG}/paper/cover_note.md")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\&", "&").replace("$", "").replace("``", "\"").replace("''", "\"").replace("\\citep", "").replace("\\citet", "")
zmeta = {"title": "Roundhead or Cavalier, Leave or Remain? The Danelaw, Civil War Allegiance and the 2016 Referendum in England and Wales",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive version: <a href=\"{PAGE}\">{PAGE}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>. Blog post: {{https://blog.tristanhotham.com/2026/10/31/civil-war-leave/}}.</p><p>Sources: Hanretty (2017) Leave estimates and 2011 census by constituency (ONS/NRS, OGL) via parlitools; ONS/OS boundaries (OGL); Wikipedia list of MPs elected to the English Parliament in 1640 (CC BY-SA 4.0); Wikidata (CC0); historic counties from Fencing the Commons (doi:10.5281/zenodo.23873003); constituency data from Did Beeching's Cuts Make Places Vote Leave? (doi:10.5281/zenodo.24091898). Text, figures and derived data CC BY 4.0 (Long Parliament fields CC BY-SA 4.0); code MIT.</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["Brexit", "Danelaw", "English Civil War", "Long Parliament", "historical persistence", "electoral geography", "boundary design", "England and Wales"],
         "license": "cc-by-4.0", "language": "eng",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": PAGE, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "10.5281/zenodo.23873003", "relation": "isDerivedFrom", "resource_type": "publication"},
                                 {"identifier": "10.5281/zenodo.24091898", "relation": "isDerivedFrom", "resource_type": "publication"}],
         "files": sorted(os.listdir(Z))}
sj = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in sj and "\u2013" not in sj and "--" not in sj
_json.dump(zmeta, open(f"{Z}/metadata.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("blog words", words, "figures", len(used), "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
