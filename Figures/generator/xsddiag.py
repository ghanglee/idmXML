"""Generate XMLSpy-style XSD tree diagrams as editable SVG (real <text>, grouped shapes).

Usage (module): render(schema, root_name, expand=set_of_names, out='fig.svg', columns_split=None)
"""
import xmlschema
from xmlschema.validators import XsdGroup, XsdAnyElement
from PIL import ImageFont
from xml.sax.saxutils import escape

FONT_B = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', 12)
FONT_I = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf', 12)
FONT_R = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf', 10)
FAMILY = "Arial, 'Liberation Sans', Helvetica, sans-serif"
XMLNS = '{http://www.w3.org/XML/1998/namespace}'

BOX_H = 22      # element box height
ATT_H = 18      # attribute box height
VGAP = 6        # vertical gap between siblings
HGAP = 22       # horizontal gap from trunk to child
TOG = 9         # toggle square size
COMP_W, COMP_H = 46, 22


def tw(s, f=FONT_B):
    return f.getlength(s)


def occ(p):
    mx = '*' if p.max_occurs is None else str(p.max_occurs)
    return p.min_occurs, mx


class N:
    """Layout node."""
    def __init__(self, kind, **kw):
        self.kind = kind
        self.children = []
        self.__dict__.update(kw)
        self.w = self.h = 0  # own box size
        self.x = self.y = 0  # own box top-left


def build(schema, el, expand, path_types, first_seen, is_root=False):
    t = el.type
    name = el.local_name
    is_ref = el.ref is not None
    mn, mx = occ(el)
    attrs = []
    for k, a in getattr(el, 'attributes', {}).items():
        if not k:
            continue
        nm = 'xml:' + k[len(XMLNS):] if k.startswith(XMLNS) else k.split('}')[-1]
        attrs.append((nm, a.use == 'required'))
    content = None
    only_any_text = False
    if t.is_complex() and not t.has_simple_content() and t.content is not None and len(t.content) > 0:
        content = t.content
        items = list(content.iter_elements()) if False else list(content)
        if all(isinstance(p, XsdAnyElement) for p in items) and getattr(t, 'mixed', False):
            only_any_text = True
            content = None
    texty = t.is_simple() or t.has_simple_content() or getattr(t, 'mixed', False) or only_any_text
    key = el.ref.name if is_ref else (t.name or id(el))
    expandable = bool(attrs) or content is not None
    recursion = key in path_types
    want = is_root or (not is_ref) or (name in expand and name not in first_seen)
    expanded = expandable and want and not recursion
    if expanded and is_ref:
        first_seen.add(name)
    n = N('el', name=name, ref=is_ref, min=mn, max=mx, texty=texty and not content, mixed=getattr(t, 'mixed', False),
          expandable=expandable, expanded=expanded)
    if expanded:
        pt = path_types | {key}
        if attrs:
            n.children.append(N('attrs', items=attrs, min=1, max='1'))
        if content is not None:
            n.children.append(build_group(schema, content, expand, pt, first_seen))
        if is_root and el.identities:
            n.children.append(N('constraints', min=1, max='1'))
    return n


def build_group(schema, g, expand, path_types, first_seen):
    mn, mx = occ(g)
    n = N('group', model=g.model, min=mn, max=mx)
    for p in g:
        if isinstance(p, XsdGroup):
            n.children.append(build_group(schema, p, expand, path_types, first_seen))
        elif isinstance(p, XsdAnyElement):
            ns = ' '.join(sorted(p.namespace)) if not isinstance(p.namespace, str) else p.namespace
            n.children.append(N('any', ns=ns, min=p.min_occurs, max='*' if p.max_occurs is None else str(p.max_occurs)))
        else:
            n.children.append(build(schema, p, expand, path_types, first_seen))
    return n


# ---------------------------------------------------------------- sizing
def size(n):
    if n.kind == 'el':
        n.w = 14 + tw(n.name) + (16 if n.expandable else 8) + (8 if n.ref else 0) + (8 if n.texty else 0)
        n.h = BOX_H
    elif n.kind == 'group':
        n.w, n.h = COMP_W + TOG + 2, COMP_H
    elif n.kind == 'any':
        n.w, n.h = 14 + tw('any ' + n.ns) + 8, BOX_H
    elif n.kind == 'constraints':
        n.w, n.h = 14 + TOG + tw('constraints', FONT_I) + 12, BOX_H
    elif n.kind == 'attrs':
        inner_w = max(tw(a) for a, _ in n.items) + 20
        n.w = max(inner_w + 30, tw('attributes', FONT_I) + 60)
        n.h = 24 + len(n.items) * (ATT_H + 5) + 4
    for c in n.children:
        size(c)


def label_h(n):
    return 12 if (n.kind in ('el', 'group', 'any') and (n.max not in ('1',))) else 0


def subtree_h(n):
    own = n.h + label_h(n)
    if getattr(n, 'split', None):
        for c in n.children: subtree_h(c)
        k = n.split
        h1 = sum(c.sh for c in n.children[:k]) + VGAP * (k - 1)
        h2 = sum(c.sh for c in n.children[k:]) + VGAP * (len(n.children) - k - 1)
        n.sh = max(own, h1, h2) + 24
        return n.sh
    if not n.children:
        n.sh = own
        return own
    ch = sum(subtree_h(c) for c in n.children) + VGAP * (len(n.children) - 1)
    n.sh = max(own, ch + label_h(n))
    return n.sh


def place(n, x, y_top):
    """Place subtree with top at y_top; node box vertically centred on children span."""
    n.x = x
    if getattr(n, 'split', None):
        k = n.split
        cx = x + n.w + HGAP + 6
        yy = y_top + 24
        for c in n.children[:k]:
            place(c, cx, yy); yy += c.sh + VGAP
        right = max(bounds(c)[2] for c in n.children[:k])
        n.cx2 = right + 40
        yy = y_top + 24
        for c in n.children[k:]:
            place(c, n.cx2, yy); yy += c.sh + VGAP
        n.y = y_top + (n.sh - n.h) / 2
        n.bus_y = y_top + 8
        return
    if not n.children:
        n.y = y_top + (n.sh - n.h - label_h(n)) / 2
        return
    cx = x + n.w + HGAP + 6
    yy = y_top + (n.sh - label_h(n) - (sum(c.sh for c in n.children) + VGAP * (len(n.children) - 1))) / 2
    for c in n.children:
        place(c, cx, yy)
        yy += c.sh + VGAP
    first, last = n.children[0], n.children[-1]
    mid = (cy(first) + cy(last)) / 2
    n.y = mid - n.h / 2


def cy(n):
    return n.y + n.h / 2


def bounds(n, b=None):
    b = b or [1e9, 1e9, -1e9, -1e9]
    b[0] = min(b[0], n.x); b[1] = min(b[1], n.y)
    b[2] = max(b[2], n.x + n.w + 6 + (6 if n.kind == 'el' and n.max != '1' else 0))
    b[3] = max(b[3], n.y + n.h + 4 + label_h(n))
    for c in n.children:
        bounds(c, b)
    return b


# ---------------------------------------------------------------- drawing
S = []


def add(s):
    S.append(s)


def rect(x, y, w, h, dashed=False, fill='#ffffff', shadow=True, sw=1.2):
    if shadow:
        add(f'<rect x="{x+3:.1f}" y="{y+3:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#c8c8c8" stroke="none"/>')
    da = ' stroke-dasharray="4 2"' if dashed else ''
    add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="#000000" stroke-width="{sw}"{da}/>')


def toggle(x, y, plus):
    add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{TOG}" height="{TOG}" fill="#ffffff" stroke="#000000" stroke-width="0.9"/>')
    add(f'<line x1="{x+2:.1f}" y1="{y+TOG/2:.1f}" x2="{x+TOG-2:.1f}" y2="{y+TOG/2:.1f}" stroke="#000000" stroke-width="1"/>')
    if plus:
        add(f'<line x1="{x+TOG/2:.1f}" y1="{y+2:.1f}" x2="{x+TOG/2:.1f}" y2="{y+TOG-2:.1f}" stroke="#000000" stroke-width="1"/>')


def text(x, y, s, cls='b', anchor='start', size=12):
    weight = 'bold' if cls == 'b' else 'normal'
    style = 'italic' if cls == 'i' else 'normal'
    add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FAMILY}" font-size="{size}" font-weight="{weight}" '
        f'font-style="{style}" text-anchor="{anchor}" fill="#000000">{escape(s)}</text>')


def line(x1, y1, x2, y2, dashed=False):
    da = ' stroke-dasharray="4 3"' if dashed else ''
    add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#000000" stroke-width="1"{da}/>')


def card(n):
    if n.max == '1' and n.min == 1:
        return
    if n.max == '1' and n.min == 0:
        return
    text(n.x + n.w - 2, n.y + n.h + 13, f'{n.min}..{n.max}', 'r', 'end', 11)


def draw(n):
    add(f'<g id="{n.kind}-{getattr(n, "name", getattr(n, "model", ""))}">')
    optional = n.min == 0
    if n.kind == 'el':
        if n.max != '1':
            rect(n.x + 4, n.y + 4, n.w, n.h, optional, shadow=True)
        rect(n.x, n.y, n.w, n.h, optional, shadow=n.max == '1')
        tx = n.x + 8
        if n.ref:
            # reference arrow
            ax, ay = n.x + 3, n.y + n.h - 3
            add(f'<path d="M{ax:.1f} {ay:.1f} L{ax+6:.1f} {ay-6:.1f} M{ax+2:.1f} {ay-6:.1f} L{ax+6:.1f} {ay-6:.1f} L{ax+6:.1f} {ay-2:.1f}" '
                f'stroke="#000000" stroke-width="1.2" fill="none"/>')
            tx += 6
        if n.texty:
            for k in range(3):
                line(n.x + 3, n.y + 3 + k * 2, n.x + 9, n.y + 3 + k * 2)
            tx += 4
        text(tx, n.y + n.h / 2 + 4.3, n.name)
        if n.expandable:
            toggle(n.x + n.w - TOG - 4, n.y + (n.h - TOG) / 2, not n.expanded)
        card(n)
    elif n.kind == 'group':
        x, y, w, h = n.x, n.y, COMP_W, COMP_H
        c = 6
        pts = f'{x+c},{y} {x+w-c},{y} {x+w},{y+c} {x+w},{y+h-c} {x+w-c},{y+h} {x+c},{y+h} {x},{y+h-c} {x},{y+c}'
        add(f'<polygon points="{pts}" transform="translate(3,3)" fill="#c8c8c8" stroke="none"/>')
        da = ' stroke-dasharray="4 2"' if optional else ''
        add(f'<polygon points="{pts}" fill="#ffffff" stroke="#000000" stroke-width="1.2"{da}/>')
        my = y + h / 2
        if n.model == 'sequence':
            line(x + 8, my, x + w - 8, my)
            for k in range(3):
                add(f'<rect x="{x + w/2 - 8 + k*6:.1f}" y="{my-2:.1f}" width="4" height="4" fill="#000000"/>')
        elif n.model == 'choice':
            line(x + 8, my, x + 15, my); line(x + 15, my, x + 21, my - 5)
            line(x + 21, my - 6, x + 21, my + 6)
            for k in (-4, 0, 4):
                add(f'<rect x="{x+23:.1f}" y="{my+k-1.5:.1f}" width="3" height="3" fill="#000000"/>')
            line(x + 28, my, x + w - 8, my)
        else:
            text(x + w / 2, my + 4, 'all', 'r', 'middle', 10)
        toggle(x + w + 2, y + (h - TOG) / 2, False)
        if n.max != '1':
            text(x + w - 2, y + h + 13, f'{n.min}..{n.max}', 'r', 'end', 11)
    elif n.kind == 'any':
        rect(n.x, n.y, n.w, n.h, optional)
        text(n.x + 8, n.y + n.h / 2 + 4.3, 'any ' + n.ns)
        if n.max != '1':
            text(n.x + n.w - 2, n.y + n.h + 13, f'{n.min}..{n.max}', 'r', 'end', 11)
    elif n.kind == 'constraints':
        rect(n.x, n.y, n.w, n.h, False, shadow=False)
        toggle(n.x + 6, n.y + (n.h - TOG) / 2, True)
        text(n.x + 10 + TOG, n.y + n.h / 2 + 4.3, 'constraints', 'i')
    elif n.kind == 'attrs':
        x, y, w, h = n.x, n.y, n.w, n.h
        tabw = tw('attributes', FONT_I) + 30
        add(f'<path d="M{x:.1f} {y+20:.1f} L{x:.1f} {y:.1f} L{x+tabw:.1f} {y:.1f} L{x+tabw+8:.1f} {y+8:.1f} '
            f'L{x+w:.1f} {y+8:.1f} L{x+w:.1f} {y+h:.1f} L{x:.1f} {y+h:.1f} Z" fill="#ffffff" stroke="#000000" stroke-width="1"/>')
        toggle(x + 5, y + 5, False)
        text(x + 18, y + 14, 'attributes', 'i')
        yy = y + 24
        for a, req in n.items:
            aw = tw(a) + 20
            rect(x + 14, yy, aw, ATT_H, not req)
            text(x + 24, yy + ATT_H / 2 + 4.3, a)
            yy += ATT_H + 5
    add('</g>')
    # connectors
    if getattr(n, 'split', None):
        sx = n.x + n.w + 2
        tx = sx + HGAP / 2 + 3
        k = n.split
        c1, c2 = n.children[:k], n.children[k:]
        ys1 = [cy(c) for c in c1]
        line(sx, cy(n), tx, cy(n))
        line(tx, n.bus_y, tx, max(ys1 + [cy(n)]))
        for c in c1:
            line(tx, cy(c), c.x, cy(c), dashed=(c.min == 0))
        tx2 = n.cx2 - HGAP / 2 - 3
        line(tx, n.bus_y, tx2, n.bus_y)
        ys2 = [cy(c) for c in c2]
        line(tx2, n.bus_y, tx2, max(ys2))
        for c in c2:
            line(tx2, cy(c), c.x, cy(c), dashed=(c.min == 0))
    elif n.children:
        sx = n.x + n.w + (2 if n.kind == 'el' else 0)
        tx = sx + HGAP / 2 + 3
        ys = [cy(c) for c in n.children]
        line(sx, cy(n), tx, cy(n))
        line(tx, min(ys + [cy(n)]), tx, max(ys + [cy(n)]))
        for c in n.children:
            line(tx, cy(c), c.x, cy(c), dashed=(c.min == 0))
    for c in n.children:
        draw(c)


def render(schema, root, expand=(), out='out.svg', title=None, split=None):
    S.clear()
    el = schema.elements[root]
    tree = build(schema, el, set(expand), frozenset(), set(), is_root=True)
    size(tree)
    if split:
        g = next(c for c in tree.children if c.kind == 'group')
        g.split = split
    subtree_h(tree)
    place(tree, 10, 10)
    b = bounds(tree)
    draw(tree)
    W, H = b[2] + 12, b[3] + 12
    body = '\n'.join(S)
    svg = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
           f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}">\n'
           f'<title>{escape(title or root)}</title>\n<rect x="0" y="0" width="{W:.0f}" height="{H:.0f}" fill="#ffffff"/>\n{body}\n</svg>\n')
    open(out, 'w', encoding='utf-8').write(svg)
    return W, H
