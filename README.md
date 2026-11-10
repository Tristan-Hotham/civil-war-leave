# Roundhead or Cavalier, Leave or Remain?

The Danelaw, Civil War allegiance and the 2016 referendum in England and Wales. Two old divisions of England, the Danelaw line of Alfred and Guthrum and the sides taken by members of the Long Parliament, tested against the estimated Leave share of every 2010 Westminster constituency, with an analysis plan written before any outcome model was run (NOTES.md). A data study by Dr Tristan Hotham (Independent researcher).

Interactive page: https://maps.tristanhotham.com/civil-war-leave/
Paper: https://doi.org/10.5281/zenodo.24104516
Blog post: https://blog.tristanhotham.com/2026/10/31/civil-war-leave/
Code and data: https://github.com/Tristan-Hotham/civil-war-leave

## Headline results

- The Danelaw (England, 533 seats): seats on the Danelaw side of the line voted Leave by 6.9 points more on average (56.9% against 50.0%). With region fixed effects, density and 2011 census composition the gap is -0.16 (95% CI -1.81 to 1.49). Not formally equivalent to zero at the planned 1 point threshold, but close to zero.
- Boundary design (251 seats within 50 km of the line): -0.42 (95% CI -3.34 to 2.50); unstable across bandwidths (3.65 at 25 km, -2.13 at 75 km), a jump of 2.59 at a placebo line 50 km south-west, and 7 of 13 controls jump at the line. Scandinavian place-name endings do jump at the line (3.9 points); 97.5% of 1,100 such settlements in England lie on the Danelaw side.
- Other Danelaw measures: area share and Scandinavian name share null; the 15 Danelaw shires of the medieval lists 2.07 (95% CI 0.64 to 3.50), the one positive check of 10.
- Civil War: 201 of 507 seats returned in 1640 had members who later joined the King (17 of 24 in Wales, as in Dodd 1952). Per 10 points of a county's royalist share: raw 0.84 (95% CI -0.66 to 2.35); main -0.30 (95% CI -0.56 to -0.05), N = 558, 49 counties; wild cluster bootstrap p = 0.069; permutation p = 0.005. Not significant for England alone, for 1642 to 1644 disablements only, or as a majority indicator. Small, fragile, and in the opposite direction to the popular story.

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

Hotham, T. (2026) Roundhead or Cavalier, Leave or Remain? The Danelaw, Civil War allegiance and the 2016 referendum in England and Wales. Zenodo. https://doi.org/10.5281/zenodo.24104516

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
