**Title:** [OC] Seats on the Danelaw side of Alfred and Guthrum's line voted Leave by 6.9 points more. Compared with similar places, the gap is -0.2.

**Body:**

People often set the 2016 referendum map beside the Danelaw or the Civil War. I tested the Danelaw across England's 533 constituencies and the Civil War across 558 seats in England and Wales, with the plan written down before running any model.

- Danelaw side of the line (Thames, Lea, Bedford, Ouse, Watling Street to Chester): 56.9% Leave vs 50.0%.
- Comparing seats with similar places in the same region (density, age, degrees, ethnicity, jobs, housing): -0.16 points, 95% interval -1.8 to 1.5.
- The line is real in one way: 98% of the 1,100 English settlements (Wikidata) ending -by, -thorpe, -thwaite or -toft are on the Danelaw side.
- Civil War: 201 of 507 seats elected in 1640 had members who later joined the King. Counties with more royalist members were, if anything, very slightly less Leave once like is compared with like (-0.30 points per 10 points of royalist share). That is small and fragile: the wild cluster bootstrap p is 0.07 and 3 of 8 checks lose significance.

Interactive map with the line, the 1640 boroughs and every seat: https://maps.tristanhotham.com/civil-war-leave/

**Source comment:**

Data: Leave estimates by constituency, Hanretty (2017); 2011 census (ONS, OGL); List of MPs elected to the English Parliament in 1640 (Wikipedia, CC BY-SA 4.0); Wikidata settlements (CC0). Method: OLS with region fixed effects and census controls, a boundary comparison along the line, placebo lines, wild cluster bootstrap; plan written before the analysis. Tools: Python (pandas, statsmodels, geopandas, matplotlib), MapLibre. Paper and code: https://github.com/Tristan-Hotham/civil-war-leave
