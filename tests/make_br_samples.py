#!/usr/bin/env python3
"""Generate businessRule samples for idmXSD v2.0 Rev 12 into samples/IDM/businessRule/r12/.
Usage: python3 tests/make_br_samples.py [repository root]
The window-cost conversion needs the Rev 11 source samples/WindowCostIDM_BusinessRules.xml (from the
IDMxPPM app repository); without it, the existing converted file is kept and reused as template."""
import copy, os, sys, uuid
from lxml import etree

REPO = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, 'TestCases/businessRule/r12')
NSU = 'https://standards.iso.org/iso/29481/-3/ed-2/en'
NS = '{%s}' % NSU
XL = '{http://www.w3.org/XML/1998/namespace}lang'
q = lambda n: NS + n
SRC = os.path.join(REPO, 'samples/WindowCostIDM_BusinessRules.xml')
CONVERT = os.path.exists(SRC)
src = etree.parse(SRC if CONVERT else os.path.join(OUT, 'WindowCostIDM_BusinessRules_r12.xml'))


def E(tag, parent=None, text=None, **a):
    a = {k.rstrip('_'): v for k, v in a.items()}
    e = etree.SubElement(parent, q(tag), a) if parent is not None else etree.Element(q(tag), a, nsmap={None: NSU})
    if text is not None:
        e.text = text
    return e


def rev13(el):
    """Revision 13: project phase instead of project stage; actor/@actorType removed."""
    for e in el.iter():
        if not isinstance(e.tag, str):
            continue
        if e.tag in (q('standardProjectStage'), q('localProjectStage')):
            e.tag = e.tag.replace('Stage', 'Phase')
        if e.tag == q('actor'):
            e.attrib.pop('actorType', None)


def write(tree_or_el, name, comment=None):
    el = tree_or_el.getroot() if hasattr(tree_or_el, 'getroot') else tree_or_el
    rev13(el)
    if comment:
        el.addprevious(etree.Comment(comment)) if el.getparent() is not None else None
    tree = etree.ElementTree(el)
    etree.indent(tree, space='  ')
    path = os.path.join(OUT, name)
    data = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', pretty_print=True)
    if comment:
        data = data.replace(b'?>\n', ('?>\n<!-- ' + comment + ' -->\n').encode(), 1)
    open(path, 'wb').write(data)
    return path


# ------------------------------------------------------------------ 1. convert the window-cost sample
def convert_business_rule(br):
    """Rev 11 / early Rev 12 forms -> Rev 12: one statement, images, description, reference."""
    kids = list(br)
    stmts, images, descs, refs = [], [], [], []
    for k in kids:
        tag = etree.QName(k).localname
        if tag == 'proposition':
            ds = k.findall(q('description'))
            for i, d in enumerate(ds):
                if i == 0 and not stmts:
                    stmts.append(('', d.get('title', '')))
                else:
                    descs.append(d)
                images += d.findall(q('image'))
        elif tag == 'statement':
            stmts.append((k.get(XL, ''), k.text or ''))
        elif tag == 'image':
            images.append(k)
        elif tag == 'description':
            descs.append(k)
        elif tag == 'reference':
            refs.append(k)
    for k in kids:
        br.remove(k)
    # translations are out of scope: keep the English statement, else the first one
    chosen = next((t for l, t in stmts if l.startswith('en')), stmts[0][1] if stmts else '')
    E('statement', br, chosen.strip())
    if images:
        imgs = E('images', br)
        for im in images:
            imgs.append(copy.deepcopy(im))
    for d in descs:
        if d.findall(q('image')):
            d = copy.deepcopy(d)
            for im in d.findall(q('image')):
                d.remove(im)
        br.append(copy.deepcopy(d))
    for rf in refs:
        br.append(rf)
    return [l for l, _ in stmts if l and not l.startswith('en')]


if CONVERT:
    conv = copy.deepcopy(src)
    r = conv.getroot()
    dropped = {}
    for br in r.iter(q('businessRule')):
        d = convert_business_rule(br)
        if d:
            dropped[br.get('id')] = d
    # add commentary to two rules to show the optional description
    brs = {b.get('id'): b for b in r.iter(q('businessRule'))}
    def add_desc(br, title):
        refs = br.findall(q('reference'))
        d = etree.Element(q('description'), title=title)
        if refs:
            refs[0].addprevious(d)
        else:
            br.append(d)
    add_desc(brs['BR-2'], 'Commentary: applies only to windows located in walls that form a fire-compartment boundary; '
                          'windows in other walls are not restricted by this rule.')
    add_desc(brs['BR-3'], 'Commentary: the window count refers to identical windows of one window type; '
                          'different sizes are recorded as separate window types.')
    spec = r.find(q('specId'))
    spec.set('shortTitle', 'WindowCostIDM_BusinessRules_r12')
    write(conv, 'WindowCostIDM_BusinessRules_r12.xml',
          'idmXSD v2.0 Rev 12 sample - converted from samples/WindowCostIDM_BusinessRules.xml: one statement per business rule '
          '(English kept; translations dropped: ' + ', '.join(f'{k}: {"/".join(v)}' for k, v in dropped.items()) +
          '), image -> images/image, commentary added as description for BR-2 and BR-3.')


# ------------------------------------------------------------------ helper: minimal IDM shell
def shell(short, full, code, summary, aim):
    root = E('idm')
    E('specId', root, guid=str(uuid.uuid5(uuid.NAMESPACE_URL, 'idmxsd-r12-' + short)), shortTitle=short,
      fullTitle=full, idmCode=code, documentStatus='WD')
    root.append(copy.deepcopy(src.getroot().find(q('authoring'))))
    uc = E('uc', root)
    uc.append(copy.deepcopy(root.find(q('specId'))))
    uc.find(q('specId')).set('guid', str(uuid.uuid5(uuid.NAMESPACE_URL, 'idmxsd-r12-uc-' + short)))
    uc.append(copy.deepcopy(root.find(q('authoring'))))
    E('description', E('summary', uc), title=summary)
    E('description', E('aimAndScope', uc), title=aim)
    E('language', uc, 'EN')
    E('use', uc, name='Check Code Compliance')
    E('type', E('region', uc, value='international'), 'USR')
    E('name', E('standardProjectPhase', uc), 'design')
    return root, uc


def er_shell(root, short):
    er = E('er', root)
    E('specId', er, guid=str(uuid.uuid5(uuid.NAMESPACE_URL, 'idmxsd-r12-er-' + short)), shortTitle=short + '_ER',
      fullTitle=short + ' exchange requirement', idmCode='ER-' + short, documentStatus='WD')
    er.append(copy.deepcopy(root.find(q('authoring'))))
    return er


def IU(er, id_, name, dt, definition, synonyms=(), ext=None):
    iu = E('informationUnit', er, id=id_, name=name, dataType=dt, isMandatory='true', definition=definition)
    for text, lang in synonyms:
        s = E('synonym', iu, text)
        if lang:
            s.set(XL, lang)
    if ext:
        E('correspondingExternalElement', iu, basis=ext[0], name=ext[1])
    return iu


# ------------------------------------------------------------------ 2. minimal
root, uc = shell('BR_minimal_r12', 'Minimal business rule sample (idmXSD v2.0 Rev 12)', 'BR-MIN-R12',
                 'Minimal IDM showing a business rule with a statement only.',
                 'Shows the smallest valid business rule: id, name and statement.')
br = E('businessRule', uc, id='BR-01', name='Minimum ceiling height of habitable rooms')
E('statement', br, 'The clear ceiling height of a habitable room shall be at least 2.2 m.')
write(root, 'BR_minimal_r12.xml', 'idmXSD v2.0 Rev 12 sample - minimal business rule (statement only).')
minimal = copy.deepcopy(root)

# ------------------------------------------------------------------ 3. full
root, uc = shell('BR_full_r12', 'Business rules linked to constraints (idmXSD v2.0 Rev 12)', 'BR-FULL-R12',
                 'IDM showing business rules with statements, images, commentary and references, linked from ER '
                 'constraints that state the rules informally and formally (RuleML, LegalRuleML, SPARQL, SHACL).',
                 'Fire resistance of load-bearing walls and of walls in fire-compartment boundaries.')
br = E('businessRule', uc, id='BR-07', name='Fire resistance of load-bearing walls')
E('statement', br, 'Load-bearing walls in buildings over 12 storeys shall have a fire resistance of at least 2 hours.')
imgs = E('images', br)
E('image', imgs, caption='Section of a fire-rated load-bearing wall', filePath='images/BR-07_wall_section.png')
E('image', imgs, caption='Building over 12 storeys with load-bearing walls highlighted', filePath='images/BR-07_building.png')
E('description', br, title='Commentary: applies to walls that carry vertical loads, including shear walls. '
                           'Non-load-bearing partitions are covered by BR-08.')
E('description', br, title='Commentary: the number of storeys is counted above ground level.')
E('reference', br, 'Building Act Enforcement Decree, Art. 56(1) (illustrative)')
E('reference', br, 'EN 13501-2 (classification of fire resistance)')
br = E('businessRule', uc, id='BR-08', name='Fire resistance of compartment walls')
E('statement', br, 'Walls that form a fire-compartment boundary shall have a fire resistance of at least 1 hour.')
E('reference', br, 'Building Act Enforcement Decree, Art. 46 (illustrative)')
uc.append(etree.Element(q('actor'), id='actor-1', name='Architect'))
uc.append(etree.Element(q('actor'), id='actor-2', name='Building Control Officer', external='true'))
E('reference', uc, basisStandard='false', fullCitation='Building Act Enforcement Decree (illustrative)')

er = er_shell(root, 'BR_full_r12')
# constraints first (schema order), information units after
c = E('constraint', er, id='C-07a')
E('associatedBusinessRule', c, ref='BR-07')
for ref in ('IU-012', 'IU-003', 'IU-021'):
    E('associatedInformationUnit', c, ref=ref)
E('description', c, title='IU-012 >= 2h WHERE IU-003 = true AND IU-021 > 12')
x = E('expression', c, id='C-07a-ruleml')
E('formalRuleLanguage', x, name='RuleML', version='1.03', uri='http://ruleml.org/spec')
x.append(etree.fromstring(
    '<Implies xmlns="http://ruleml.org/spec"><if><And>'
    '<Atom><Rel>isLoadBearing</Rel><Var>wall</Var><Data>true</Data></Atom>'
    '<Atom><Rel>numberOfStoreys</Rel><Var>bldg</Var><Var>n</Var></Atom>'
    '<Atom><Rel>greaterThan</Rel><Var>n</Var><Data>12</Data></Atom>'
    '</And></if><then><Atom><Rel>fireRatingAtLeast</Rel><Var>wall</Var><Data>PT2H</Data></Atom></then></Implies>'))
x = E('expression', c, id='C-07a-lrml')
E('formalRuleLanguage', x, name='LegalRuleML', version='1.0', publicationYear='2021', uri='http://docs.oasis-open.org/legalruleml/ns/v1.0/')
x.append(etree.fromstring(
    '<lrml:LegalRuleML xmlns:lrml="http://docs.oasis-open.org/legalruleml/ns/v1.0/" xmlns:ruleml="http://ruleml.org/spec">'
    '<lrml:Statements key="stmts-br07"><lrml:PrescriptiveStatement key="ps-br07"><ruleml:Rule closure="universal"/>'
    '</lrml:PrescriptiveStatement></lrml:Statements></lrml:LegalRuleML>'))
x = E('expression', c, id='C-07a-sparql')
E('formalRuleLanguage', x, name='SPARQL', version='1.1', publicationYear='2013')
x[-1].tail = None
cdata = etree.CDATA('\n        ASK { ?w :isLoadBearing true ; :fireRating ?r ; :inBuilding ?b .\n'
                    '              ?b :numberOfStoreys ?n .\n'
                    '              FILTER (?n > 12 && ?r < "PT2H"^^xsd:duration) }   # true = violation\n      ')
x[-1].tail = cdata
x = E('expression', c, id='C-07a-shacl', uri='rules/BR-07.shacl.ttl')
E('formalRuleLanguage', x, name='SHACL', publicationYear='2017', uri='http://www.w3.org/ns/shacl#')
c = E('constraint', er, id='C-08a')
E('associatedBusinessRule', c, ref='BR-08')
E('associatedInformationUnit', c, ref='IU-012')
E('associatedInformationUnit', c, ref='IU-030')
E('description', c, title='IU-012 >= 1h WHERE IU-030 = true (informal only)')
IU(er, 'IU-012', 'Fire rating', 'IfcLabel',
   'Fire resistance rating of the element, expressed as the period it maintains load-bearing capacity, integrity and insulation under standard fire test conditions.',
   [('Fire resistance rating', 'en'), ('FRR', 'en'), ('Period of fire resistance', 'en-GB'), ('내화등급', 'ko'), ('耐火性能', 'ja')],
   ('IFC4.3', 'Pset_WallCommon.FireRating'))
IU(er, 'IU-003', 'Is load-bearing', 'IfcBoolean', 'Whether the wall carries vertical loads.', [('Load bearing', 'en')],
   ('IFC4.3', 'Pset_WallCommon.LoadBearing'))
IU(er, 'IU-021', 'Number of storeys', 'IfcInteger', 'Number of storeys above ground level.', [('Storey count', 'en')])
IU(er, 'IU-030', 'Is compartment boundary', 'IfcBoolean', 'Whether the wall forms a fire-compartment boundary.',
   [('Compartmentation', 'en')], ('IFC4.3', 'Pset_WallCommon.Compartmentation'))
write(root, 'BR_full_r12.xml', 'idmXSD v2.0 Rev 12 sample - business rules with statement, images, commentary and '
                               'references, linked from constraints with informal and formal (RuleML, LegalRuleML, SPARQL, SHACL) expressions.')

# ------------------------------------------------------------------ 4. invalid samples (one defect each)
INVALID = [
    ('01_no_statement.xml', 'businessRule without statement', lambda b: b.remove(b.find(q('statement')))),
    ('02_two_statements.xml', 'two statements (one statement per business rule)',
     lambda b: b.find(q('statement')).addnext(copy.deepcopy(b.find(q('statement'))))),
    ('03_statement_with_xml_lang.xml', 'xml:lang on statement (translations are out of scope)',
     lambda b: b.find(q('statement')).set(XL, 'en')),
    ('04_empty_images.xml', 'images without image', lambda b: E('images', b)),
    ('05_image_without_images.xml', 'image directly under businessRule (must be inside images)',
     lambda b: E('image', b, caption='Section', filePath='images/x.png')),
    ('06_description_before_statement.xml', 'description before statement (order: statement, images, description, reference)',
     lambda b: b.insert(0, etree.Element(q('description'), title='Commentary'))),
    ('07_proposition_ed2.xml', 'ed. 2 proposition wrapper (removed in Rev 12)',
     lambda b: (b.remove(b.find(q('statement'))),
                E('description', E('proposition', b), title='The clear ceiling height of a habitable room shall be at least 2.2 m.'),
                b.insert(0, b.find(q('proposition'))))),
    ('08_empty_statement.xml', 'empty statement', lambda b: setattr(b.find(q('statement')), 'text', '')),
]
lines = ['# Invalid businessRule samples (idmXSD v2.0 Rev 12)', '',
         'Each file is `BR_minimal_r12.xml` with exactly one defect. All must be rejected by the schema.', '',
         '| File | Defect |', '|---|---|']
for fn, why, fx in INVALID:
    t = copy.deepcopy(minimal)
    b = t.find('.//' + q('businessRule'))
    fx(b)
    t.find(q('specId')).set('shortTitle', 'BR_invalid_' + fn[:2])
    tree = etree.ElementTree(t); etree.indent(tree, space='  ')
    data = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', pretty_print=True)
    data = data.replace(b'?>\n', ('?>\n<!-- INVALID on purpose (idmXSD v2.0 Rev 12): ' + why + ' -->\n').encode(), 1)
    open(os.path.join(OUT, 'invalid', fn), 'wb').write(data)
    lines.append(f'| `{fn}` | {why} |')
open(os.path.join(OUT, 'invalid', 'README.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('generated into', OUT)
