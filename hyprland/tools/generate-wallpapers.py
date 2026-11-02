#!/usr/bin/env python3
"""Render original vector artwork for horizontal and portrait 4K outputs."""
from pathlib import Path
import random

import gi
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import GdkPixbuf
from PIL import Image

OUTPUT = Path(__file__).resolve().parents[1] / "config" / "wallpapers"


def artwork(width, height):
    rng = random.Random(27)
    portrait = height > width
    cx, cy = width * 0.64, height * (0.43 if portrait else 0.49)
    radius = min(width, height) * (0.28 if portrait else 0.26)
    stars = []
    for _ in range(95):
        x, y = rng.uniform(0, width), rng.uniform(0, height)
        stars.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rng.uniform(.7, 1.6):.1f}" fill="#a9b1d6" opacity="{rng.uniform(.10, .32):.2f}"/>')
    grid = []
    horizon = height * .70
    for i in range(-8, 13):
        grid.append(f'<path d="M {width*.6:.1f} {horizon:.1f} L {i*width/7:.1f} {height}"/>')
    for i in range(1, 12):
        y = horizon + (height - horizon) * (i / 12) ** 2
        grid.append(f'<path d="M 0 {y:.1f} H {width}"/>')
    rings = []
    for factor, opacity in [(1.15, .10), (1.45, .10), (1.85, .08), (2.35, .06)]:
        rings.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{radius*factor:.1f}" fill="none" stroke="#7aa2f7" stroke-width="1.3" opacity="{opacity}"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<defs>
  <linearGradient id="base" x2=".9" y2="1"><stop stop-color="#080d1b"/><stop offset=".5" stop-color="#101426"/><stop offset="1" stop-color="#090e1b"/></linearGradient>
  <radialGradient id="blue"><stop stop-color="#466bdc" stop-opacity=".28"/><stop offset="1" stop-color="#466bdc" stop-opacity="0"/></radialGradient>
  <radialGradient id="violet"><stop stop-color="#8a52cb" stop-opacity=".23"/><stop offset="1" stop-color="#8a52cb" stop-opacity="0"/></radialGradient>
  <radialGradient id="sphere" cx=".23" cy=".14" r=".9"><stop stop-color="#384b80"/><stop offset=".36" stop-color="#182544"/><stop offset=".8" stop-color="#0c1224"/><stop offset="1" stop-color="#080d1a"/></radialGradient>
  <linearGradient id="orbit"><stop stop-color="#bb9af7" stop-opacity="0"/><stop offset=".25" stop-color="#bb9af7"/><stop offset=".55" stop-color="#7aa2f7"/><stop offset=".8" stop-color="#7dcfff"/><stop offset="1" stop-color="#7dcfff" stop-opacity="0"/></linearGradient>
  <linearGradient id="rim" x2="1" y2="1"><stop stop-color="#7dcfff" stop-opacity=".85"/><stop offset=".4" stop-color="#7aa2f7" stop-opacity=".4"/><stop offset=".7" stop-color="#bb9af7" stop-opacity=".08"/><stop offset="1" stop-color="#bb9af7" stop-opacity=".5"/></linearGradient>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="12"/></filter>
  <filter id="wideGlow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="45"/></filter>
</defs>
<rect width="{width}" height="{height}" fill="url(#base)"/>
<ellipse cx="{cx-radius*.5}" cy="{cy-radius*.3}" rx="{radius*2.5}" ry="{radius*2.2}" fill="url(#blue)"/>
<ellipse cx="{cx+radius*.7}" cy="{cy+radius*.7}" rx="{radius*2.3}" ry="{radius*2.8}" fill="url(#violet)"/>
{''.join(stars)}
<g stroke="#7aa2f7" stroke-width="1" opacity=".055" fill="none">{''.join(grid)}</g>
{''.join(rings)}
<g transform="rotate(-25 {cx} {cy})">
 <ellipse cx="{cx}" cy="{cy}" rx="{radius*1.8}" ry="{radius*.5}" fill="none" stroke="url(#orbit)" stroke-width="12" opacity=".28" filter="url(#glow)"/>
 <ellipse cx="{cx}" cy="{cy}" rx="{radius*1.8}" ry="{radius*.5}" fill="none" stroke="url(#orbit)" stroke-width="2.2" opacity=".6"/>
</g>
<circle cx="{cx}" cy="{cy}" r="{radius*1.01}" fill="none" stroke="#7aa2f7" stroke-width="15" opacity=".20" filter="url(#wideGlow)"/>
<circle cx="{cx}" cy="{cy}" r="{radius}" fill="url(#sphere)" stroke="url(#rim)" stroke-width="2.5"/>
<g transform="rotate(-25 {cx} {cy})" fill="none" stroke="url(#orbit)">
 <path d="M {cx-radius*1.8} {cy} A {radius*1.8} {radius*.5} 0 0 0 {cx+radius*1.8} {cy}" stroke-width="13" opacity=".40" filter="url(#glow)"/>
 <path d="M {cx-radius*1.8} {cy} A {radius*1.8} {radius*.5} 0 0 0 {cx+radius*1.8} {cy}" stroke-width="3" opacity=".95"/>
</g>
<path d="M {-width*.1} {height*.94} C {width*.35} {height*.70}, {width*.6} {height*.98}, {width*1.1} {height*.60}" fill="none" stroke="url(#orbit)" stroke-width="2" opacity=".13"/>
</svg>'''


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name, size in [("landscape", (3840, 2160)), ("portrait", (2160, 3840))]:
        source = OUTPUT / f"orbit-{name}.svg"
        source.write_text(artwork(*size))
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(str(source))
        pixbuf.savev(str(source.with_suffix(".png")), "png", ["compression"], ["8"])
        print(source.with_suffix(".png"))
        variants = {
            "violet": {"7aa2f7": "bb9af7", "7dcfff": "f4a8ff", "466bdc": "8052c9", "8a52cb": "644fe0"},
            "aurora": {"7aa2f7": "73daca", "bb9af7": "7aa2f7", "7dcfff": "9ece6a", "466bdc": "2d858b", "8a52cb": "3469ad"},
            "dusk": {"7aa2f7": "e0af68", "bb9af7": "f7768e", "7dcfff": "ff9e64", "466bdc": "99655d", "8a52cb": "a34f85"},
        }
        for variant, colors in variants.items():
            # Replace simultaneously so a target color cannot be replaced twice.
            import re
            vector = re.sub("|".join(colors), lambda match: colors[match.group()], artwork(*size))
            variant_source = OUTPUT / f"{variant}-{name}.svg"
            variant_source.write_text(vector)
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(str(variant_source))
            pixbuf.savev(str(variant_source.with_suffix(".png")), "png", ["compression"], ["8"])
    preview = Image.new("RGB", (1296, 572), "#080d1b")
    for name, box in [("landscape", (16, 16, 960, 540)), ("portrait", (992, 16, 288, 540))]:
        image = Image.open(OUTPUT / f"orbit-{name}.png").convert("RGB")
        image.thumbnail((box[2], box[3]), Image.Resampling.LANCZOS)
        preview.paste(image, (box[0], box[1]))
    preview.save(OUTPUT / "preview.png")


if __name__ == "__main__":
    main()
