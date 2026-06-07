"""
Generates branded PNG placeholder images for every Product and Category
that has no image yet, and attaches them to the model.

Usage:
    python manage.py generate_placeholder_images
    python manage.py generate_placeholder_images --force   # regenerate even if image exists

Output:
    media/products/<sku>.png
    media/categories/<slug>.png
"""

import hashlib
import io
import re

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont

from catalog.models import Category, Product


# Eight palette triples: (bg_top, bg_bottom, accent) — picked deterministically per item.
PALETTES = [
    ((15, 23, 42), (2, 6, 23), (56, 189, 248)),     # slate / sky
    ((30, 41, 59), (2, 6, 23), (244, 114, 182)),    # slate / pink
    ((6, 78, 59), (3, 7, 18), (52, 211, 153)),      # emerald
    ((124, 45, 18), (12, 10, 9), (251, 146, 60)),   # orange / amber
    ((49, 46, 129), (3, 7, 18), (167, 139, 250)),   # indigo / violet
    ((76, 29, 149), (3, 7, 18), (192, 132, 252)),   # purple
    ((131, 24, 67), (12, 10, 9), (249, 168, 212)),  # fuchsia
    ((54, 83, 20), (12, 10, 9), (163, 230, 53)),    # lime
]

# Category-slug → short glyph string shown in the badge circle.
CATEGORY_GLYPH = {
    "sensors": "S",
    "temperature-sensors": "T°",
    "pressure-sensors": "P",
    "proximity-sensors": "Px",
    "motion-sensors": "M",
    "gas-sensors": "G",
    "humidity-sensors": "H%",
    "distance-sensors": "D",
    "light-sensors": "L",
    "actuators": "A",
    "dc-motors": "DC",
    "servo-motors": "Sv",
    "stepper-motors": "St",
    "relays": "R",
    "solenoids": "Sol",
    "controllers": "uC",
    "arduino-boards": "Ar",
    "esp-boards": "ESP",
    "raspberry-pi-boards": "Pi",
    "plc-modules": "PLC",
    "communication-modules": "Net",
    "wifi-modules": "WiFi",
    "bluetooth-modules": "BT",
    "lora-modules": "LoRa",
    "rs485-modules": "RS",
    "power-supplies": "PWR",
    "din-rail-psu": "PSU",
    "dc-dc-converters": "DC",
}

WIDTH = 800
HEIGHT = 600


def _hash_int(text: str) -> int:
    return int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)


def _palette_for(key: str):
    return PALETTES[_hash_int(key) % len(PALETTES)]


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """Try a few common system fonts, fall back to Pillow's default bitmap font."""
    candidates = [
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "DejaVuSans.ttf",
        "Arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def _load_mono(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/cour.ttf",
        "DejaVuSansMono.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return _load_font(size)


def _wrap(text: str, max_chars: int = 22, max_lines: int = 3) -> list:
    words = re.split(r"\s+", text.strip())
    lines = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= max_chars:
            current = f"{current} {word}".strip()
        else:
            if current:
                lines.append(current)
            current = word
        if len(lines) == max_lines - 1 and len(current) > max_chars:
            current = current[: max_chars - 1] + "..."
    if current:
        lines.append(current)
    return lines[:max_lines]


def _vertical_gradient(top_rgb, bottom_rgb) -> Image.Image:
    """Build a WIDTH×HEIGHT image with a top-to-bottom linear gradient."""
    base = Image.new("RGB", (WIDTH, HEIGHT), top_rgb)
    top = Image.new("RGB", (1, HEIGHT), top_rgb)
    px = top.load()
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        px[0, y] = (
            int(top_rgb[0] + (bottom_rgb[0] - top_rgb[0]) * t),
            int(top_rgb[1] + (bottom_rgb[1] - top_rgb[1]) * t),
            int(top_rgb[2] + (bottom_rgb[2] - top_rgb[2]) * t),
        )
    base.paste(top.resize((WIDTH, HEIGHT)), (0, 0))
    return base


def _draw_grid(img: Image.Image, accent_rgb, step: int = 40, alpha: int = 18) -> None:
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    color = (*accent_rgb, alpha)
    for x in range(0, WIDTH + 1, step):
        draw.line([(x, 0), (x, HEIGHT)], fill=color, width=1)
    for y in range(0, HEIGHT + 1, step):
        draw.line([(0, y), (WIDTH, y)], fill=color, width=1)
    img.paste(overlay, (0, 0), overlay)


def _text_size(draw: ImageDraw.ImageDraw, text: str, font) -> tuple:
    """Pillow-10-safe text bbox -> (width, height)."""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def render_png(label_top: str, label_main: str, label_bottom: str, palette_key: str) -> bytes:
    bg_top, bg_bottom, accent = _palette_for(palette_key)

    img = _vertical_gradient(bg_top, bg_bottom).convert("RGBA")
    _draw_grid(img, accent)
    draw = ImageDraw.Draw(img)

    # Badge circle
    cx, cy, r = WIDTH // 2, 200, 90
    badge = Image.new("RGBA", img.size, (0, 0, 0, 0))
    badge_draw = ImageDraw.Draw(badge)
    badge_draw.ellipse(
        (cx - r, cy - r, cx + r, cy + r),
        fill=(*accent, 38),
        outline=(*accent, 220),
        width=3,
    )
    img.paste(badge, (0, 0), badge)

    # Glyph inside badge
    glyph_font = _load_font(64)
    gw, gh = _text_size(draw, label_top, glyph_font)
    draw.text(
        (cx - gw // 2, cy - gh // 2 - 6),
        label_top,
        fill=(*accent, 255),
        font=glyph_font,
    )

    # Product / category name (wrapped)
    name_font = _load_font(38)
    lines = _wrap(label_main)
    line_h = 50
    total_h = len(lines) * line_h
    start_y = 380 - total_h // 2
    for i, line in enumerate(lines):
        lw, _ = _text_size(draw, line, name_font)
        draw.text(
            (cx - lw // 2, start_y + i * line_h),
            line,
            fill=(255, 255, 255, 255),
            font=name_font,
        )

    # SKU / footer
    mono_font = _load_mono(22)
    sw, _ = _text_size(draw, label_bottom, mono_font)
    draw.text(
        (cx - sw // 2, 540),
        label_bottom,
        fill=(*accent, 240),
        font=mono_font,
    )

    # Watermark
    wm_font = _load_font(14)
    ww, _ = _text_size(draw, "AutoShop", wm_font)
    draw.text(
        (WIDTH - ww - 20, HEIGHT - 25),
        "AutoShop",
        fill=(255, 255, 255, 96),
        font=wm_font,
    )

    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG", optimize=True)
    return buf.getvalue()


class Command(BaseCommand):
    help = "Generates PNG placeholder images for products and categories that lack one."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Regenerate placeholders even for items that already have an image.",
        )

    def handle(self, *args, **options):
        force = options["force"]

        prod_count = self._handle_products(force)
        cat_count = self._handle_categories(force)

        self.stdout.write(self.style.SUCCESS(
            f"\n[OK] Generated {prod_count} product placeholders "
            f"and {cat_count} category placeholders."
        ))

    def _handle_products(self, force: bool) -> int:
        count = 0
        qs = Product.objects.select_related("category").all()
        total = qs.count()
        self.stdout.write(f"Processing {total} products...")

        for product in qs:
            if product.image and not force:
                continue

            glyph = CATEGORY_GLYPH.get(product.category.slug, "*")
            png_bytes = render_png(
                label_top=glyph,
                label_main=product.name,
                label_bottom=product.sku,
                palette_key=product.sku,
            )
            filename = f"{product.sku}.png"
            product.image.save(filename, ContentFile(png_bytes), save=True)
            count += 1

        self.stdout.write(f"  [OK] {count} product placeholders written.")
        return count

    def _handle_categories(self, force: bool) -> int:
        count = 0
        qs = Category.objects.all()
        total = qs.count()
        self.stdout.write(f"Processing {total} categories...")

        for category in qs:
            if category.image and not force:
                continue

            glyph = CATEGORY_GLYPH.get(category.slug, "*")
            png_bytes = render_png(
                label_top=glyph,
                label_main=category.name,
                label_bottom=category.slug.upper(),
                palette_key=category.slug,
            )
            filename = f"{category.slug}.png"
            category.image.save(filename, ContentFile(png_bytes), save=True)
            count += 1

        self.stdout.write(f"  [OK] {count} category placeholders written.")
        return count
