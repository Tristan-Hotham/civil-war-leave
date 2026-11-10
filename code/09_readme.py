"""Step 9. README.md, LICENSE, reddit/post.md and release/paper/cover_note.md from data/results.json.
10.5281/zenodo.24104516, https://doi.org/10.5281/zenodo.24104516 and https://blog.tristanhotham.com/2026/10/31/civil-war-leave/ are left for the publisher to fill."""
from common import *

R = jload(f"{DATA}/results.json")
t1, t2, lp, g, d1 = R["t1"], R["t2"], R["lp"], R["geo"], R["desc1"]
ci = lambda d, k=2: f"{d['b']:.{k}f} (95% CI {d['lo']:.{k}f} to {d['hi']:.{k}f})"
readme = f"""# Roundhead or Cavalier, Leave or Remain?

The Danelaw, Civil War allegiance and the 2016 referendum in England and Wales. Two old divisions of England, the Danelaw line of Alfred and Guthrum and the sides taken by members of the Long Parliament, tested against the estimated Leave share of every 2010 Westminster constituency, with an analysis plan written before any outcome model was run (NOTES.md). A data study by Dr Tristan Hotham (Independent researcher).

Interactive page: https://maps.tristanhotham.com/{SLUG}/
Paper: {{https://doi.org/10.5281/zenodo.24104516}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/civil-war-leave/}}
Code and data: {REPO}

## Headline results

- The Danelaw (England, {t1['main']['n']} seats): seats on the Danelaw side of the line voted Leave by {d1['raw_gap']:.1f} points more on average ({d1['leave_dl']:.1f}% against {d1['leave_nodl']:.1f}%). With region fixed effects, density and 2011 census composition the gap is {ci(t1['main'])}. Not formally equivalent to zero at the planned 1 point threshold, but close to zero.
- Boundary design ({t1['rd']['main']['n']} seats within 50 km of the line): {ci(t1['rd']['main'])}; unstable across bandwidths ({t1['rd']['bw25']['b']:.2f} at 25 km, {t1['rd']['bw75']['b']:.2f} at 75 km), a jump of {t1['rd']['placebo_sw']['b']:.2f} at a placebo line 50 km south-west, and {t1['rd']['balance_n_sig']} of 13 controls jump at the line. Scandinavian place-name endings do jump at the line ({t1['rd']['scand']['b']:.1f} points); {g['scand_inside_pc']:.1f}% of {g['scand_england']:,} such settlements in England lie on the Danelaw side.
- Other Danelaw measures: area share and Scandinavian name share null; the 15 Danelaw shires of the medieval lists {ci(t1['robust']['shires'])}, the one positive check of {t1['robust_summary']['n']}.
- Civil War: {lp['royalist']} of {lp['seats']} seats returned in 1640 had members who later joined the King ({lp['wales_excl_monmouth_royalist']} of {lp['wales_excl_monmouth_seats']} in Wales, as in Dodd 1952). Per 10 points of a county's royalist share: raw {ci(t2['ladder']['M1'])}; main {ci(t2['main'])}, N = {t2['main']['n']}, {t2['main']['clusters']} counties; wild cluster bootstrap p = {t2['wild']['p']:.3f}; permutation p = {t2['perm']['p']:.3f}. Not significant for England alone, for 1642 to 1644 disablements only, or as a majority indicator. Small, fragile, and in the opposite direction to the popular story.

## Files

| File | What it is |
|---|---|
| `index.html`, `js/page.js` | Interactive page: MapLibre on OpenFreeMap Positron; 2010 seats coloured by Leave share, Danelaw side or Viking village names; historic counties by members for the King; 1640 boroughs; the Danelaw line and placebo lines; search, layers, full screen, popups. |
| `header.png` | Social card, 1200 x 630. |
| `data/analysis.csv` | Every seat in England and Wales with the outcome, controls, all exposures and the borough measure (the model input). |
| `data/seat_geo.csv` | Per seat: Danelaw side, area share, signed distance to the line, segment, placebo distances, historic county, shire coding, settlement and Scandinavian name counts. |
| `data/lp1640_constituencies.csv` | The 1640 member list parsed row by row: county, constituency, members, notes, disablement counts, hand decisions, royalist count, borough point. CC BY-SA 4.0 (from Wikipedia). |
| `data/county_allegiance.csv`, `data/county_level.csv` | Royalist share by historic county (three codings); county means used in the figures. |
| `data/danelaw_line.geojson` | The line (with every point named), the Danelaw side and the placebo lines. |
| `data/results.json`, `data/results_models.json`, `data/model_tables.json` | Every number quoted anywhere; every model; full coefficient tables. |
| `data/web/` | Page data. |
| `code/` | Scripts in order, templates, `allegiance_overrides.csv` (hand decisions), `qa.js`. |
| `release/` | Paper (PDF, LaTeX, figures, `cover_note.md`), blog post and figures, Zenodo files. |
| `reddit/` | Collage, its script, the looping GIF and the post text. |
| `NOTES.md` | Working notes and the analysis plan, written and timestamped before the models were run. |

## Method in brief

- Outcome and controls: Hanretty's (2017) estimated Leave share by 2010 constituency; 2011 census composition (11 shares), log density spline, log distance to a city, region fixed effects (the controls of the beeching-leave study).
- Test 1: the Danelaw line drawn from the treaty text (Thames, Lea, Bedford, Ouse) and Watling Street to Chester; seats with at least half their area on the Danelaw side. OLS with errors clustered by council; a boundary design within 50 km of the line with segment effects, bandwidth and kernel variants, covariate balance and placebo lines.
- Test 2: share of each historic county's 1640 members later disabled for siding with the King, with ten documented hand decisions; OLS clustered by historic county, wild cluster bootstrap and permutation tests.
- Holm adjustment across the two main tests; equivalence tests against a 1 point smallest effect of interest; leave-one-region-out and many other planned checks.

## How to rerun

Needs Python 3 with pandas, numpy, geopandas, shapely, pyproj, statsmodels, scipy, matplotlib, Pillow; xelatex; node with Playwright for QA. Raw inputs are listed in `code/common.py`.

```
python3 code/01_geo.py           # the line, seat sides and distances, historic counties, Scandinavian names
python3 code/02_mps.py           # parse the 1640 member list, code allegiance, place boroughs
python3 code/03_models.py        # all planned models
python3 code/04_results.py       # results.json and page data
python3 code/05_figures.py       # figures and header
python3 code/06_build_site.py    # index.html
python3 code/07_paper.py         # paper (DOI=10.5281/zenodo.N to fill the DOI)
python3 reddit/collage.py
python3 code/09_readme.py        # README, LICENSE, Reddit post, cover note
python3 code/08_release.py       # blog post, Zenodo files
```

## Sources and licences

- Leave estimates: Hanretty, C. (2017) Areal interpolation and the UK's referendum on EU membership. Journal of Elections, Public Opinion and Parties 27(4), 466 to 483. 2011 census by constituency (ONS and NRS, Open Government Licence v3.0) via parlitools; assembled in Hotham (2026) Did Beeching's cuts make places vote Leave?, doi:10.5281/zenodo.24091898.
- Westminster constituency boundaries 2010: ONS and OS, Open Government Licence v3.0.
- Wikipedia contributors, "List of MPs elected to the English Parliament in 1640 (November)", retrieved 2026, CC BY-SA 4.0.
- Historic counties rebuilt from Wikidata places in Hotham (2026) Fencing the commons, doi:10.5281/zenodo.23873003. Settlements: Wikidata (CC0).
- Base map: OpenFreeMap Positron (OpenStreetMap contributors, ODbL). MapLibre GL JS (BSD 3-Clause).
- Text, figures and derived data CC BY 4.0, except `data/lp1640_constituencies.csv` and the Long Parliament fields in other files, which are CC BY-SA 4.0 because they come from Wikipedia; code MIT.

## Citation

Hotham, T. (2026) Roundhead or Cavalier, Leave or Remain? The Danelaw, Civil War allegiance and the 2016 referendum in England and Wales. Zenodo. {{https://doi.org/10.5281/zenodo.24104516}}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

{AI}
"""
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)
mit = open("/home/claude/studies/wiki-vs-hansard/LICENSE", encoding="utf-8").read().split("Text, figures and the paper")[0]
lic = mit.replace("Code (code/, js/, reddit/collage.py, reddit/gif.py)", "Code (code/, js/, reddit/collage.py)") + (
    "Text, figures and the paper: Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/\n"
    "Derived data (data/): CC BY 4.0, except data/lp1640_constituencies.csv and the Long Parliament fields (members, notes, royalist counts) in other files, "
    "which are adapted from English Wikipedia and shared under CC BY-SA 4.0, https://creativecommons.org/licenses/by-sa/4.0/. "
    "Other sources: 2011 census and boundaries (Open Government Licence v3.0), Wikidata (CC0).\n")
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(lic)
post = f"""**Title:** [OC] Seats on the Danelaw side of Alfred and Guthrum's line voted Leave by {d1['raw_gap']:.1f} points more. Compared with similar places, the gap is {t1['main']['b']:.1f}.

**Body:**

People often set the 2016 referendum map beside the Danelaw or the Civil War. I tested the Danelaw across England's {R['n']['england']} constituencies and the Civil War across {R['n']['ew_test2']} seats in England and Wales, with the plan written down before running any model.

- Danelaw side of the line (Thames, Lea, Bedford, Ouse, Watling Street to Chester): {d1['leave_dl']:.1f}% Leave vs {d1['leave_nodl']:.1f}%.
- Comparing seats with similar places in the same region (density, age, degrees, ethnicity, jobs, housing): {t1['main']['b']:.2f} points, 95% interval {t1['main']['lo']:.1f} to {t1['main']['hi']:.1f}.
- The line is real in one way: {g['scand_inside_pc']:.0f}% of the {g['scand_england']:,} English settlements (Wikidata) ending -by, -thorpe, -thwaite or -toft are on the Danelaw side.
- Civil War: {lp['royalist']} of {lp['seats']} seats elected in 1640 had members who later joined the King. Counties with more royalist members were, if anything, very slightly less Leave once like is compared with like ({t2['main']['b']:.2f} points per 10 points of royalist share). That is small and fragile: the wild cluster bootstrap p is {t2['wild']['p']:.2f} and {t2['robust_summary']['n'] - t2['robust_summary']['n_sig']} of {t2['robust_summary']['n']} checks lose significance.

Interactive map with the line, the 1640 boroughs and every seat: https://maps.tristanhotham.com/{SLUG}/

**Source comment:**

Data: Leave estimates by constituency, Hanretty (2017); 2011 census (ONS, OGL); List of MPs elected to the English Parliament in 1640 (Wikipedia, CC BY-SA 4.0); Wikidata settlements (CC0). Method: OLS with region fixed effects and census controls, a boundary comparison along the line, placebo lines, wild cluster bootstrap; plan written before the analysis. Tools: Python (pandas, statsmodels, geopandas, matplotlib), MapLibre. Paper and code: {REPO}
"""
os.makedirs(os.path.join(ROOT, "reddit"), exist_ok=True)
open(os.path.join(ROOT, "reddit", "post.md"), "w", encoding="utf-8").write(post)
cover = f"""# Cover note: Roundhead or Cavalier, Leave or Remain?

## Suitable journals (no article processing charge on the standard route)

Word limits below come from checks recorded in earlier studies of the same author in 2026 (the journals' author pages could not be re-read in this session); recheck before submitting. The paper is about 8,200 words before the references, counting tables and captions, with 6 figures and 7 main-text tables.

1. **Political Geography** (Elsevier). Hybrid: subscription publication is free to authors; open access is optional and paid. Full-length papers up to 11,000 words (checked on the journal's Elsevier page for an earlier paper in 2026). Fits as it stands. Best fit: a test of a popular geographical claim about old boundaries and the electoral map, with a boundary design.
2. **British Politics** (Palgrave Macmillan). Subscription, no charge to authors. Articles of no more than 9,000 words excluding the bibliography (author guidelines, checked in 2026 for an earlier paper). Fits. Suits the British historical framing.
3. **Electoral Studies** (Elsevier). Hybrid, subscription route free to authors. Word limit not confirmed; check the guide for authors and shorten the background section if needed.

Also suggested: the **Journal of Historical Political Economy**; its charges and limits could not be checked in this session.

## Before submitting

- Persistence and boundary-design references verified online at review and cited in Sections 2.2, 2.3 and 7.3: Voigtländer and Voth (2012, QJE), Fouka and Voth (2023, APSR), Alesina and Giuliano (2015, JEL), Leslie et al. (2015, Nature), Keele and Titiunik (2015, Political Analysis). Kershaw and Røyrvik (2016) was not verified and is not cited.
- A national count of royalist and parliamentarian members from Brunton and Pennington (1954) would strengthen the check on the allegiance coding (currently the Welsh count from Dodd 1952).
- A territorial coding of districts held by each side in May 1643 from Gardiner's School Atlas of English History (1914, plate for 1 May 1643) would add the territorial test the brief suggested.

## Summary of the contribution (for a cover letter)

Maps that set the 2016 Leave vote beside the Danelaw or the Civil War are widely shared, and a large literature asks whether historical shocks leave lasting political traces. This paper puts two such claims to a planned test across the {R['n']['ew']} constituencies of England and Wales. Seats on the Danelaw side of the line agreed by Alfred and Guthrum voted Leave by {d1['raw_gap']:.1f} points more, but with region, density and census composition held fixed the gap is {t1['main']['b']:.2f} points (95% CI {t1['main']['lo']:.2f} to {t1['main']['hi']:.2f}); a boundary design is unstable and finds a jump at a placebo line, while Scandinavian place-names do jump at the real line. Coding the sides taken by the members of the Long Parliament from the 1640 member list, counties with more royalist members show a small negative conditional association with Leave that is not robust to wild cluster bootstrap inference. The resemblance of the maps is a resemblance of places, not, on this evidence, a political memory. Data and code are openly released.
"""
open(os.path.join(REL, "paper", "cover_note.md"), "w", encoding="utf-8").write(cover)
for t_ in (readme, post, cover, lic):
    for bad in ("—", "–", "DSIT", "DCMS", "civil serv", "pre-registered"):
        assert bad not in t_, bad
print("readme", len(readme.split()), "words; cover", len(cover.split()), "; post title", post.splitlines()[0][:160])
