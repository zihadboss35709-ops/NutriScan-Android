#!/usr/bin/env python3
"""
NutriScan AI — Android icon generator
======================================
Generates PNG launcher icons for all density buckets using only Python
built-ins (no Pillow or other dependencies required).

Run before building locally:
    python3 generate_icons.py

The GitHub Actions workflow runs this automatically.
"""
import os
import struct
import zlib
import math


# ── Brand colours ────────────────────────────────────────────────────────────
BG_COLOR   = (27, 94, 32)    # #1B5E20  deep green background
RING_COLOR = (46, 125, 50)   # #2E7D32  slightly lighter ring
ICON_COLOR = (255, 255, 255) # #FFFFFF  white icon

# ── Density → size (px) ──────────────────────────────────────────────────────
DENSITIES = {
    'mdpi':    48,
    'hdpi':    72,
    'xhdpi':   96,
    'xxhdpi':  144,
    'xxxhdpi': 192,
}

BASE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'android', 'app', 'src', 'main', 'res',
)


# ── PNG helpers ───────────────────────────────────────────────────────────────

def _chunk(tag: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(tag + data) & 0xFFFFFFFF
    return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', crc)


def _make_png(pixels: list[list[tuple[int, int, int]]], width: int, height: int) -> bytes:
    """Encode a 2-D pixel grid (RGB tuples) as a minimal PNG."""
    signature = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr = _chunk(b'IHDR', ihdr_data)

    raw_rows = b''
    for row in pixels:
        raw_rows += b'\x00'  # filter type None
        for r, g, b in row:
            raw_rows += bytes([r, g, b])

    idat = _chunk(b'IDAT', zlib.compress(raw_rows, 9))
    iend = _chunk(b'IEND', b'')
    return signature + ihdr + idat + iend


# ── Pixel drawing utilities ───────────────────────────────────────────────────

def _blend(c1, c2, t):
    """Linear blend between c1 and c2 at fraction t."""
    return tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3))


def _circle_aa(cx, cy, r, x, y):
    """Anti-aliased coverage for a filled circle at pixel (x, y)."""
    dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    if dist <= r - 1:
        return 1.0
    if dist >= r + 0.5:
        return 0.0
    return max(0.0, r + 0.5 - dist)


def _ring_aa(cx, cy, r_out, r_in, x, y):
    out = _circle_aa(cx, cy, r_out, x, y)
    inn = _circle_aa(cx, cy, r_in, x, y)
    return max(0.0, out - inn)


def _make_icon_pixels(size: int) -> list[list[tuple[int, int, int]]]:
    """Draw the NutriScan icon: green background disc + white fork."""
    cx = cy = size / 2
    r_bg   = size * 0.48            # background circle
    r_ring = size * 0.38            # inner ring (lighter shade)
    r_in   = size * 0.30

    pixels = []
    for y in range(size):
        row = []
        for x in range(size):
            # Background (fill everything with BG_COLOR first)
            px = BG_COLOR

            # Lighter ring
            ring_cov = _ring_aa(cx, cy, r_ring, r_in, x, y)
            if ring_cov > 0:
                px = _blend(px, RING_COLOR, ring_cov)

            # ── Fork (simplified, pixel art) ─────────────────────────────
            # Tines: three thin vertical bars in upper 45% of the circle
            tine_w  = max(1, size // 20)
            tine_h  = int(size * 0.26)
            tine_y0 = int(size * 0.18)
            tine_y1 = tine_y0 + tine_h

            left_x   = int(cx - size * 0.10)
            mid_x    = int(cx)
            right_x  = int(cx + size * 0.10)

            def _in_tine(tx):
                return tx - tine_w // 2 <= x <= tx + tine_w // 2 and tine_y0 <= y <= tine_y1

            # Handle: centred, from bottom of tines to 75% of circle
            handle_w = max(2, size // 12)
            handle_y0 = tine_y1
            handle_y1 = int(size * 0.76)
            in_handle = (int(cx - handle_w // 2) <= x <= int(cx + handle_w // 2)
                         and handle_y0 <= y <= handle_y1)

            # Cross-bar connecting tines at bottom of tine region
            bar_y = tine_y1 - max(1, size // 20)
            in_bar = (left_x - tine_w // 2 <= x <= right_x + tine_w // 2
                      and bar_y <= y <= tine_y1)

            if (_in_tine(left_x) or _in_tine(mid_x) or _in_tine(right_x)
                    or in_handle or in_bar):
                # Only draw fork inside the background circle
                bg_cov = _circle_aa(cx, cy, r_bg, x, y)
                if bg_cov > 0:
                    px = _blend(px, ICON_COLOR, 0.95 * bg_cov)

            # Clip to background circle (anti-aliased edge)
            bg_cov = _circle_aa(cx, cy, r_bg, x, y)
            if bg_cov < 1.0:
                px = _blend(BG_COLOR, px, bg_cov)

            row.append(px)
        pixels.append(row)
    return pixels


# ── Main ─────────────────────────────────────────────────────────────────────

def generate():
    for density, size in DENSITIES.items():
        out_dir = os.path.join(BASE, f'mipmap-{density}')
        os.makedirs(out_dir, exist_ok=True)

        pixels = _make_icon_pixels(size)
        png_bytes = _make_png(pixels, size, size)

        for name in ('ic_launcher.png', 'ic_launcher_round.png'):
            path = os.path.join(out_dir, name)
            with open(path, 'wb') as f:
                f.write(png_bytes)

        print(f'  ✓ mipmap-{density}  ({size}×{size} px)')

    print('\nIcons generated successfully.')


if __name__ == '__main__':
    print('Generating NutriScan AI launcher icons...\n')
    generate()
