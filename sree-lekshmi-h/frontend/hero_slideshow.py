"""Reusable hero slideshow for RecipePilot (Streamlit).

Images come from TheMealDB (strMealThumb). The URLs are fetched server-side,
cached, and handed to a small HTML/JS component that runs the slideshow in
the browser (fade transitions, arrows, dots, 5 s autoplay, swipe).

Usage:
    from hero_slideshow import render_hero_slideshow
    render_hero_slideshow()
"""

import json
from concurrent.futures import ThreadPoolExecutor

import requests
import streamlit as st
import streamlit.components.v1 as components

THEMEALDB_RANDOM_URL = "https://www.themealdb.com/api/json/v1/1/random.php"
SLIDE_COUNT = 6
MIN_SLIDES = 3          # below this we treat the fetch as failed
REQUEST_TIMEOUT = 5     # seconds
CACHE_TTL = 30 * 60     # keep the same slides for 30 minutes


def _fetch_one_meal():
    """Return {'id', 'name', 'img'} for one random meal, or None on any failure."""
    try:
        resp = requests.get(THEMEALDB_RANDOM_URL, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        meal = (resp.json().get("meals") or [None])[0]
    except (requests.RequestException, ValueError):
        return None
    if not meal:
        return None
    img = (meal.get("strMealThumb") or "").strip()
    if not img.startswith("http"):
        return None
    return {"id": meal.get("idMeal"), "name": meal.get("strMeal") or "", "img": img}


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def _fetch_slides_cached(count: int):
    """Fetch `count` distinct meals. Raises if too few came back, so a
    failed fetch is never cached."""
    slides, seen = [], set()
    with ThreadPoolExecutor(max_workers=count + 2) as pool:
        for _ in range(3):  # a few rounds to replace duplicates/failures
            needed = count - len(slides)
            if needed <= 0:
                break
            for meal in pool.map(lambda _: _fetch_one_meal(), range(needed + 2)):
                if meal and meal["id"] not in seen and len(slides) < count:
                    seen.add(meal["id"])
                    slides.append({"id": meal["id"], "name": meal["name"], "img": meal["img"]})
    if len(slides) < MIN_SLIDES:
        raise RuntimeError("TheMealDB returned too few images")
    return slides


def get_hero_slides(count: int = SLIDE_COUNT):
    """Slides for the hero; an empty list means the browser shows gradient fallbacks."""
    try:
        return _fetch_slides_cached(count)
    except Exception:
        return []


_HERO_HTML = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap" rel="stylesheet">
<style>
  :root {
    --saffron: #F2B134;
    --saffron-deep: #E09B12;
    --ink: #1B1410;
    --cream: #FFF8EC;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; height: 100%; background: transparent; }
  .hero {
    position: relative; width: 100%; height: 100%;
    overflow: hidden; border-radius: 18px; background: var(--ink);
    font-family: "DM Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
    color: var(--cream);
  }
  .slide {
    position: absolute; inset: 0; opacity: 0;
    background-size: cover; background-position: center;
    transition: opacity 1.2s ease-in-out;
  }
  .slide.active { opacity: 1; z-index: 1; }
  .slide.active .photo { animation: drift 9s ease-out forwards; }
  .photo { position: absolute; inset: 0; background: inherit; transform: scale(1); }
  @keyframes drift { from { transform: scale(1); } to { transform: scale(1.06); } }

  .overlay {
    position: absolute; inset: 0; z-index: 2; pointer-events: none;
    background:
      linear-gradient(90deg, rgba(27,20,16,.72) 0%, rgba(27,20,16,.38) 55%, rgba(27,20,16,.12) 100%),
      linear-gradient(0deg, rgba(27,20,16,.55) 0%, rgba(27,20,16,0) 40%);
  }
  .content {
    position: absolute; z-index: 3; left: clamp(24px, 6vw, 80px);
    right: clamp(24px, 6vw, 80px); top: 50%; transform: translateY(-56%);
    max-width: 640px; animation: rise .9s cubic-bezier(.2,.7,.2,1) both;
  }
  @keyframes rise { from { opacity: 0; transform: translateY(-46%); } to { opacity: 1; transform: translateY(-56%); } }
  h1 {
    margin: 0 0 18px; font-family: "Fraunces", Georgia, "Times New Roman", serif;
    font-weight: 700; font-size: clamp(1.8rem, 4.4vw, 3.1rem);
    line-height: 1.05; letter-spacing: -0.01em;
    text-shadow: 0 2px 18px rgba(0,0,0,.35);
  }
  a.cta {
    display: inline-block; padding: 11px 26px; border-radius: 999px;
    background: var(--saffron); color: var(--ink); font-weight: 600;
    font-size: .98rem; text-decoration: none;
    box-shadow: 0 8px 24px rgba(242,177,52,.35);
    transition: transform .2s ease, background .2s ease, box-shadow .2s ease;
  }
  a.cta:hover { transform: translateY(-2px); background: var(--saffron-deep); box-shadow: 0 12px 28px rgba(242,177,52,.45); }
  a.cta:focus-visible, .arrow:focus-visible, .dot:focus-visible { outline: 3px solid #fff; outline-offset: 3px; }

  .arrow {
    position: absolute; z-index: 4; top: 50%; transform: translateY(-50%);
    width: 40px; height: 40px; border-radius: 50%; border: 1px solid rgba(255,255,255,.35);
    background: rgba(27,20,16,.38); color: #fff; font-size: 18px; line-height: 1;
    cursor: pointer; backdrop-filter: blur(4px);
    transition: background .2s ease, transform .2s ease;
  }
  .arrow:hover { background: rgba(27,20,16,.65); transform: translateY(-50%) scale(1.06); }
  .arrow.prev { left: 14px; } .arrow.next { right: 14px; }

  .footer {
    position: absolute; z-index: 4; left: clamp(24px, 6vw, 80px); right: clamp(24px, 6vw, 80px);
    bottom: 12px; display: flex; align-items: center; justify-content: space-between; gap: 16px;
  }
  .dots { display: flex; gap: 10px; }
  .dot {
    width: 9px; height: 9px; padding: 0; border-radius: 999px; border: 0; cursor: pointer;
    background: rgba(255,255,255,.5); transition: width .3s ease, background .3s ease;
  }
  .dot.active { width: 28px; background: var(--saffron); }
  .caption { font-size: .85rem; color: rgba(255,248,236,.85); text-align: right;
             white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

  /* gradient fallbacks when an image is missing or fails to load */
  .slide.fb0 { background: linear-gradient(135deg, #7A3E12, #C9791B 55%, #F2B134); }
  .slide.fb1 { background: linear-gradient(135deg, #2F4A2A, #5E8B3E 55%, #C7B54A); }
  .slide.fb2 { background: linear-gradient(135deg, #5A1F1F, #A8412F 55%, #E58B4D); }
  .slide.fb3 { background: linear-gradient(135deg, #1F3A4A, #3F7C8C 55%, #D9B26A); }

  @media (max-width: 600px) {
    .arrow { width: 34px; height: 34px; font-size: 15px; }
    .arrow.prev { left: 8px; } .arrow.next { right: 8px; }
    .overlay { background: linear-gradient(0deg, rgba(27,20,16,.8) 0%, rgba(27,20,16,.5) 60%, rgba(27,20,16,.35) 100%); }
    .caption { display: none; }
    .footer { justify-content: center; }
    h1 { margin-bottom: 14px; }
  }
  @media (prefers-reduced-motion: reduce) {
    .slide { transition: none; }
    .slide.active .photo, .content { animation: none; }
    .content { transform: translateY(-56%); }
  }
</style>

<section class="hero" id="hero" aria-roledescription="carousel" aria-label="Featured dishes">
  <div id="slides"></div>
  <div class="overlay"></div>
  <div class="content">
    <h1>Discover. Cook. Enjoy.</h1>
    <a class="cta" id="cta" href="__TARGET__" target="_top">Explore Recipes</a>
  </div>
  <button class="arrow prev" id="prev" aria-label="Previous slide">&#10094;</button>
  <button class="arrow next" id="next" aria-label="Next slide">&#10095;</button>
  <div class="footer">
    <div class="dots" id="dots" role="tablist"></div>
    <div class="caption" id="caption" aria-live="polite"></div>
  </div>
</section>

<script>
(function () {
  var INTERVAL = __INTERVAL__;
  var data = __SLIDES__;
  if (!data.length) { data = [{img: "", name: ""}, {img: "", name: ""}, {img: "", name: ""}]; }

  var slidesEl = document.getElementById("slides");
  var dotsEl = document.getElementById("dots");
  var captionEl = document.getElementById("caption");
  var hero = document.getElementById("hero");
  var cta = document.getElementById("cta");
  var slides = [], dots = [], current = 0, timer = null;

  // Slightly shorter banner on phones (the iframe is same-origin, so it can resize itself)
  function fit() {
    try {
      var f = window.frameElement;
      if (f) { f.style.height = (window.innerWidth <= 600 ? __HM__ : __H__) + "px"; }
    } catch (err) { /* keep the default height */ }
  }
  window.addEventListener("resize", fit);
  fit();

  data.forEach(function (item, i) {
    var s = document.createElement("div");
    s.className = "slide fb" + (i % 4);
    s.setAttribute("role", "group");
    s.setAttribute("aria-label", (i + 1) + " of " + data.length);
    var photo = document.createElement("div");
    photo.className = "photo";
    if (item.img) {
      photo.style.backgroundImage = "url('" + item.img + "')";
      photo.style.backgroundSize = "cover";
      photo.style.backgroundPosition = "center";
      var probe = new Image();
      probe.onerror = function () { photo.style.backgroundImage = "none"; };
      probe.src = item.img;
    }
    s.appendChild(photo);
    slidesEl.appendChild(s);
    slides.push(s);

    var d = document.createElement("button");
    d.className = "dot";
    d.setAttribute("aria-label", "Go to slide " + (i + 1));
    d.addEventListener("click", function () { go(i, true); });
    dotsEl.appendChild(d);
    dots.push(d);
  });

  function go(i, user) {
    current = (i + slides.length) % slides.length;
    slides.forEach(function (s, k) { s.classList.toggle("active", k === current); });
    dots.forEach(function (d, k) { d.classList.toggle("active", k === current); });
    var it = data[current];
    captionEl.textContent = it.name || "";
    cta.href = "__TARGET__" + (it.id
      ? "?meal_id=" + encodeURIComponent(it.id) + "&meal=" + encodeURIComponent(it.name)
      : "");
    if (user) restart();
  }
  function start() { stop(); timer = setInterval(function () { go(current + 1); }, INTERVAL); }
  function stop() { if (timer) { clearInterval(timer); timer = null; } }
  function restart() { start(); }

  document.getElementById("prev").addEventListener("click", function () { go(current - 1, true); });
  document.getElementById("next").addEventListener("click", function () { go(current + 1, true); });
  hero.addEventListener("mouseenter", stop);
  hero.addEventListener("mouseleave", start);
  document.addEventListener("keydown", function (e) {
    if (e.key === "ArrowLeft") go(current - 1, true);
    if (e.key === "ArrowRight") go(current + 1, true);
  });

  // touch swipe
  var x0 = null;
  hero.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; stop(); }, {passive: true});
  hero.addEventListener("touchend", function (e) {
    if (x0 !== null) {
      var dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 40) go(current + (dx < 0 ? 1 : -1), true); else start();
    }
    x0 = null;
  });

  // Streamlit sandboxes component iframes (no top navigation), so a plain
  // target="_top" link is blocked. The iframe is same-origin, so build the link
  // in the parent page and click it there; fall back to a new tab.
  cta.addEventListener("click", function (e) {
    e.preventDefault();
    var rel = cta.getAttribute("href");
    try {
      var pdoc = window.parent.document;
      var url = new URL(rel, window.parent.location.href).href;
      var a = pdoc.createElement("a");
      a.href = url; a.target = "_self";
      pdoc.body.appendChild(a); a.click(); pdoc.body.removeChild(a);
    } catch (err) {
      window.open(rel, "_blank");
    }
  });

  go(0);
  start();
})();
</script>
"""


def render_hero_slideshow(
    height: int = 320,
    mobile_height: int = 280,
    interval_ms: int = 5000,
    target_page: str = "Recipe_Finder",
):
    """Render the wide, short hero slideshow.

    target_page is the URL slug of the page the button opens
    (pages/1_Recipe_Finder.py -> "Recipe_Finder"). The button adds
    ?meal_id=<TheMealDB id>&meal=<name> for the slide currently showing.
    """
    slides = get_hero_slides()
    html = (
        _HERO_HTML
        .replace("__SLIDES__", json.dumps(slides))
        .replace("__INTERVAL__", str(int(interval_ms)))
        .replace("__TARGET__", target_page)
        .replace("__HM__", str(int(mobile_height)))
        .replace("__H__", str(int(height)))
    )
    # st.components.v1.html is deprecated in newer Streamlit; use st.iframe when available.
    if hasattr(st, "iframe"):
        st.iframe(html, height=height)
    else:
        components.html(html, height=height)