"""Build a single-page static HTML site from docs/*.md.

Layout:
  - sticky left sidebar with project title, authors, and a clickable TOC
  - main column with the 13 sections concatenated, each with an anchor id
  - small vanilla JS for scrollspy (active section highlight) and mobile toggle

Output: site/index.html + site/style.css. Self-contained.
"""
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
DOCS = ROOT / "docs"
SITE = ROOT / "site"
SITE.mkdir(exist_ok=True)

AUTHORS = ["Peiyuan Shan", "Linghang Xue", "Supawich Puengdang"]
PROJECT_TITLE = "Pair Trading Across 10 Industries"
PROJECT_SUBTITLE = "FinTech 533 Capstone"

SECTIONS = [
    ("01_strategy_overview",          "Strategy Overview"),
    ("02_market_phenomenon",          "Market Phenomenon"),
    ("03_industry_universe",          "Industry Universe & Pair Selection"),
    ("04_statistical_tests",          "Statistical Tests"),
    ("05_hedge_ratio_and_spread",     "Hedge Ratio & Spread"),
    ("06_entry_rules",                "Entry Rules"),
    ("07_exit_rules",                 "Exit Rules"),
    ("08_trade_fates",                "Trade Fates"),
    ("09_backtest_design",            "Backtest Design"),
    ("10_blotter_and_ledger",         "Blotter & Ledger"),
    ("11_performance_metrics",        "Performance Metrics"),
    ("12_strategy_monitoring",        "Strategy Monitoring"),
    ("13_when_strategy_stops_working","When the Strategy Stops Working"),
]


CSS = """
:root {
  --fg: #1a1a1a;
  --muted: #6b6b6b;
  --bg: #ffffff;
  --bg-soft: #f7f7f5;
  --accent: #0b6e4f;
  --accent-soft: #d9eee5;
  --border: #e6e6e6;
  --code-bg: #f4f4f2;
  --sidebar-w: 280px;
  --content-max: 820px;
}

* { box-sizing: border-box; }

html { scroll-behavior: smooth; }
body {
  margin: 0; padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  font-size: 16px;
  line-height: 1.65;
  color: var(--fg);
  background: var(--bg);
}

a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

/* ---------- layout ---------- */
.layout {
  display: flex;
  align-items: flex-start;
  min-height: 100vh;
}

aside.sidebar {
  width: var(--sidebar-w);
  flex-shrink: 0;
  background: var(--bg-soft);
  border-right: 1px solid var(--border);
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  padding: 28px 22px 24px;
}
aside.sidebar h1 {
  font-size: 18px;
  margin: 0 0 4px;
  letter-spacing: -0.01em;
  line-height: 1.3;
}
aside.sidebar .subtitle {
  color: var(--muted);
  font-size: 12.5px;
  margin-bottom: 14px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
aside.sidebar .authors {
  font-size: 13px;
  color: var(--fg);
  padding-bottom: 18px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 18px;
  line-height: 1.55;
}
aside.sidebar .authors strong {
  display: block;
  color: var(--muted);
  font-weight: 500;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 4px;
}

aside.sidebar nav ol {
  list-style: none;
  padding: 0;
  margin: 0;
  counter-reset: tocnum;
}
aside.sidebar nav li { margin: 0; }
aside.sidebar nav a {
  display: block;
  padding: 6px 10px 6px 12px;
  border-left: 2px solid transparent;
  color: var(--muted);
  font-size: 13.5px;
  line-height: 1.4;
  transition: color 0.12s ease, border-color 0.12s ease, background 0.12s ease;
}
aside.sidebar nav a:hover {
  color: var(--accent);
  text-decoration: none;
  background: rgba(11, 110, 79, 0.05);
}
aside.sidebar nav a.active {
  color: var(--accent);
  border-left-color: var(--accent);
  font-weight: 600;
  background: rgba(11, 110, 79, 0.07);
}
aside.sidebar nav .num {
  display: inline-block;
  width: 22px;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
  font-size: 12px;
}
aside.sidebar nav a.active .num { color: var(--accent); }

aside.sidebar .top-link {
  margin-top: 18px;
  padding-top: 14px;
  border-top: 1px solid var(--border);
  font-size: 12.5px;
}

/* ---------- main column ---------- */
main {
  flex: 1;
  min-width: 0;
  padding: 36px 40px 80px;
}
main .content {
  max-width: var(--content-max);
  margin: 0 auto;
}

main h1.section-title {
  font-size: 26px;
  margin-top: 0;
  border-bottom: 2px solid var(--accent-soft);
  padding-bottom: 8px;
}
main h2 { font-size: 19px; margin-top: 26px; }
main h3 {
  font-size: 14.5px;
  margin-top: 22px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
section.doc-section {
  padding-top: 28px;
  margin-top: 28px;
  border-top: 1px solid var(--border);
  scroll-margin-top: 16px;
}
section.doc-section:first-of-type {
  border-top: none;
  margin-top: 0;
  padding-top: 0;
}

p, li { font-size: 15.5px; }
code {
  background: var(--code-bg);
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 13.5px;
  font-family: "SF Mono", Menlo, Consolas, monospace;
}
pre {
  background: var(--code-bg);
  padding: 14px 16px;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 13.5px;
  line-height: 1.55;
  border: 1px solid var(--border);
}
pre code { background: transparent; padding: 0; }

table {
  border-collapse: collapse;
  margin: 16px 0;
  width: 100%;
  font-size: 14.5px;
}
table th, table td {
  border-bottom: 1px solid var(--border);
  padding: 8px 10px;
  text-align: left;
  vertical-align: top;
}
table th { background: var(--bg-soft); font-weight: 600; }
table tr:hover td { background: #fafafa; }

blockquote {
  border-left: 3px solid var(--accent-soft);
  padding: 4px 14px;
  margin: 16px 0;
  color: var(--muted);
}

/* ---------- figures ---------- */
main img {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 22px auto 6px;
}
main p:has(> img) {
  text-align: center;
  margin: 0;
}


/* ---------- hero / KPIs on first section ---------- */
.hero {
  padding: 28px 0 8px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 8px;
}
.hero h1 {
  font-size: 30px;
  margin: 0 0 8px;
  letter-spacing: -0.01em;
  border: none;
  padding: 0;
}
.hero .lede {
  color: var(--muted);
  font-size: 15.5px;
  max-width: 680px;
  margin: 0 0 20px;
}
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px;
  margin: 18px 0 18px;
}
.kpi {
  background: var(--bg-soft);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 14px;
}
.kpi .label {
  font-size: 11.5px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}
.kpi .value {
  font-size: 20px;
  font-weight: 600;
  color: var(--accent);
  letter-spacing: -0.01em;
}

footer.site-footer {
  border-top: 1px solid var(--border);
  background: var(--bg-soft);
  padding: 18px 24px;
  margin-top: 60px;
  color: var(--muted);
  font-size: 13px;
  text-align: center;
}

/* ---------- mobile ---------- */
.menu-toggle {
  display: none;
  position: fixed;
  top: 12px;
  left: 12px;
  z-index: 50;
  background: var(--accent);
  color: #fff;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0,0,0,0.12);
}

@media (max-width: 900px) {
  .menu-toggle { display: block; }
  aside.sidebar {
    position: fixed;
    left: -300px;
    top: 0;
    height: 100vh;
    width: 280px;
    z-index: 40;
    transition: left 0.22s ease;
    box-shadow: 4px 0 14px rgba(0,0,0,0.06);
  }
  aside.sidebar.open { left: 0; }
  main { padding: 60px 22px 60px; }
  .hero h1 { font-size: 24px; }
}
"""


JS = """
(function() {
  // --- mobile menu toggle ---
  var btn = document.getElementById('menu-toggle');
  var sidebar = document.querySelector('aside.sidebar');
  if (btn && sidebar) {
    btn.addEventListener('click', function() {
      sidebar.classList.toggle('open');
    });
    sidebar.querySelectorAll('a').forEach(function(a) {
      a.addEventListener('click', function() {
        if (window.innerWidth <= 900) sidebar.classList.remove('open');
      });
    });
  }

  // --- scrollspy: highlight active section in sidebar ---
  var sections = Array.prototype.slice.call(document.querySelectorAll('section.doc-section'));
  var links = {};
  document.querySelectorAll('aside.sidebar nav a[href^="#"]').forEach(function(a) {
    var id = a.getAttribute('href').slice(1);
    links[id] = a;
  });
  function setActive(id) {
    Object.keys(links).forEach(function(k) { links[k].classList.remove('active'); });
    if (id && links[id]) links[id].classList.add('active');
  }
  function onScroll() {
    var scrollPos = window.scrollY + 120;
    var current = sections[0] ? sections[0].id : null;
    for (var i = 0; i < sections.length; i++) {
      if (sections[i].offsetTop <= scrollPos) current = sections[i].id;
    }
    setActive(current);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('load', onScroll);
})();
"""


HERO_HTML = """
<div class="hero">
  <h1>Pair Trading Across 10 Industries</h1>
  <p class="lede">
    A statistical pair-trading strategy applied to ten US equity industries.
    We screen 386 candidate pairs by correlation, Engle&ndash;Granger cointegration,
    and ADF on the spread, then backtest a Z-score-driven entry/exit rule with
    stop-loss and timeout over three years of Interactive Brokers data.
  </p>
  <div class="kpi-grid">
    <div class="kpi"><div class="label">Backtest window</div><div class="value">2023&ndash;2026</div></div>
    <div class="kpi"><div class="label">Stocks fetched</div><div class="value">92 / 96</div></div>
    <div class="kpi"><div class="label">Pairs screened</div><div class="value">386</div></div>
    <div class="kpi"><div class="label">Pairs selected</div><div class="value">3</div></div>
    <div class="kpi"><div class="label">Trades</div><div class="value">68</div></div>
    <div class="kpi"><div class="label">Sharpe</div><div class="value">1.45</div></div>
    <div class="kpi"><div class="label">Total return</div><div class="value">+3.92%</div></div>
    <div class="kpi"><div class="label">Max drawdown</div><div class="value">&minus;0.85%</div></div>
  </div>
</div>
"""


def render_md(md_text):
    return markdown.markdown(
        md_text, extensions=["tables", "fenced_code", "sane_lists"]
    )


def strip_leading_h1(html):
    """Drop the leading <h1>...</h1> from each section's converted HTML.
    Section titles come from SECTIONS so they are stable; the <h1> in the
    markdown is redundant once the section gets its own anchor + heading."""
    return re.sub(r"^\s*<h1>.*?</h1>\s*", "", html, count=1, flags=re.DOTALL)


def build_sidebar():
    authors = "<br>".join(AUTHORS)
    items = []
    for slug, title in SECTIONS:
        n = slug.split("_")[0]
        items.append(
            f'<li><a href="#{slug}"><span class="num">{n}.</span>{title}</a></li>'
        )
    items_html = "\n      ".join(items)
    return f"""<aside class="sidebar" aria-label="Section navigation">
  <h1><a href="#top" style="color:inherit">{PROJECT_TITLE}</a></h1>
  <div class="subtitle">{PROJECT_SUBTITLE}</div>
  <div class="authors">
    <strong>Authors</strong>
    {authors}
  </div>
  <nav>
    <ol>
      {items_html}
    </ol>
  </nav>
  <div class="top-link"><a href="#top">&uarr; Back to top</a></div>
</aside>"""


def build_main():
    parts = [HERO_HTML]
    for slug, title in SECTIONS:
        md_text = (DOCS / f"{slug}.md").read_text(encoding="utf-8")
        body = strip_leading_h1(render_md(md_text))
        n = slug.split("_")[0]
        parts.append(
            f'<section class="doc-section" id="{slug}">\n'
            f'  <h1 class="section-title">{n}. {title}</h1>\n'
            f"  {body}\n"
            f"</section>"
        )
    return "\n".join(parts)


def build_page():
    authors_meta = ", ".join(AUTHORS)
    authors_footer = " &middot; ".join(AUTHORS)
    sidebar = build_sidebar()
    main_html = build_main()
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{PROJECT_TITLE} &mdash; {PROJECT_SUBTITLE}</title>
  <meta name="author" content="{authors_meta}" />
  <meta name="description" content="A statistical pair-trading strategy across 10 US equity industries. {PROJECT_SUBTITLE}." />
  <link rel="stylesheet" href="style.css" />
</head>
<body id="top">
  <button id="menu-toggle" class="menu-toggle" aria-label="Open navigation">&#9776; Sections</button>
  <div class="layout">
    {sidebar}
    <main>
      <div class="content">
        {main_html}
      </div>
      <footer class="site-footer">
        {PROJECT_TITLE} &mdash; {PROJECT_SUBTITLE} &middot; {authors_footer}
      </footer>
    </main>
  </div>
  <script>{JS}</script>
</body>
</html>
"""
    (SITE / "index.html").write_text(html, encoding="utf-8")
    print("  built index.html")


def build_css():
    (SITE / "style.css").write_text(CSS.strip() + "\n", encoding="utf-8")
    print("  built style.css")


def cleanup_old_section_pages():
    """Remove the per-section .html files from the previous multi-page build."""
    for slug, _ in SECTIONS:
        old = SITE / f"{slug}.html"
        if old.exists():
            old.unlink()
            print(f"  removed {old.name}")


if __name__ == "__main__":
    print(f"Building single-page site to {SITE}")
    cleanup_old_section_pages()
    build_css()
    build_page()
    print("Done.")
