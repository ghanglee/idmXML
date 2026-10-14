"""Figure 1: UML class diagram of idmXSD v2.0 (Rev 12), hand-laid-out, editable SVG."""
import os
from PIL import ImageFont
from xml.sax.saxutils import escape
import cairosvg

FS = 15
F = ImageFont.truetype('/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf', FS)
FAM = "Calibri, Carlito, 'Segoe UI', Arial, sans-serif"
ROW = 19
HEAD = 22
BLUE, BLUE_S = '#DCE6F2', '#7F9DB9'
YEL, YEL_S = '#FFD966', '#7F6000'

S = []
C = {}


def tw(s):
    return F.getlength(s)


def T(x, y, s, anchor='start', size=FS, italic=False, color='#000000', bold=False):
    S.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FAM}" font-size="{size}" text-anchor="{anchor}" '
             f'{"font-style=\"italic\" " if italic else ""}{"font-weight=\"bold\" " if bold else ""}fill="{color}">{escape(s)}</text>')


def cls(name, x, y, attrs=(), w=None, label=None):
    label = label or name.split('#')[0]
    w = w or max([tw(label) + 30] + [tw('-  ' + a) + 24 for a in attrs])
    h = HEAD + (len(attrs) * ROW + 6 if attrs else 14)
    S.append(f'<g id="class-{escape(name)}">')
    S.append(f'<rect x="{x}" y="{y}" width="{w:.1f}" height="{h}" fill="{BLUE}" stroke="{BLUE_S}" stroke-width="1"/>')
    S.append(f'<line x1="{x}" y1="{y+HEAD}" x2="{x+w:.1f}" y2="{y+HEAD}" stroke="{BLUE_S}" stroke-width="1"/>')
    T(x + w / 2, y + 16, label, 'middle')
    for i, a in enumerate(attrs):
        T(x + 8, y + HEAD + 15 + i * ROW, '-')
        T(x + 22, y + HEAD + 15 + i * ROW, a)
    S.append('</g>')
    C[name] = (x, y, w, h)
    return C[name]


def ext(name, x, y, label=None, w=None):
    """Class specified elsewhere (yellow, rounded)."""
    label = label or name.split('#')[0]
    w = w or tw(label) + 34
    h = 26
    S.append(f'<g id="ext-{escape(name)}"><rect x="{x}" y="{y}" width="{w:.1f}" height="{h}" rx="6" ry="6" fill="{YEL}" stroke="{YEL_S}" stroke-width="1"/>')
    T(x + w / 2, y + 18, label, 'middle')
    S.append('</g>')
    C[name] = (x, y, w, h)
    return C[name]


def L(n, dy=None):
    x, y, w, h = C[n]; return (x, y + (h / 2 if dy is None else dy))


def R(n, dy=None):
    x, y, w, h = C[n]; return (x + w, y + (h / 2 if dy is None else dy))


def Tp(n, dx=None):
    x, y, w, h = C[n]; return (x + (w / 2 if dx is None else dx), y)


def B(n, dx=None):
    x, y, w, h = C[n]; return (x + (w / 2 if dx is None else dx), y + h)


def poly(pts, dashed=False, start=None, end=None, color='#000000'):
    d = ' '.join(f'{"M" if i == 0 else "L"}{x:.1f} {y:.1f}' for i, (x, y) in enumerate(pts))
    da = ' stroke-dasharray="6 4"' if dashed else ''
    S.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.1"{da}/>')
    if start:
        diamond(pts[0], pts[1], start == 'filled')
    if end == 'arrow':
        arrow(pts[-1], pts[-2])


def diamond(p, q, filled):
    import math
    (x, y), (x2, y2) = p, q
    a = math.atan2(y2 - y, x2 - x)
    L1, W1 = 18, 7
    pts = [(x, y), (x + L1 / 2 * math.cos(a) - W1 * math.sin(a), y + L1 / 2 * math.sin(a) + W1 * math.cos(a)),
           (x + L1 * math.cos(a), y + L1 * math.sin(a)),
           (x + L1 / 2 * math.cos(a) + W1 * math.sin(a), y + L1 / 2 * math.sin(a) - W1 * math.cos(a))]
    S.append('<polygon points="' + ' '.join(f'{a:.1f},{b:.1f}' for a, b in pts) +
             f'" fill="{"#404040" if filled else "#ffffff"}" stroke="#404040" stroke-width="1"/>')


def arrow(p, q):
    import math
    (x, y), (x2, y2) = p, q
    a = math.atan2(y2 - y, x2 - x)
    p1 = (x + 11 * math.cos(a + 0.4), y + 11 * math.sin(a + 0.4))
    p2 = (x + 11 * math.cos(a - 0.4), y + 11 * math.sin(a - 0.4))
    S.append(f'<path d="M{p1[0]:.1f} {p1[1]:.1f} L{x:.1f} {y:.1f} L{p2[0]:.1f} {p2[1]:.1f}" fill="none" stroke="#000000" stroke-width="1.1"/>')


def m(x, y, s, anchor='start'):
    T(x, y, s, anchor, FS - 1)


def selfagg(n, label, mult_top='0..*', side='right', dx=0):
    """Recursive aggregation loop on the right/bottom of class n."""
    x, y, w, h = C[n]
    if side == 'right':
        p0 = (x + w, y + h - 8)
        pts = [p0, (x + w + 34, y + h - 8), (x + w + 34, y + h + 26), (x + w - 30, y + h + 26), (x + w - 30, y + h)]
        poly(pts[::-1], start='hollow')
        m(x + w + 4, y + h - 12, mult_top)
        m(x + w - 46, y + h + 20, '1')
        T(x + w - 26, y + h + 44, label, 'middle', FS - 1)


def bus(xb, src, targets, smult='1', tmults=None, src_side='R', dashed_t=None):
    """Connect src right side to a vertical bus at xb, then to the left side of each target."""
    sp = R(src) if src_side == 'R' else src
    ys = [L(t)[1] for t in targets]
    poly([sp, (xb, sp[1])])
    poly([(xb, min(ys + [sp[1]])), (xb, max(ys + [sp[1]]))])
    for i, t in enumerate(targets):
        tp = L(t)
        poly([(xb, tp[1]), tp])
        if tmults:
            m(tp[0] - 6, tp[1] - 5, tmults[i], 'end')
    if smult:
        m(sp[0] + 5, sp[1] - 5, smult)


def build():
    S.clear(); C.clear()
    # ------------------------------------------------------------------ IDM + UC
    cls('idm', 15, 80, [], w=110)
    ext('specId#idm', 270, 42)
    ext('authoring#idm', 270, 98)
    cls('uc', 215, 210, [], w=190)

    colA = 520
    A = [('summary', 30, []), ('aimAndScope', 82, []), ('benefits', 134, []), ('limitations', 186, []),
         ('requiredResources', 238, []), ('requiredCompetencies', 290, []), ('userDefinedProperty', 342, ['name: String']),
         ('scopeKeyword', 418, []), ('benefitKeyword', 470, []),
         ('reference', 522, ['basisStandard: Boolean', 'fullCitation: String'])]
    for n, y, at in A:
        cls(n, colA, y, at, w=235)
    colB = 850
    Bc = [('language', 118, []), ('use', 170, ['name: String']), ('region', 236, ['value: String', 'type: String']),
          ('standardProjectPhase', 316, []), ('localProjectPhase', 368, []), ('constructionEntity', 420, ['name: String']),
          ('actor', 484, ['id: String <<PK>>', 'name: String', 'external: Boolean']),
          ('businessRule', 590, ['id: String <<PK>>', 'name: String', 'statement: String'])]
    for n, y, at in Bc:
        cls(n, colB, y, at, w=245)
    colC = 1180
    cls('description#uc', 835, 26, ['title: String'], w=260, label='description')
    cls('image', 1180, 22, ['caption: String', 'filePath: String', 'mimeType: String', 'encoding: String', '(content): base64'], w=250)
    cls('name', colC, 160, [], w=250)
    cls('outcomes', colC, 210, [], w=250)
    cls('informationRequirements', colC, 260, ['associatedEr: String [0..*] <<FK>>'], w=250)
    cls('classification', colC, 330, ['id: String', 'name: String', 'version: String', 'publicationYear: gYear'], w=250)
    cls('subActor', colC, 500, ['id: String <<PK>>', 'name: String'], w=250)
    cls('images#br', colC, 590, [], w=250, label='images')
    ext('description#out', 1465, 222, 'description')
    ext('image#br', 1475, 596, 'image')
    ext('description#br', 1225, 672, 'description')

    # idm composition
    ix, iy, iw, ih = C['idm']
    trunk = 175
    poly([(ix + iw, iy + 12), (trunk, iy + 12)], start='filled')
    m(ix + iw + 22, iy + 8, '1')
    poly([(trunk, iy + 12), (trunk, 1150 + 18)])
    poly([(trunk, iy + 12), (205, iy + 12)])
    poly([(205, L('specId#idm')[1]), (205, L('authoring#idm')[1])])
    poly([(205, L('specId#idm')[1]), L('specId#idm')]); m(L('specId#idm')[0] - 6, L('specId#idm')[1] - 5, '1', 'end')
    poly([(205, L('authoring#idm')[1]), L('authoring#idm')]); m(L('authoring#idm')[0] - 6, L('authoring#idm')[1] - 5, '1', 'end')
    poly([(trunk, L('uc')[1]), L('uc')]); m(L('uc')[0] - 6, L('uc')[1] - 5, '1', 'end')
    # subIdm
    pts = [(ix + 25, iy + ih), (ix + 25, iy + ih + 26), (ix + 85, iy + ih + 26), (ix + 85, iy + ih)]
    poly(pts, start='hollow')
    m(ix + 92, iy + ih + 14, '0..*'); m(ix + 8, iy + ih + 22, '1')
    T(ix + 55, iy + ih + 44, 'subIdm', 'middle', FS - 1)

    # uc -> specId/authoring (shared, distant) : bus to col A and col B
    ux, uy, uw, uh = C['uc']
    busA = 470
    poly([(ux + uw, uy + 10), (busA, uy + 10)]); m(ux + uw + 5, uy + 5, '1')
    poly([(busA, 30 + 11), (busA, 522 + 30)])
    poly([(ux + uw - 10, uy), (ux + uw - 10, 128), (260, 128)], dashed=False)
    S.pop()  # keep uc->specId/authoring implicit via idm (as in original)
    for n, y, at in A:
        tp = L(n, 11)
        poly([(busA, tp[1]), tp])
    mult_A = {'summary': '1', 'aimAndScope': '1', 'benefits': '0..1', 'limitations': '0..1', 'requiredResources': '0..1',
              'requiredCompetencies': '0..1', 'userDefinedProperty': '0..*', 'scopeKeyword': '0..*', 'benefitKeyword': '0..*', 'reference': '0..*'}
    for n, _, _ in A:
        p = L(n, 11); m(p[0] - 6, p[1] - 4, mult_A[n], 'end')
    # col A -> description bus at x=785
    busD = 790
    dsc = L('description#uc')
    for n in ['summary', 'aimAndScope', 'benefits', 'limitations', 'requiredResources', 'requiredCompetencies', 'userDefinedProperty']:
        p = R(n, 11); poly([p, (busD, p[1])]); m(p[0] + 5, p[1] - 4, '1')
    poly([(busD, dsc[1]), (busD, R('userDefinedProperty', 11)[1])])
    poly([(busD, dsc[1]), dsc]); m(dsc[0] - 6, dsc[1] - 5, '1..*', 'end')
    yd = R('description#uc')[1]; poly([R('description#uc'), (C['image'][0], yd)]); m(R('description#uc')[0] + 5, yd - 5, '1'); m(C['image'][0] - 6, yd - 5, '0..*', 'end')
    # uc -> col B bus at x=815
    busB = 815
    poly([(busA, 403), (busB, 403)])
    yb = [L(n, 11)[1] for n, _, _ in Bc]
    poly([(busB, min(yb)), (busB, max(yb))])
    mult_B = {'language': '1', 'use': '1..*', 'region': '1..*', 'standardProjectPhase': '1..*', 'localProjectPhase': '0..*',
              'constructionEntity': '0..*', 'actor': '0..*', 'businessRule': '0..*'}
    for n, _, _ in Bc:
        p = L(n, 11); poly([(busB, p[1]), p]); m(p[0] - 6, p[1] - 4, mult_B[n], 'end')
    # stage -> name / outcomes / informationRequirements ; classification
    busC = 1140
    for n in ['standardProjectPhase', 'localProjectPhase']:
        p = R(n, 11); poly([p, (busC, p[1])]); m(p[0] + 5, p[1] - 4, '1')
    for n, mm in [('name', '1'), ('outcomes', '0..1'), ('informationRequirements', '0..1')]:
        p = L(n, 11); poly([(busC, p[1]), p]); m(p[0] - 6, p[1] - 4, mm, 'end')
    poly([(busC, L('name', 11)[1]), (busC, R('localProjectPhase', 11)[1])])
    # classification links (use, localProjectPhase, constructionEntity, actor, subActor) via bus x=1160
    busK = 1160
    for n in ['use', 'localProjectPhase', 'constructionEntity', 'actor']:
        p = R(n, 30)
        if n == 'actor':
            p = R(n, 22)
        poly([p, (busK, p[1])]); m(p[0] + 5, p[1] - 4, '1')
    poly([(busK, R('use', 30)[1]), (busK, R('actor', 22)[1])])
    poly([(busK, L('classification', 40)[1]), L('classification', 40)]); m(L('classification')[0] - 6, L('classification', 40)[1] - 4, '0..1', 'end')
    sx, sy, sw, sh = C['subActor']
    poly([(sx + sw, sy + 30), (sx + sw + 20, sy + 30), (sx + sw + 20, C['classification'][1] + 60), R('classification', 60)])
    m(sx + sw + 4, sy + 26, '1'); m(R('classification')[0] + 4, C['classification'][1] + 56, '0..1')
    # actor -> subActor
    yy_ = C['subActor'][1] + 52
    poly([(R('actor')[0], yy_), (C['subActor'][0], yy_)])
    m(C['subActor'][0] - 6, yy_ - 4, '0..*', 'end'); m(R('actor')[0] + 5, yy_ - 4, '1')
    # outcomes / informationRequirements -> description
    od = L('description#out')
    for n in ['outcomes', 'informationRequirements']:
        p = R(n, 11); poly([p, (1450, p[1])]); m(p[0] + 4, p[1] - 4, '1')
    poly([(1450, R('outcomes', 11)[1]), (1450, R('informationRequirements', 11)[1])])
    poly([(1450, od[1]), od]); m(od[0] + 4, od[1] + 30, '1..*')
    # businessRule -> images (0..1) -> image (1..*); businessRule -> description (0..*)
    poly([R('businessRule', 11), L('images#br', 11)]); m(R('businessRule')[0] + 5, R('businessRule', 11)[1] - 4, '1'); m(L('images#br')[0] - 6, L('images#br', 11)[1] - 4, '0..1', 'end')
    poly([R('images#br', 11), (C['image#br'][0], R('images#br', 11)[1])]); m(R('images#br')[0] + 4, R('images#br', 11)[1] - 4, '1'); m(C['image#br'][0] - 4, R('images#br', 11)[1] + 15, '1..*', 'end')
    yd = L('description#br')[1]
    poly([R('businessRule', 70), (1150, R('businessRule', 70)[1]), (1150, yd), L('description#br')]); m(R('businessRule')[0] + 5, R('businessRule', 70)[1] - 4, '1'); m(L('description#br')[0] - 6, yd - 5, '0..*', 'end')
    # businessRule reference -> uc reference
    rb = B('reference', 120); bb = B('businessRule', 150)
    poly([rb, (rb[0], 680), (bb[0], 680), bb])
    m(rb[0] - 6, rb[1] + 14, '0..*', 'end'); m(bb[0] + 5, bb[1] + 14, '1')
    # subUc
    x, y, w, h = C['uc']
    poly([(x + w - 40, y + h), (x + w - 40, y + h + 26), (x + w + 22, y + h + 26), (x + w + 22, y + 20), (x + w, y + 20)][::-1], start=None)
    S.pop()
    pts = [(x + w - 40, y + h), (x + w - 40, y + h + 26), (x + w + 22, y + h + 26), (x + w + 22, y + 26), (x + w, y + 26)]
    poly(pts, start='hollow'); m(x + w - 36, y + h + 20, '1'); m(x + w + 3, y + 22, '0..*')
    T(x + w - 20, y + h + 44, 'subUc', 'middle', FS - 1)

    # ------------------------------------------------------------------ BCM
    yb0 = 730
    cls('businessContextMap', 215, yb0, [], w=190)
    ext('specId#bcm', 470, yb0 - 25, 'specId')
    ext('authoring#bcm', 470, yb0 + 18, 'authoring')
    cls('pm', 520, yb0 + 100, [], w=120)
    cls('im', 520, yb0 + 260, [], w=120)
    cls('dataObjectAndEr', 760, yb0 - 10, ['id: String <<PK>>', 'associatedDataObject: String <<FK>>', 'associatedEr: String <<FK>>'], w=300)
    cls('shapeAndActor', 760, yb0 + 80, ['id: String <<PK>>', 'associatedShape: String <<FK>>', 'associatedActor: String <<FK>>'], w=300)
    cls('diagram', 760, yb0 + 172, ['id: String <<PK>>', 'name: String', 'notation: String', 'diagramFilePath: String',
                                    'imageFilePath: String', 'diagramContent: String'], w=300)
    cls('tm', 760, yb0 + 337, [], w=120)
    cls('messageAndEr', 1120, yb0 + 330, ['id: String <<PK>>', 'associatedMessage: String <<FK>>', 'associatedEr: String <<FK>>'], w=310)
    ext('description#diag', 1150, yb0 + 172 + 47, 'description')
    bx, by, bw, bh = C['businessContextMap']
    poly([(trunk, L('businessContextMap')[1]), L('businessContextMap')]); m(L('businessContextMap')[0] - 6, L('businessContextMap')[1] - 5, '0..*', 'end')
    bt = 440
    poly([R('businessContextMap', 10), (bt, R('businessContextMap', 10)[1])]); m(bx + bw + 5, by + 5, '1')
    poly([(bt, L('specId#bcm')[1]), (bt, L('im')[1])])
    for n in ['specId#bcm', 'authoring#bcm']:
        poly([(bt, L(n)[1]), L(n)]); m(L(n)[0] - 6, L(n)[1] - 5, '1', 'end')
    poly([(bt, L('pm')[1]), L('pm')]); poly([(bt, L('im')[1]), L('im')])
    m(bt + 6, L('pm')[1] - 5, '1..* (choice)')
    # subBusinessContextMap
    pts = [(bx + bw - 40, by + bh), (bx + bw - 40, by + bh + 26), (bx + bw + 16, by + bh + 26), (bx + bw + 16, by + 26), (bx + bw, by + 26)]
    poly(pts, start='hollow'); m(bx + bw - 36, by + bh + 20, '1'); m(bx + bw + 2, by + 40, '0..*')
    T(bx + bw - 40, by + bh + 44, 'subBusinessContextMap', 'middle', FS - 1)
    # pm -> dataObjectAndEr, shapeAndActor, diagram
    pb = 715
    poly([R('pm'), (pb, R('pm')[1])]); m(R('pm')[0] + 5, R('pm')[1] - 5, '1')
    poly([(pb, L('dataObjectAndEr')[1]), (pb, L('diagram', 20)[1])])
    for n, mm in [('dataObjectAndEr', '0..*'), ('shapeAndActor', '0..*'), ('diagram', '1')]:
        p = L(n) if n != 'diagram' else L(n, 20)
        poly([(pb, p[1]), p]); m(p[0] - 6, p[1] - 5, mm, 'end')
    # subPm
    x, y, w, h = C['pm']
    pts = [(x + 40, y + h), (x + 40, y + h + 26), (x + w + 16, y + h + 26), (x + w + 16, y + 28), (x + w, y + 28)]
    poly(pts, start='hollow'); m(x + 44, y + h + 20, '1'); m(x + w + 2, y + 44, '0..*')
    T(x + 40, y + h + 44, 'subPm', 'middle', FS - 1)
    # im -> diagram, tm
    ib = 735
    poly([R('im'), (ib, R('im')[1])]); m(R('im')[0] + 5, R('im')[1] - 5, '1')
    poly([(ib, L('diagram', 120)[1]), (ib, L('tm')[1])])
    poly([(ib, L('diagram', 120)[1]), L('diagram', 120)]); m(L('diagram')[0] - 6, L('diagram', 120)[1] - 5, '1', 'end')
    poly([(ib, L('tm')[1]), L('tm')]); m(L('tm')[0] - 6, L('tm')[1] - 5, '1..*', 'end')
    # tm -> diagram (1) and messageAndEr (0..*)
    poly([Tp('tm', 60), B('diagram', 60)]); m(Tp('tm', 60)[0] + 5, Tp('tm')[1] - 4, '1'); m(B('diagram', 60)[0] - 5, B('diagram')[1] + 14, '1', 'end')
    poly([R('tm'), L('messageAndEr', 25)]); m(R('tm')[0] + 5, R('tm')[1] - 5, '1'); m(L('messageAndEr')[0] - 6, L('messageAndEr', 25)[1] - 5, '0..*', 'end')
    poly([R('diagram', 60), (C['description#diag'][0], R('diagram', 60)[1])]); m(R('diagram')[0] + 5, R('diagram', 60)[1] - 5, '1'); m(L('description#diag')[0] - 6, R('diagram', 60)[1] - 5, '0..*', 'end')

    # ------------------------------------------------------------------ ER
    ye = 1150
    cls('er', 215, ye, [], w=190)
    ext('specId#er', 470, ye - 18, 'specId')
    ext('authoring#er', 470, ye + 20, 'authoring')
    cls('informationUnit', 470, ye + 70, ['id: String <<PK>>', 'name: String', 'dataType: String', 'isMandatory: Boolean', 'definition: String'], w=245)
    cls('constraint', 470, ye + 245, ['id: String <<PK>>', 'associatedBusinessRule: String [0..*] <<FK>>',
                                       'associatedInformationUnit: String [0..*] <<FK>>'], w=330)
    cls('correspondingMvd', 470, ye + 400, ['basis: String', 'name: String'], w=245)
    cls('synonym', 870, ye - 20, ['(content): String', 'xml:lang: language'], w=245)
    cls('examples', 870, ye + 60, [], w=245)
    cls('correspondingExternalElement', 870, ye + 115, ['basis: String', 'name: String'], w=245)
    cls('expression', 870, ye + 245, ['id: String', 'uri: anyURI', '(rule content): any [0..*]'], w=245)
    cls('formalRuleLanguage', 1180, ye + 245, ['name: String', 'version: String', 'publicationYear: gYear', 'uri: anyURI'], w=250)
    ext('businessRule#er', 870, ye + 355, 'businessRule')
    ext('description#er', 470, ye + 490, 'description')
    ext('description#iu', 745, ye + 157, 'description')
    ext('description#c', 520, ye + 352, 'description')
    ext('description#mvd', 775, ye + 420, 'description')
    ext('description#ex', 1160, ye + 65, 'description')
    ext('description#cee', 1160, ye + 130, 'description')
    ex, ey, ew, eh = C['er']
    poly([(trunk, L('er')[1]), L('er')]); m(L('er')[0] - 6, L('er')[1] - 5, '0..1', 'end')
    et = 440
    poly([R('er', 10), (et, R('er', 10)[1])]); m(ex + ew + 5, ey + 5, '1')
    poly([(et, L('specId#er')[1]), (et, L('description#er')[1])])
    for n in ['specId#er', 'authoring#er']:
        poly([(et, L(n)[1]), L(n)]); m(L(n)[0] - 6, L(n)[1] - 5, '1', 'end')
    for n, mm, dy in [('informationUnit', '1..* (choice)', 11), ('constraint', '0..*', 11), ('correspondingMvd', '0..*', 11)]:
        p = L(n, dy); poly([(et, p[1]), p]); m(p[0] - 6, p[1] - 4, '', 'end')
        m(et + 4, p[1] - 4, mm)
    poly([(et, L('description#er')[1]), L('description#er')]); m(L('description#er')[0] - 6, L('description#er')[1] - 5, '0..*', 'end')
    # subEr
    pts = [(ex + ew - 40, ey + eh), (ex + ew - 40, ey + eh + 26), (ex + ew + 16, ey + eh + 26), (ex + ew + 16, ey + 26), (ex + ew, ey + 26)]
    poly(pts, start='hollow'); m(ex + ew - 36, ey + eh + 20, '1'); m(ex + ew + 2, ey + 40, '0..*')
    T(ex + ew - 40, ey + eh + 44, 'subEr', 'middle', FS - 1)
    # informationUnit children bus x=840
    ib2 = 840
    p = R('informationUnit', 11); poly([p, (ib2, p[1])]); m(p[0] + 5, p[1] - 4, '1')
    poly([(ib2, L('synonym', 11)[1]), (ib2, L('correspondingExternalElement', 11)[1])])
    for n, mm in [('synonym', '0..*'), ('examples', '0..1'), ('correspondingExternalElement', '0..*')]:
        q = L(n, 11); poly([(ib2, q[1]), q]); m(q[0] - 6, q[1] - 4, mm, 'end')
    # subInformationUnit
    x, y, w, h = C['informationUnit']
    pts = [(x + 60, y), (x + 60, y - 18), (x + w + 16, y - 18), (x + w + 16, y + 50), (x + w, y + 50)]
    poly(pts, start='hollow'); m(x + 64, y - 6, '1'); m(x + w + 2, y + 66, '0..*')
    T(x + w - 60, y - 24, 'subInformationUnit', 'middle', FS - 1)
    # constraint -> expression
    poly([R('constraint', 11), L('expression', 11)]); m(R('constraint')[0] + 5, R('constraint', 11)[1] - 4, '1'); m(L('expression')[0] - 6, L('expression', 11)[1] - 4, '0..*', 'end')
    poly([R('expression', 11), L('formalRuleLanguage', 11)]); m(R('expression')[0] + 5, R('expression', 11)[1] - 4, '1'); m(L('formalRuleLanguage')[0] - 6, L('formalRuleLanguage', 11)[1] - 4, '1', 'end')
    # FK dependencies
    cx, cy0, cw, ch = C['constraint']
    yBR = cy0 + HEAD + 15 + ROW - 5
    yIU = cy0 + HEAD + 15 + 2 * ROW - 5
    brp = L('businessRule#er')
    poly([(cx + cw, yBR + 2), (cx + cw + 35, yBR + 2), (cx + cw + 35, brp[1]), brp], dashed=True, end='arrow')
    T(cx + cw + 40, brp[1] - 6, '«ref»', 'start', FS - 2, italic=True)
    bi = B('informationUnit', 30)
    poly([(cx, yIU + 2), (cx - 14, yIU + 2), (cx - 14, bi[1] + 12), (bi[0], bi[1] + 12), bi], dashed=True, end='arrow')
    T(bi[0] + 6, bi[1] + 10, '«ref»', 'start', FS - 2, italic=True)
    # descriptions in ER (one box per owner)
    def dlink(src_pt, dst, horiz=True):
        dp = L(dst) if horiz else Tp(dst)
        if horiz:
            poly([src_pt, (dp[0], src_pt[1])]); m(src_pt[0] + 4, src_pt[1] - 4, '1'); m(dp[0] - 4, src_pt[1] + 15, '0..*', 'end')
        else:
            poly([src_pt, (src_pt[0], dp[1])]); m(src_pt[0] + 5, src_pt[1] + 13, '1'); m(src_pt[0] - 5, dp[1] - 3, '0..*', 'end')
    dlink(R('informationUnit', 100), 'description#iu')
    x0, y0, w0, h0 = C['description#c']
    dlink((x0 + w0 / 2, C['constraint'][1] + C['constraint'][3]), 'description#c', horiz=False)
    dlink(R('correspondingMvd', 33), 'description#mvd')
    dlink(R('examples', 18), 'description#ex')
    dlink(R('correspondingExternalElement', 33), 'description#cee')

    # ------------------------------------------------------------------ authoring / specId panel
    yp = 1720
    S.append(f'<rect x="15" y="{yp}" width="1560" height="400" fill="none" stroke="#000000" stroke-width="1.2"/>')
    S.append(f'<line x1="1230" y1="{yp}" x2="1230" y2="{yp+400}" stroke="#000000" stroke-width="1.2"/>')
    cls('authoring', 520, yp + 10, ['copyright: String'], w=190)
    cls('changeLog', 30, yp + 120, ['id: String <<PK>>', 'changeDateTime: DateTime', 'changeSummary: String'], w=270)
    cls('author', 450, yp + 120, ['id: String <<PK>>'], w=215)
    cls('committee', 790, yp + 120, ['name: String'], w=170)
    cls('publisher', 985, yp + 120, ['name: String', 'location: String'], w=175)
    cls('change', 30, yp + 290, ['changedElement: String', 'changedFrom: String'], w=270)
    cls('person', 330, yp + 245, ['firstName: String', 'middleName: String', 'lastName: String', 'emailAddress: String', 'affiliation: String'], w=210)
    cls('organization', 570, yp + 245, ['name: String'], w=210)
    cls('specId', 1255, yp + 50, ['guid: String <<PK>>', 'shortTitle: String', 'localShortTitle: String', 'fullTitle: String',
                                   'subTitle: String', 'idmCode: String', 'localCode: String', 'documentStatus: String',
                                   'localDocumentStatus: String', 'version: String'], w=285)
    ax, ay, aw, ah = C['authoring']
    yy = yp + 92
    poly([B('authoring'), (B('authoring')[0], yy)]); m(B('authoring')[0] + 5, B('authoring')[1] + 14, '1')
    poly([(Tp('changeLog')[0], yy), (Tp('publisher')[0], yy)])
    for n, mm in [('changeLog', '1..*'), ('author', '1..*'), ('committee', '0..*'), ('publisher', '0..1')]:
        t = Tp(n); poly([(t[0], yy), t]); m(t[0] - 6, t[1] - 5, mm, 'end')
    poly([R('changeLog', 32), L('author', 32)]); m(R('changeLog')[0] + 5, R('changeLog', 32)[1] - 5, '1..*  changedBy')
    m(L('author')[0] - 6, L('author', 32)[1] - 5, '1', 'end')
    poly([R('author', 18), L('committee', 18)]); m(R('author')[0] + 5, R('author', 18)[1] - 5, '1..*  leader'); m(L('committee')[0] - 6, L('committee', 18)[1] - 5, '0..*', 'end')
    poly([R('author', 42), L('committee', 42)]); m(R('author')[0] + 5, R('author', 42)[1] - 5, '1..*  member'); m(L('committee')[0] - 6, L('committee', 42)[1] - 5, '0..*', 'end')
    pb2 = yp + 222
    poly([B('author'), (B('author')[0], pb2)]); m(B('author')[0] + 5, B('author')[1] + 14, '1')
    poly([(Tp('person')[0], pb2), (Tp('organization')[0], pb2)])
    for n in ['person', 'organization']:
        t = Tp(n); poly([(t[0], pb2), t]); m(t[0] - 6, t[1] - 5, '1..*', 'end')
    T(B('author')[0] + 10, pb2 + 16, '{choice}', 'start', FS - 2, italic=True)
    poly([B('changeLog', 135), Tp('change', 135)], start='filled'); m(B('changeLog', 135)[0] + 8, B('changeLog')[1] + 30, '1'); m(Tp('change', 135)[0] + 8, Tp('change')[1] - 6, '0..*')

    # legend
    ext('legend', 1180, 1640, ' ', w=46)
    T(1235, 1658, ': Classes specified elsewhere in the diagram', 'start', FS - 1)
    T(1180, 1686, '<<FK>>: reference by identifier (ref attribute)', 'start', FS - 1)
    W, H = 1590, yp + 410
    body = '\n'.join(S)
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
            f'<title>idmXSD v2.0 logical view (UML class diagram)</title>\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n{body}\n</svg>\n')


if __name__ == '__main__':
    svg = build()
    open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fig1_uml.svg'), 'w').write(svg)
    cairosvg.svg2png(url=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fig1_uml.svg'), write_to=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fig1_uml.png'), scale=1.4)
