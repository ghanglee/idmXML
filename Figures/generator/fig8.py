import os
from PIL import ImageFont
from xml.sax.saxutils import escape
import cairosvg

FAM = "Calibri, Carlito, 'Segoe UI', Arial, sans-serif"
F = lambda s: ImageFont.truetype('/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf', s)
S = []


def T(x, y, s, size, anchor='middle', color='#000000'):
    S.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FAM}" font-size="{size}" text-anchor="{anchor}" fill="{color}">{escape(s)}</text>')


def brace(x1, x2, y, color='#4A6FA5'):
    xm = (x1 + x2) / 2
    S.append(f'<path d="M{x1} {y+14} Q{x1} {y+4} {x1+10} {y+4} L{xm-10} {y+4} Q{xm} {y+4} {xm} {y-6} '
             f'Q{xm} {y+4} {xm+10} {y+4} L{x2-10} {y+4} Q{x2} {y+4} {x2} {y+14}" fill="none" stroke="{color}" stroke-width="1.5"/>')


boxes = [
    ('Specification|Type', ['ISO 29481-1'], 12, 145, False),
    ('Primary|Use', ['ISO 29481-1'], 162, 280, False),
    ('Project Phase|(Start)', ['ISO 22263'], 302, 455, False),
    ('Project Phase|(End)', ['ISO 22263'], 470, 622, False),
    ('Primary|Region', ['ISO 3166-1 Country', 'or a user-defined', 'region'], 640, 742, False),
    ('Language', ['ISO 639-1'], 755, 858, False),
    ('Short title|in English', [], 893, 1022, True),
    ('Author or|committee', ['Last name of the', 'leading author or a', 'short committee name'], 1040, 1168, True),
    ('Initial|Date', ['ISO 8601-1'], 1185, 1278, True),
    ('Document|status', [], 1295, 1438, True),
]
EX = 'er_AuthorEstimate_BR_DE_NOR_EN_CostEstimationForPCBridge_bSNoric_20200317T093000_WD'


def build():
    S.clear()
    W, H = 1460, 480
    S.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
    T(722, 50, 'IDM specification code', 22)
    brace(10, 1436, 80)
    T(435, 133, 'IDM classification code', 22)
    brace(12, 858, 158)
    T(1150, 133, 'Individual-specification-oriented information', 22)
    brace(878, 1436, 158)
    by, bh = 236, 80
    for i, (lab, note, x1, x2, blue) in enumerate(boxes):
        fill = '#DEEBF7' if blue else '#FFFFFF'
        S.append(f'<g id="part-{i+1}"><rect x="{x1}" y="{by}" width="{x2-x1}" height="{bh}" rx="12" ry="12" fill="{fill}" stroke="#7F7F7F" stroke-width="2.5"/>')
        l1, *l2 = lab.split('|')
        if l2:
            T((x1 + x2) / 2, by + 34, l1, 18); T((x1 + x2) / 2, by + 58, l2[0], 18)
        else:
            T((x1 + x2) / 2, by + 46, l1, 18)
        for k, n in enumerate(note):
            T((x1 + x2) / 2, by - 10 - 17 * (len(note) - 1 - k), n, 13, color='#2F5597')
        S.append('</g>')
        if i < len(boxes) - 1:
            nx = boxes[i + 1][2]
            S.append(f'<line x1="{x2+2}" y1="{by+bh-2}" x2="{nx-2}" y2="{by+bh-2}" stroke="#7F7F7F" stroke-width="2"/>')
    # example string and leader lines
    size = 30
    f = F(size)
    prefix = 'e.g.   '
    x0 = 190
    T(x0 - 12, 445, 'e.g.', size, 'end', '#2F5597')
    T(x0, 445, EX, size, 'start', '#2F5597')
    segs = EX.split('_')
    pos = x0
    for i, sg in enumerate(segs):
        w = f.getlength(sg)
        cx = pos + w / 2
        x1, x2 = boxes[i][2], boxes[i][3]
        S.append(f'<line x1="{(x1+x2)/2:.1f}" y1="{by+bh+2}" x2="{cx:.1f}" y2="412" stroke="#2F5597" stroke-width="1" stroke-dasharray="3 3"/>')
        pos += w + f.getlength('_')
    svg = (f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
           f'<title>IDM code</title>\n' + '\n'.join(S) + '\n</svg>\n')
    return svg


if __name__ == '__main__':
    open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fig8_code.svg'), 'w').write(build())
    cairosvg.svg2png(url=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fig8_code.svg'), write_to=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fig8_code.png'), scale=1.5)
