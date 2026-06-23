#!/usr/bin/env python3
"""Generate Best Solution branded badge assets (favicon, apple-touch-icon, OG image).

Renders the purple/gold "BEST SOLUTION" flyer-style badge with a faceted gold
diamond + "Professional Jewelry & Glass Polish" tagline. Pure-SVG -> PNG via
cairosvg so the artwork is reproducible from source.
"""
import cairosvg
from PIL import Image
import io
import os

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Brand palette (matches index.html :root tokens)
PURPLE_DEEP = "#3B1473"
PURPLE      = "#4C1D95"
PURPLE_GLOW = "#7C3AED"
GOLD        = "#D4A017"
GOLD_BRIGHT = "#FFD700"
GOLD_LITE   = "#FFE680"
GOLD_SOFT   = "#E8C84A"
GOLD_DARK   = "#A6760A"
CREAM       = "#FBF7EF"


def defs():
    return f"""
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0"   stop-color="{PURPLE_GLOW}"/>
      <stop offset="0.55" stop-color="{PURPLE}"/>
      <stop offset="1"   stop-color="{PURPLE_DEEP}"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.42" r="0.65">
      <stop offset="0"   stop-color="#9B5BF0" stop-opacity="0.85"/>
      <stop offset="0.6" stop-color="{PURPLE}" stop-opacity="0.25"/>
      <stop offset="1"   stop-color="{PURPLE_DEEP}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="gemglow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0"   stop-color="{GOLD_BRIGHT}" stop-opacity="0.55"/>
      <stop offset="1"   stop-color="{GOLD_BRIGHT}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="gTable" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{GOLD_LITE}"/>
      <stop offset="1" stop-color="{GOLD_BRIGHT}"/>
    </linearGradient>
    <linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{GOLD_BRIGHT}"/>
      <stop offset="1" stop-color="{GOLD}"/>
    </linearGradient>
  </defs>"""


def diamond(cx, cy, scale):
    """Faceted brilliant-cut gem, ~100x100 design units, centred on (cx,cy)."""
    tx = cx - 50 * scale
    ty = cy - 50 * scale
    facets = [
        # pts, fill
        ("30,8 70,8 77,32 23,32",  "url(#gTable)"),  # table
        ("30,8 23,32 10,32",       GOLD_SOFT),        # crown L
        ("70,8 90,32 77,32",       GOLD_SOFT),        # crown R
        ("10,32 23,32 50,92",      GOLD_DARK),        # pavilion outer L
        ("23,32 50,32 50,92",      "#C99A12"),        # pavilion L
        ("50,32 77,32 50,92",      GOLD_SOFT),        # pavilion R
        ("77,32 90,32 50,92",      GOLD_DARK),        # pavilion outer R
    ]
    parts = [f'<g transform="translate({tx:.2f},{ty:.2f}) scale({scale:.4f})">']
    # soft glow halo behind gem
    parts.append('<ellipse cx="50" cy="50" rx="62" ry="62" fill="url(#gemglow)"/>')
    for pts, fill in facets:
        parts.append(f'<polygon points="{pts}" fill="{fill}"/>')
    # girdle + crown facet lines for sparkle
    parts.append('<polyline points="10,32 90,32" fill="none" stroke="#FFF3C0" '
                 'stroke-width="0.8" stroke-opacity="0.7"/>')
    parts.append('<polyline points="23,32 30,8 70,8 77,32" fill="none" '
                 'stroke="#FFF3C0" stroke-width="0.8" stroke-opacity="0.55"/>')
    parts.append('<polyline points="23,32 50,92 77,32" fill="none" '
                 'stroke="#A6760A" stroke-width="0.8" stroke-opacity="0.6"/>')
    # outline
    parts.append('<polygon points="30,8 70,8 90,32 50,92 10,32" fill="none" '
                 'stroke="#FFF7D6" stroke-width="1.6" stroke-linejoin="round"/>')
    # bright sparkle on table
    parts.append('<polygon points="34,11 47,11 41,16" fill="#FFFFFF" fill-opacity="0.55"/>')
    parts.append('</g>')
    return "".join(parts)


def square_badge(size, with_text=True):
    s = size
    r = s * 0.22
    pad = s * 0.05
    ring = s * 0.085
    gem_cy = s * (0.40 if with_text else 0.50)
    gem_scale = (s * 0.0040) if with_text else (s * 0.0058)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" '
           f'viewBox="0 0 {s} {s}">', defs()]
    svg.append(f'<rect width="{s}" height="{s}" rx="{r}" fill="url(#bg)"/>')
    svg.append(f'<rect width="{s}" height="{s}" rx="{r}" fill="url(#glow)"/>')
    # inner gold ring frame
    svg.append(f'<rect x="{ring}" y="{ring}" width="{s-2*ring}" height="{s-2*ring}" '
               f'rx="{r*0.7}" fill="none" stroke="url(#gold)" '
               f'stroke-width="{max(1, s*0.012)}" stroke-opacity="0.9"/>')
    svg.append(diamond(s * 0.5, gem_cy, gem_scale))
    if with_text:
        fs = s * 0.165
        svg.append(
            f'<text x="{s*0.5}" y="{s*0.715}" text-anchor="middle" '
            f'font-family="Oswald" font-weight="700" font-size="{fs}" '
            f'letter-spacing="{s*0.004}" fill="#FFFFFF">BEST</text>')
        svg.append(
            f'<text x="{s*0.5}" y="{s*0.715+fs*0.92}" text-anchor="middle" '
            f'font-family="Oswald" font-weight="700" font-size="{fs}" '
            f'letter-spacing="{s*0.004}" fill="#FFFFFF">SOLUTION</text>')
        svg.append(
            f'<text x="{s*0.5}" y="{s*0.94}" text-anchor="middle" '
            f'font-family="Oswald" font-weight="600" font-size="{s*0.052}" '
            f'letter-spacing="{s*0.012}" fill="{GOLD_BRIGHT}">'
            f'JEWELRY &amp; GLASS POLISH</text>')
    svg.append('</svg>')
    return "".join(svg)


def og_image(w=1200, h=630):
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
           f'viewBox="0 0 {w} {h}">', defs()]
    svg.append(f'<rect width="{w}" height="{h}" fill="url(#bg)"/>')
    svg.append(f'<rect width="{w}" height="{h}" fill="url(#glow)"/>')
    # gold frame
    m = 28
    svg.append(f'<rect x="{m}" y="{m}" width="{w-2*m}" height="{h-2*m}" rx="22" '
               f'fill="none" stroke="url(#gold)" stroke-width="3" stroke-opacity="0.85"/>')
    # diamond
    svg.append(diamond(w * 0.5, h * 0.30, 1.95))
    # wordmark
    svg.append(
        f'<text x="{w*0.5}" y="{h*0.70}" text-anchor="middle" font-family="Oswald" '
        f'font-weight="700" font-size="148" letter-spacing="6" fill="#FFFFFF">'
        f'BEST SOLUTION</text>')
    # gold rule
    svg.append(f'<rect x="{w*0.5-300}" y="{h*0.745}" width="600" height="3" '
               f'fill="url(#gold)"/>')
    # tagline
    svg.append(
        f'<text x="{w*0.5}" y="{h*0.86}" text-anchor="middle" font-family="Oswald" '
        f'font-weight="600" font-size="40" letter-spacing="7" fill="{GOLD_BRIGHT}">'
        f'PROFESSIONAL JEWELRY &amp; GLASS POLISH</text>')
    svg.append('</svg>')
    return "".join(svg)


def render_png(svg, path, w, h):
    cairosvg.svg2png(bytestring=svg.encode(), write_to=path,
                     output_width=w, output_height=h)
    print("wrote", path)


def main():
    # OG / Twitter card
    render_png(og_image(), os.path.join(OUT, "og-image.png"), 1200, 630)

    # Apple touch icon (with wordmark, legible at 180)
    render_png(square_badge(1024, with_text=True),
               os.path.join(OUT, "apple-touch-icon.png"), 180, 180)

    # High-res logo for reuse
    render_png(square_badge(1024, with_text=True),
               os.path.join(OUT, "logo-badge.png"), 1024, 1024)

    # Favicon: clean diamond-only mark, crisp at small sizes
    fav_svg = square_badge(512, with_text=False)
    with open(os.path.join(OUT, "favicon.svg"), "w") as f:
        f.write(fav_svg)
    print("wrote favicon.svg")
    render_png(fav_svg, os.path.join(OUT, "favicon-32.png"), 32, 32)

    # favicon.ico (16/32/48)
    imgs = []
    for px in (16, 32, 48):
        buf = io.BytesIO()
        cairosvg.svg2png(bytestring=fav_svg.encode(), write_to=buf,
                         output_width=px, output_height=px)
        buf.seek(0)
        imgs.append(Image.open(buf).convert("RGBA"))
    imgs[0].save(os.path.join(OUT, "favicon.ico"), format="ICO",
                 sizes=[(16, 16), (32, 32), (48, 48)],
                 append_images=imgs[1:])
    print("wrote favicon.ico")


if __name__ == "__main__":
    main()
