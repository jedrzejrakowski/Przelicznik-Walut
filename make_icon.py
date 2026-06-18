"""Generuje przykladowa ikone aplikacji (icon.ico).

Motyw: zaokraglone zielone tlo, dwukierunkowa strzalka (przeliczanie) oraz
symbol "zl". Uruchom raz:  python make_icon.py
Wymaga biblioteki Pillow:  pip install pillow
"""

from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

SIZE = 256
BG = (26, 110, 26, 255)        # zielen (jak kolor wyniku w aplikacji)
FG = (255, 255, 255, 255)      # bialy


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in ("DejaVuSans-Bold.ttf", "DejaVuSans.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def build() -> Image.Image:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Zaokraglone tlo.
    draw.rounded_rectangle([8, 8, SIZE - 8, SIZE - 8], radius=48, fill=BG)

    # Dwukierunkowa strzalka (symbol przeliczania) w gornej czesci.
    y = 92
    draw.line([(70, y), (186, y)], fill=FG, width=12)
    draw.polygon([(70, y), (96, y - 20), (96, y + 20)], fill=FG)      # w lewo
    y2 = 128
    draw.line([(70, y2), (186, y2)], fill=FG, width=12)
    draw.polygon([(186, y2), (160, y2 - 20), (160, y2 + 20)], fill=FG)  # w prawo

    # Symbol "zl".
    font = _font(96)
    text = "zł"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        ((SIZE - tw) / 2 - bbox[0], 150 - bbox[1]),
        text,
        font=font,
        fill=FG,
    )
    return img


def main() -> None:
    img = build()
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save("icon.ico", format="ICO", sizes=sizes)
    img.save("icon.png", format="PNG")
    print("Zapisano icon.ico oraz icon.png")


if __name__ == "__main__":
    main()
