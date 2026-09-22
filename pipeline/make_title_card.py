from pathlib import Path

width, height = 1280, 720
background = (36, 31, 26)
accent = (139, 62, 47)
paper = (244, 234, 215)
muted = (203, 187, 162)

# A dependency-free PPM card. Text is drawn with a compact 5x7 bitmap alphabet.
font = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    " ": ["00000"] * 7,
}

pixels = [list(background) for _ in range(width * height)]

def rect(x0, y0, x1, y1, color):
    for y in range(max(0, y0), min(height, y1)):
        base = y * width
        for x in range(max(0, x0), min(width, x1)):
            pixels[base + x] = list(color)

def text(line, y, scale, color):
    glyph_width = 6 * scale
    total = len(line) * glyph_width - scale
    x0 = (width - total) // 2
    for index, character in enumerate(line):
        glyph = font[character]
        for gy, row in enumerate(glyph):
            for gx, value in enumerate(row):
                if value == "1":
                    x = x0 + index * glyph_width + gx * scale
                    rect(x, y + gy * scale, x + scale, y + (gy + 1) * scale, color)

rect(0, 0, width, 12, accent)
text("THE ABE TABAK TAPES", 245, 9, paper)
text("FAMILY ORAL HISTORY", 350, 5, muted)
text("TAPE 1", 430, 6, paper)

out = Path(__file__).resolve().parent / "pilot-tape1" / "title-card.ppm"
with out.open("wb") as handle:
    handle.write(f"P6\n{width} {height}\n255\n".encode())
    handle.write(bytes(channel for pixel in pixels for channel in pixel))
print(out)
