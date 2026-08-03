#!/usr/bin/env python3
"""Render the project ER diagram as a presentation-ready PNG."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "open_data_erd.png"

SCALE = 2
WIDTH, HEIGHT = 2400, 1350

NAVY = "#172554"
INDIGO = "#4F46E5"
ORANGE = "#F97316"
SLATE = "#334155"
MUTED = "#64748B"
BG = "#F8FAFC"
SOURCE_FILL = "#EEF2FF"
DERIVED_FILL = "#FFF7ED"
WHITE = "#FFFFFF"

FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size * SCALE)


def sc(value: int) -> int:
    return value * SCALE


def rounded_box(
    layer: Image.Image,
    rect: tuple[int, int, int, int],
    title: str,
    fields: list[str],
    *,
    derived: bool = False,
) -> None:
    x1, y1, x2, y2 = (sc(v) for v in rect)
    draw = ImageDraw.Draw(layer)

    # Soft shadow.
    shadow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        (x1 + sc(6), y1 + sc(8), x2 + sc(6), y2 + sc(8)),
        radius=sc(18),
        fill=(15, 23, 42, 28),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(sc(7)))
    layer.alpha_composite(shadow)

    border = ORANGE if derived else INDIGO
    fill = DERIVED_FILL if derived else SOURCE_FILL
    draw.rounded_rectangle(
        (x1, y1, x2, y2),
        radius=sc(18),
        fill=fill,
        outline=border,
        width=sc(3),
    )

    header_height = sc(56)
    draw.rounded_rectangle(
        (x1, y1, x2, y1 + header_height),
        radius=sc(18),
        fill=border,
    )
    draw.rectangle(
        (x1, y1 + sc(28), x2, y1 + header_height),
        fill=border,
    )

    draw.text(
        (x1 + sc(18), y1 + sc(12)),
        title,
        font=font(FONT_BOLD, 21),
        fill=WHITE,
    )

    field_font = font(FONT_MONO, 16)
    y = y1 + header_height + sc(17)
    line_height = sc(28)
    for field in fields:
        draw.text(
            (x1 + sc(18), y),
            field,
            font=field_font,
            fill=SLATE,
        )
        y += line_height


def arrow(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[int, int]],
    *,
    color: str = INDIGO,
) -> None:
    pts = [(sc(x), sc(y)) for x, y in points]
    draw.line(pts, fill=color, width=sc(4), joint="curve")

    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    size = sc(12)
    if x2 > x1:
        head = [(x2, y2), (x2 - size, y2 - size // 2), (x2 - size, y2 + size // 2)]
    elif x2 < x1:
        head = [(x2, y2), (x2 + size, y2 - size // 2), (x2 + size, y2 + size // 2)]
    elif y2 > y1:
        head = [(x2, y2), (x2 - size // 2, y2 - size), (x2 + size // 2, y2 - size)]
    else:
        head = [(x2, y2), (x2 - size // 2, y2 + size), (x2 + size // 2, y2 + size)]
    draw.polygon(head, fill=color)


def main() -> None:
    image = Image.new("RGBA", (sc(WIDTH), sc(HEIGHT)), BG)
    draw = ImageDraw.Draw(image)

    # Heading.
    draw.text(
        (sc(100), sc(45)),
        "OPEN DATA — PLANNED ENTITY RELATIONSHIP DIAGRAM",
        font=font(FONT_BOLD, 34),
        fill=NAVY,
    )
    draw.text(
        (sc(100), sc(93)),
        "Sensory-friendly Melbourne CBD navigation",
        font=font(FONT_REGULAR, 20),
        fill=MUTED,
    )
    draw.rounded_rectangle(
        (sc(100), sc(132), sc(2300), sc(138)),
        radius=sc(3),
        fill=INDIGO,
    )

    # Connectors are rendered before boxes so lines never cover text.
    # SENSOR to source tables.
    arrow(draw, [(1200, 300), (1200, 325), (400, 325), (400, 360)])
    arrow(draw, [(1200, 300), (1200, 360)])
    arrow(draw, [(1200, 300), (1200, 325), (2000, 325), (2000, 360)])

    # Geospatial and analytical relationships.
    arrow(draw, [(1200, 625), (1200, 710)])
    arrow(draw, [(650, 840), (900, 840)])
    arrow(draw, [(2000, 570), (2000, 710)])

    # Inputs to prediction use separate outside lanes to avoid congestion.
    arrow(draw, [(400, 598), (400, 660), (760, 660), (760, 1090), (930, 1090), (930, 1160)])
    arrow(draw, [(2000, 980), (2000, 1090), (1470, 1090), (1470, 1160)])

    # Entity boxes.
    rounded_box(
        image,
        (930, 165, 1470, 300),
        "SENSOR",
        ["sensor_id  (PK)", "status", "notes"],
    )
    rounded_box(
        image,
        (100, 360, 700, 598),
        "MINUTE_COUNT",
        [
            "sensor_id          (PK, FK)",
            "observed_at        (PK)",
            "total",
            "direction_1_count",
            "direction_2_count",
            "quality_status",
        ],
    )
    rounded_box(
        image,
        (900, 360, 1500, 625),
        "SENSOR_LOCATION_HISTORY",
        [
            "location_id        (PK)",
            "sensor_id          (FK)",
            "latitude",
            "longitude",
            "valid_from",
            "valid_to",
        ],
    )
    rounded_box(
        image,
        (1700, 360, 2300, 570),
        "HOURLY_COUNT",
        [
            "sensor_id          (PK, FK)",
            "observed_hour      (PK)",
            "total",
            "quality_status",
        ],
    )
    rounded_box(
        image,
        (100, 710, 650, 980),
        "REFUGE_CANDIDATE",
        [
            "place_id           (PK)",
            "category_id        (FK)",
            "name",
            "latitude",
            "longitude",
            "validation_status",
        ],
    )
    rounded_box(
        image,
        (900, 710, 1500, 948),
        "ROAD_EDGE",
        [
            "edge_id            (PK)",
            "from_node_id       (FK)",
            "to_node_id         (FK)",
            "distance",
            "walkability",
        ],
    )
    rounded_box(
        image,
        (1700, 710, 2300, 980),
        "CROWD_BASELINE",
        [
            "sensor_id          (PK, FK)",
            "weekday            (PK)",
            "hour_of_day        (PK)",
            "p40_count",
            "p75_count",
            "sample_size",
            "calculated_at",
        ],
        derived=True,
    )
    rounded_box(
        image,
        (930, 1160, 1470, 1325),
        "CROWD_PREDICTION",
        [
            "sensor_id, target_hour (PK)",
            "predicted_level",
            "confidence, model_version",
        ],
        derived=True,
    )

    # Legend.
    draw.rounded_rectangle(
        (sc(100), sc(1235), sc(125), sc(1260)),
        radius=sc(5),
        fill=SOURCE_FILL,
        outline=INDIGO,
        width=sc(2),
    )
    draw.text(
        (sc(140), sc(1233)),
        "Imported / normalised data",
        font=font(FONT_REGULAR, 15),
        fill=MUTED,
    )
    draw.rounded_rectangle(
        (sc(100), sc(1278), sc(125), sc(1303)),
        radius=sc(5),
        fill=DERIVED_FILL,
        outline=ORANGE,
        width=sc(2),
    )
    draw.text(
        (sc(140), sc(1276)),
        "Derived analytical output",
        font=font(FONT_REGULAR, 15),
        fill=MUTED,
    )

    # Downsample for antialiased lines and text.
    image = image.convert("RGB").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    image.save(OUTPUT, quality=95, optimize=True)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
