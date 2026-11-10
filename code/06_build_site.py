"""Step 6. index.html from code/page_template.html and code/page.css, filled from data/results.json, with the full-screen
snippet. 10.5281/zenodo.24104516, https://doi.org/10.5281/zenodo.24104516 and https://blog.tristanhotham.com/2026/10/31/civil-war-leave/ are left for the publisher to fill."""
from common import *

R = jload(f"{DATA}/results.json")
KEEP = {"DOI", "DOI_URL", "BLOG_URL"}
# facts stated in words on the page, checked against the data
assert R["lp"]["counties_none"] == ["Bedfordshire", "Denbighshire", "Essex", "Middlesex"], R["lp"]["counties_none"]
bal = R["t1"]["rd"]["balance"]
for v, sign in (("ldens", -1), ("lcity", 1), ("pct_degree", -1)):
    assert bal[v]["p"] < 0.05 and (bal[v]["b"] > 0) == (sign > 0), v
assert R["t1"]["rd"]["placebo_sw"]["p"] < 0.05 and R["t1"]["rd"]["scand"]["p"] < 0.05
assert R["t1"]["robust_summary"]["sig"] == ["Exposure: the 15 Danelaw shires of the medieval shire lists"]
assert R["t2"]["robust_summary"]["n"] - R["t2"]["robust_summary"]["n_sig"] == 3
assert R["t2"]["outcomes"]["ukip15"]["p"] < 0.05 and R["t2"]["outcomes"]["brexit_19"]["p"] > 0.05 and R["t2"]["outcomes"]["reform24"]["p"] > 0.05
assert abs(R["t2"]["middlesex_adj"]) < 1 and R["desc1"]["comp"]["pct_whitebrit"] > 0 and R["desc1"]["comp"]["pct_degree"] < 0
assert R["t2"]["county_min_leave"] == "Middlesex"
t = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
t = t.replace("{{CSS}}", open(os.path.join(ROOT, "code", "page.css"), encoding="utf-8").read())
t = t.replace("{{FULLSCREEN}}", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
t = t.replace("{{REPO}}", REPO).replace("{{AI}}", AI).replace("{{BYLINE}}", BYLINE).replace("{{VERSION}}", "2026a")
t = re.sub(r"\{\{([^{}|]+)(\|(\w+))?\}\}", lambda m: m.group(0) if m.group(1) in KEEP else fmt(get(R, m.group(1)), m.group(3)), t)
assert set(re.findall(r"\{\{([^}]+)\}\}", t)) <= KEEP, set(re.findall(r"\{\{([^}]+)\}\}", t))
vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", t, flags=re.S)
for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv", "pre-registered"):
    assert bad not in vis, bad
assert '<script src="https://maps.tristanhotham.com/assets/site-nav.js" defer></script>\n</body>' in t
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(t)
print("index.html", len(t) // 1024, "KB")
