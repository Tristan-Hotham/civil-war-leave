# civil-war-leave: working notes

Slug: civil-war-leave. Title (working): "Roundhead or Cavalier, Leave or Remain? Old fault lines and the 2016 vote".
Brief: /home/claude/work/new13/BRIEFS.md section E (+ top of new12, new11, new10, new9, new8 briefs, house brief
/home/claude/newdata/BRIEF.md, GIF brief /home/claude/gifs/BRIEF.md). Format refs: fame-half-life, byelection-attention;
closest analogue for data and models: beeching-leave (same outcome and controls).
Scratch: /home/claude/scratch/civil-war-leave (delete by exact path at the end).

## 0. Analysis plan (pre-specified in a written plan)

Written 2026-11-10T08:34:26Z (UTC), before any association between any exposure and any outcome was computed.
At this point I had looked only at: the column names of beeching-leave/data/constituencies.csv, one example row, the
number of seats by country and region; the wikitext layout of the Long Parliament member lists (lp1640, lp1645), not
counted or coded; the property names of the historic county shapes. No Leave figure has been mapped, summarised by
group, or correlated with anything.

### Question
Popular maps often set the 2016 Leave/Remain map beside old divisions of England. Two such divisions are tested:
the Danelaw (the area of Scandinavian rule and law east and north of the line agreed by Alfred and Guthrum, c. 878 to
890) and the sides taken in the First Civil War (1642 to 1646). The question is whether either old division predicts
the estimated Leave share of a constituency once today's composition, density and region are held fixed. Both tests
are correlational. A null is a result and will be reported plainly.

### Unit, sample, outcome (both tests)
- Unit: Westminster constituency, 2010 boundaries. Test 1: England (533 seats). Test 2: England and Wales (573 seats;
  Wales returned members to the Long Parliament). Scotland is excluded from both.
- Outcome: Hanretty's (2017) estimated Leave share in 2016, % (`leave` in beeching-leave/data/constituencies.csv,
  parlitools `figure_to_use`, counted ward results where known).
- Controls, identical to the beeching-leave main model (all 2011 census by constituency): natural cubic spline of log
  population density (4 df, centred), log(1 + km to the nearest built-up area of 100,000+), % aged 65+, % level 4+
  qualifications, % no qualifications, % semi-routine and routine, % White British, % born outside the UK, % social
  rented, % manufacturing, % agriculture, % mining, % long-term sick; region fixed effects (9 English regions, plus Wales
  in Test 2).
- Standard errors clustered by local authority (LAD containing most of the seat) in Test 1; in Test 2 the exposure is
  set at county level, so clustered by historic county (about 52 clusters), with wild cluster bootstrap p-values
  (Webb weights, 9,999 draws, null imposed) because the number of clusters is modest.

### Test 1 (primary): the Danelaw
Exposure D1 (main). The treaty line as written in the Treaty of Alfred and Guthrum (translation in Attenborough 1922;
Keynes and Lapidge 1983): up the Thames, up the Lea to its source, straight to Bedford, up the Ouse to Watling Street;
then, as conventionally drawn beyond the treaty text, north-west along Watling Street (the A5 line) to Wroxeter and on
along the Roman road through Whitchurch to Chester and the Dee estuary. I draw it as a polyline of documented points
(listed in code/common.py with what each point is). A seat is in the Danelaw if at least half its area lies on the
east/north side (D1 = 1); the area share itself (0 to 1) is the continuous version.
H1: conditional on region and composition, Danelaw seats differ in Leave share. Two-sided. The popular claim implies a
positive sign (Leave higher in the Danelaw).
Main specification (M4): OLS Leave ~ D1 + region FE + rurality + composition, England, SE clustered by LAD.
Ladder reported: M1 bivariate, M2 + region FE, M3 + rurality, M4 + composition (main).
What counts against H1: a 95% CI for D1 in M4 that includes zero. Smallest effect of interest (SESOI) fixed now at 1
percentage point of Leave: if the 90% CI lies inside -1 to +1 (TOST at 5%), the result is called equivalent to zero.

Boundary design (pre-specified second estimate of Test 1). Seats whose centroid is within 50 km of the line (the
treaty part plus Watling Street to Chester), England. Running variable: signed distance in km from the seat centroid to
the line (positive = Danelaw side). Local linear, separate slopes each side, line-segment fixed effects (four segments:
the Lea; Lea source to Bedford and the Ouse; Watling Street from Stony Stratford to High Cross; High Cross to Chester),
plus the rurality and composition controls; SE clustered by LAD. Bandwidths 25, 50 (main) and 75 km; triangular kernel
as a check; without controls as a check. Covariate balance at the line: each control in turn as the outcome of the
same boundary model without controls.
Placebo lines: the whole line translated 50 km to the north-east and 50 km to the south-west; boundary model at each
fake line, using only seats on the same side of the real line as the fake line lies. Expect no jump.

Measurement checks (Test 1):
- D2: the 12th-century legal Danelaw, the shires listed under Danish law in the Leges Henrici Primi (c. 1115):
  Yorkshire, Nottinghamshire, Derbyshire, Leicestershire, Lincolnshire, Northamptonshire, Bedfordshire,
  Buckinghamshire, Hertfordshire, Essex, Middlesex, Norfolk, Suffolk, Cambridgeshire, Huntingdonshire (list to be
  verified against a source; seats coded by the historic county of their centroid).
- D3 (secondary exposure and a check that the line marks something real): share of Wikidata settlements in the seat
  with a Scandinavian name ending (-by, -thorpe/-thorp, -thwaite, -toft). Expect a clear jump at the line (validation).
  Used also as a continuous exposure in M4 (per 10 points).
- The line's least documented part: re-estimate M4 and the boundary model on seats south of latitude 52.75 N only, where
  the line is the treaty text plus the well-attested Watling Street.
Robustness (Test 1): area share instead of indicator; counted ward results only; drop London; leave-one-region-out;
density decile FE instead of spline; Conley (1999) spatial HAC SEs at 50 and 100 km; England and Wales with Wales
coded outside the Danelaw; Cook's distance top 1% dropped. Other outcomes (secondary): UKIP 2015, Brexit Party 2019
(seats it contested), Reform UK 2024 (approximate, mapped to 2010 seats).

### Test 2 (secondary): Civil War allegiance
Exposure C1 (main). For each historic county of England and Wales, the share of the members returned to the Long
Parliament in 1640 (and at by-elections before the war) for the county and its boroughs who were later "disabled" from
sitting for adhering to the King (1642 to 1644), coded from the notes column of the Wikipedia list of MPs elected in
1640 (lp1640). Seats take the value of the historic county containing their centroid (rebuilt historic counties from
the enclosure study, Hotham 2026). Effect reported per 10 points of royalist share and per SD.
H2: the royalist share of a county's members predicts Leave, conditional on region and composition. Two-sided.
Coding decision rule (set now): the coding counts as usable for a confirmatory test only if (a) at least 90% of
constituency rows parse, and (b) the total of royalist members is within 25% of the published count for the
same population (Brunton and Pennington 1954; to be verified). If either fails, Test 2 is reported as exploratory.
Even if usable, the MP coding measures the gentry who sat for a county, not territory or popular allegiance: said so.
Checks: permutation test (county values shuffled across counties, 5,000 draws); England only; leave-one-region-out;
leave-one-county-out (range); counted results only; majority-royalist indicator (C1 > 0.5) instead of the share;
other outcomes as above.
Exploratory (labelled): C2, seat-level: for seats containing a 1640 parliamentary borough, the royalist share of that
borough's members; the "recruiter" replacements of 1645 and after (lp1645) as a description only.

### Multiple tests
Two confirmatory coefficients (D1 in M4; C1 in M4). Holm-adjusted p-values reported for both.

### Language
Observational and cross-sectional. Controls are measured in 2011, long after the exposures, so M4 asks whether the old
line adds anything beyond today's composition; M2 (region only) is reported as the total association within regions.
No causal claims. Neutral about Leave and Remain.

## 1. Log
- Data construction (01_geo.py, 02_mps.py), before any outcome model:
  - Danelaw line: 37 points (code/common.py), treaty text to Stony Stratford, Watling Street to Wroxeter, Roman road to
    Chester, Dee estuary. Orientation checked with 11 named towns (asserts). England: 275 of 533 seats have at least half
    their area on the Danelaw side; 29 seats are split (5 to 95%). 251 English seats within 50 km of the land line.
  - D2 (15 "Dena lage" shires): source checked online: Wikipedia "Threefold division of England" (list attributed to the
    Leges Henrici Primi) and a Middle English shire list (Oxford, Jesus College MS 29) quoted on a blog: same 15 shires.
    221 English seats. The LHP text itself (Downer 1972 edition) could not be read; the paper says "medieval shire lists".
  - D3: 26,052 Wikidata settlements in English seats; 1,100 with Scandinavian endings, 1,073 (97.5%) of them on the
    Danelaw side of the line (the line marks something real in the place-names). 64 seats with < 5 settlements -> NA.
  - Historic county of each seat: reference point in the enclosure study's rebuilt counties; 14 seats whose largest
    area share is in another county (kept by reference point).
  - Long Parliament (lp1640): 267 constituency rows, 507 seats, all rows parse (rule a met). Royalist = "disabled" in the
    notes (counting replacements and "both"), with 10 hand decisions (code/allegiance_overrides.csv): 5 disablements that
    were not royalism (Marten, the two Hothams, Hales 1648, Ralph Verney 1645) and 5 royalist members killed before they
    could be disabled (Sidney Godolphin, Trevanion, Sir Edmund Verney, Ferdinando Stanhope, William Herbert of Cardiff).
    201 of 507 seat-holders coded royalist (40%). Check (b): a published national total (Brunton and Pennington 1954)
    could not be read online (searches gave catalogue records only). Deviation, recorded here: the check used instead is
    Dodd's Welsh figure as quoted by Zagorin (1959): 17 of the 24 Welsh members went to the King; my coding gives 17 of 24.
    The list's own introduction says "over 150" joined the King. I keep Test 2 as the planned secondary test, with the
    caveat that the national total is unchecked. County Durham returned no members in 1640: its seats have no value.
  - Borough points: 216 borough and university constituencies placed (197 by Wikidata name inside the right county, 19
    by hand: Isle of Wight boroughs, Old Sarum, Newton = Newton-le-Willows, Richmond (Yorks) and others).
- RESULTS, first and only run of the plan (03_models.py; numbers in data/results_models.json):
  Test 1 (England, N = 533, 305 LAD clusters). Raw gap +6.9 points (Danelaw 56.9% vs 50.0%). M1 +6.88 [4.32, 9.44];
  M2 region FE +8.01 [2.82, 13.19]; M3 +6.70; M4 main -0.16 [-1.81, 1.49], p = 0.85. TOST at 1 point not passed
  (90% CI -1.54 to 1.22): not shown equivalent to zero, but no association. Conley 50/100 km CIs narrower, same answer.
  Only 5 regions contain both sides (East Midlands 1 non-Danelaw seat, East 10, London 11 Danelaw seats east of the Lea,
  South East 1, West Midlands 12); North West, North East, Yorkshire all inside, South West all outside.
  Boundary design: main (50 km) -0.42 [-3.34, 2.50], N = 251; 25 km +3.65 [0.24, 7.07] p = 0.04; 75 km -2.13; triangular
  +1.24; no controls +9.60 [2.02, 17.19]; region FE +0.84; south of 52.75 N +1.68. Placebo lines: NE -0.12 (null), SW
  +2.59 [0.14, 5.05] p = 0.04 (a jump where there is no line). Balance: 7 of 13 covariates differ at the line
  (standardised gaps up to 0.86 SD). So the boundary estimates are unstable and the design cannot isolate a line effect.
  Scandinavian names jump at the line (+3.9 points, p = 0.04; validation of the line).
  Measurement checks: area share null; Scandinavian names null (-0.34 per 10 points); the 15 medieval Danelaw shires
  +2.07 [0.64, 3.50] p = 0.005 (the one positive check: reported as such, not as support, since the line itself shows
  nothing; the shire coding puts e.g. Buckinghamshire and Middlesex inside and Northumbria/Lancashire outside).
  LORO 9 regions: -0.99 to +0.90, none significant. Other outcomes null.
  Test 2 (England and Wales without County Durham, N = 558, 49 county clusters). M1 +0.84 per 10 points [-0.66, 2.35];
  M2 -0.44; M3 -0.60; M4 main -0.30 [-0.56, -0.05], p = 0.021 (per SD of royalist share -0.72 [-1.33, -0.11]).
  Wild cluster bootstrap p = 0.069 (Webb, 9,999); permutation of county values p = 0.005; Holm p = 0.042.
  Robustness: England only -0.26 p = 0.10; 1642 to 1644 only -0.27 p = 0.06; mechanical coding -0.27 p = 0.01;
  majority-royalist indicator -0.19 [-1.42, 1.04]; drop London -0.29 p = 0.02; counted results -0.66 p = 0.045;
  LORO 8 of 10 significant; leave-one-county-out 48 of 49 significant. UKIP 2015 -0.16 p = 0.01; Brexit 2019 and Reform
  2024 null. Exploratory seat-level boroughs -0.13 [-0.28, 0.02], raw 0.
  Reading: Test 1 null. Test 2: a small negative conditional association (more royalist counties slightly less Leave
  once composition is held fixed), absent in the raw and region-only models, significant with conventional clustered
  errors but not with the wild bootstrap (p = 0.07), and not with the binary coding: fragile, not robust, and in the
  opposite direction to a "Cavalier counties voted Leave" story. Reported as weak and uncertain.

## 2. Final state
- Deliverables: index.html + js/page.js (modes Leave / Danelaw / Civil War sides / Viking names; layers: line, 1640
  boroughs, county outlines, placebo lines, seat outlines, base labels; search seats, counties, boroughs; full screen);
  header.png; data/*; code/01..09; release/paper (Hotham_Civil_War_Leave.pdf, 22 pp, about 8,150 words before references
  incl. tables, abstract 241 words, 49 references, cover_note.md); release/blog (post.html, 5 figures, meta.json);
  release/zenodo; reddit/collage.py + civil-war-leave_collage.png + post.md + civil-war-leave.gif
  (/home/claude/gifs/scripts/civil-war-leave.py).
- References: the general search budget ran out during this session. Every cited work was verified either in this
  session (Rochester Cathedral Textus Roffensis bibliography for Davis 1982, Dumville 1992, Hart 1992, Downer 1972, Abrams
  2008, Cullen et al. 2011, Fellows-Jensen 2014, Kershaw 2013, Wormald 1999, Watts 2004; Zagorin 1959 page for Dodd 1952
  and Brunton and Pennington 1954; USF map pages for Gardiner 1914; Wikipedia threefold division page) or in earlier
  verified studies (beeching-leave refs.bib; Holm 1979, Cameron et al. 2008, Webb 2023, Satyanath et al. 2017, Eggers et
  al. 2015, Gelling and Cole 2000 from sibling papers). Zagorin 1959: journal confirmed (JEH, Economic History
  Association), volume and pages not seen, so omitted. Not cited because not verifiable now (listed in cover_note.md):
  Voigtlaender and Voth 2012, Fouka and Voth, Alesina and Giuliano 2015, Leslie et al. 2015, Kershaw and Royrvik 2016,
  Keele and Titiunik 2015.
- Data still wanted: Gardiner (1914) School Atlas plate "England and Wales, May 1, 1643" (etc.usf.edu/maps/pages/300/370/370.htm)
  to code territorial control by county; Brunton and Pennington (1954) national totals to check the member coding.
- QA: Playwright 1280 and 390 px, 0 console errors, no horizontal scroll; screenshots in qa/.

## 3. Independent review (2026)
- results.json reproduced exactly from 01_geo, 03_models, 04_results (scratch cache rebuilt).
- References added after online verification: Voigtlaender and Voth 2012 (QJE 127(3) 1339-1392), Fouka and Voth 2023 (APSR 117(3) 851-870),
  Alesina and Giuliano 2015 (JEL 53(4) 898-944), Leslie et al. 2015 (Nature 519, 309-314; cited for finding no clear genetic trace of the
  Danish Viking occupation), Keele and Titiunik 2015 (Political Analysis 23(1) 127-155). Zagorin 1959 volume/pages added (19(3) 376-401).
  Dumville 1992 cited as the book (chapter pages not verifiable). Rochester page author (Alexander Thomas) and "no more than seven years" wording.
- Wording: Civil War robustness count fixed in blog and page (the three non-significant checks are still negative); reddit post sample sizes;
  superlatives softened; Tables A (full, LORO, county) now referenced; collage and GIF legends moved off land; Civil War map legend explains dots and line.
