#!/usr/bin/env python3
"""idmXSD v2.0 regression and feature tests (Revisions 10-13).

Usage:  python3 tests/run_tests.py [repository root]
Runs every case against BOTH the monolithic and the modularized schema and
checks that each gives the expected result. Exit code 1 on any unexpected result.
Requires lxml.
"""
import copy, glob, os, sys, uuid
from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
XSD_DIR = os.path.dirname(HERE)
REPO = sys.argv[1] if len(sys.argv) > 1 else XSD_DIR
NS = 'https://standards.iso.org/iso/29481/-3/ed-2/en'
XL = '{http://www.w3.org/XML/1998/namespace}lang'
q = lambda n: '{%s}%s' % (NS, n)

SCHEMA_FILES = {
    'mono': os.path.join(XSD_DIR, 'Monolithic/idm_monolithic_V2.0.xsd'),
    'mod':  os.path.join(XSD_DIR, 'Modularized/idm.xsd'),
}
LXML = {k: etree.XMLSchema(etree.parse(p)) for k, p in SCHEMA_FILES.items()}
BASE_FILE = os.path.join(REPO, 'TestCases/businessRule/r12/WindowCostIDM_BusinessRules_r12.xml')  # fixture base

results = []  # (group, name, expected, {schema: (ok, msg)})

def check(group, name, tree, expect_valid, known=None):
    """known: {engine-prefix: reason} for documented validator deviations from XSD 1.0."""
    results.append((group, name, expect_valid, tree, known or {}))

def E(tag, parent=None, text=None, **attrs):
    attrs = {k.rstrip('_'): v for k, v in attrs.items()}
    e = etree.SubElement(parent, q(tag), attrs) if parent is not None else etree.Element(q(tag), attrs)
    if text is not None: e.text = text
    return e

def X(s):  # parse an XML snippet in the idm namespace
    return etree.fromstring(s.replace('<idm ', f'<idm xmlns="{NS}" ', 1) if s.startswith('<idm ') else s)

# ---------------------------------------------------------------- fixture
BASE = etree.parse(BASE_FILE)
SUB_ER_TEMPLATE = None
for sub in BASE.getroot().find(q('er')).iter(q('subEr')):
    SUB_ER_TEMPLATE = sub.find(q('er')); break

def IU(id_, name, children=()):
    iu = E('informationUnit', id=id_, name=name, dataType='IfcLabel', isMandatory='true', definition=name)
    for c in children: iu.append(c)
    return iu

def make_sub_er(ius, depth_chain=0, leaf_ius=()):
    er = etree.Element(q('er'))
    er.append(copy.deepcopy(SUB_ER_TEMPLATE.find(q('specId'))))
    er.find(q('specId')).set('guid', str(uuid.uuid4()))
    er.append(copy.deepcopy(SUB_ER_TEMPLATE.find(q('authoring'))))
    for iu in ius: er.append(iu)
    if depth_chain:
        s = E('subEr', er); s.append(make_sub_er(leaf_ius, depth_chain - 1, leaf_ius) if depth_chain > 1 else make_sub_er(leaf_ius))
    return er

def fixture(constraints=(), sub_constraints=(), br_ids=('BR-07', 'BR-08'), chain=0, chain_constraints=(), iu_ids_top=None, br_xml=None):
    """Top ER: IU-012 (with nested IU-012a), IU-003, IU-021; sub-ER with IU-S1.
    chain>0 builds an extra chain of nested sub-ERs; chain_constraints go into the deepest one."""
    t = copy.deepcopy(BASE); r = t.getroot(); uc = r.find(q('uc'))
    pos = list(uc).index(uc.find(q('actor')))
    if br_xml is not None:
        uc.insert(pos, X(br_xml)); br_ids = ()
    for i, b in enumerate(br_ids):
        br = etree.Element(q('businessRule'), id=b, name='Rule ' + b)
        E('statement', br, text='Statement of ' + b)
        uc.insert(pos + i, br)
    er = r.find(q('er'))
    for c in list(er):
        if c.tag in (q('informationUnit'), q('subEr'), q('constraint')): er.remove(c)
    after = list(er).index(er.find(q('authoring'))) + 1
    for i, c in enumerate(constraints): er.insert(after + i, X(c) if isinstance(c, str) else c)
    for iu in (iu_ids_top or [IU('IU-012', 'Fire rating', [E_sub(IU('IU-012a', 'Fire rating basis'))]),
                              IU('IU-003', 'Is load-bearing'), IU('IU-021', 'Number of storeys')]):
        er.append(iu)
    sub = make_sub_er([IU('IU-S1', 'Wall type')])
    a = list(sub).index(sub.find(q('authoring'))) + 1
    for i, c in enumerate(sub_constraints): sub.insert(a + i, X(c))
    E('subEr', er).append(sub)
    if chain:
        deep = make_sub_er([IU('IU-D0', 'chain 0')])
        cur = deep
        for d in range(1, chain):
            nxt = make_sub_er([IU(f'IU-D{d}', f'chain {d}')]); E('subEr', cur).append(nxt); cur = nxt
        a = list(cur).index(cur.find(q('authoring'))) + 1
        for i, c in enumerate(chain_constraints): cur.insert(a + i, X(c))
        E('subEr', er).append(deep)
    return t

def E_sub(iu):
    s = etree.Element(q('subInformationUnit')); s.append(iu); return s

def C(body, id_='C-1'):
    return f'<constraint xmlns="{NS}" id="{id_}">{body}</constraint>'

BR = lambda r: f'<associatedBusinessRule ref="{r}"/>'
IUR = lambda r: f'<associatedInformationUnit ref="{r}"/>'
DESC = '<description title="IU-012 &gt;= 2h WHERE IU-003 = true AND IU-021 &gt; 12"/>'
FRL = lambda **a: '<formalRuleLanguage ' + ' '.join(f'{k}="{v}"' for k, v in a.items()) + '/>'
RULEML = ('<Implies xmlns="http://ruleml.org/spec"><if><Atom><Rel>isLoadBearing</Rel><Var>w</Var></Atom></if>'
          '<then><Atom><Rel>fireRatingAtLeast</Rel><Var>w</Var><Data>PT2H</Data></Atom></then></Implies>')
LRML = ('<lrml:LegalRuleML xmlns:lrml="http://docs.oasis-open.org/legalruleml/ns/v1.0/" xmlns:ruleml="http://ruleml.org/spec">'
        '<lrml:Statements key="s"><lrml:PrescriptiveStatement key="ps"><ruleml:Rule closure="universal"/>'
        '</lrml:PrescriptiveStatement></lrml:Statements></lrml:LegalRuleML>')
EXPR = lambda frl, body='', **a: '<expression ' + ' '.join(f'{k}="{v}"' for k, v in a.items()) + f'>{frl}{body}</expression>'
FULL = C(BR('BR-07') + IUR('IU-012') + IUR('IU-003') + IUR('IU-021') + DESC
         + EXPR(FRL(name='RuleML', version='1.03', uri='http://ruleml.org/spec'), RULEML, id='e1')
         + EXPR(FRL(name='LegalRuleML', version='1.0', publicationYear='2021',
                    uri='http://docs.oasis-open.org/legalruleml/ns/v1.0/'), LRML, id='e2')
         + EXPR(FRL(name='SPARQL', version='1.1', publicationYear='2013'),
                '<![CDATA[ ASK { ?w :fireRating ?r . FILTER (?r < "PT2H"^^xsd:duration) } ]]>', id='e3')
         + EXPR(FRL(name='SHACL', publicationYear='2017', uri='http://www.w3.org/ns/shacl#'), '', id='e4',
                uri='rules/BR-07.shacl.ttl'), 'C-07a')

# ---------------------------------------------------------------- A. sample regression
for f in sorted(glob.glob(os.path.join(REPO, 'TestCases/**/*.xml'), recursive=True)):
    try: t = etree.parse(f)
    except etree.XMLSyntaxError: continue
    if t.getroot().tag != q('idm'): continue
    rel = os.path.relpath(f, REPO)
    ids = [iu.get('id') for iu in t.iter(q('informationUnit'))]
    dup = sorted({i for i in ids if ids.count(i) > 1 and len(list(t.getroot().iter(q('er')))) > 1})
    exp = False if '/invalid/' in rel else (True if '/businessRule/' in rel else None)
    check('A. samples', rel, t, exp)
    if dup:
        t2 = copy.deepcopy(t); n = 0
        for iu in t2.iter(q('informationUnit')):
            if iu.get('id') in dup: n += 1; iu.set('id', f"{iu.get('id')}-{n}")
        check('A. samples', rel + '  [duplicate IU ids made unique: ' + ', '.join(dup) + ']', t2, None)

# ---------------------------------------------------------------- B. constraint links
g = 'B. constraint links'
check(g, 'full example (BR-07, 3 IUs, informal + 4 formal expressions)', fixture([FULL]), True)
check(g, 'constraint with id only', fixture([C('')]), True)
check(g, 'informal-only constraint', fixture([C(BR('BR-07') + IUR('IU-012') + DESC)]), True)
check(g, 'one constraint linked to two business rules', fixture([C(BR('BR-07') + BR('BR-08') + IUR('IU-012'))]), True)
check(g, 'one business rule decomposed into two constraints', fixture([C(BR('BR-07') + IUR('IU-012'), 'C-a'), C(BR('BR-07') + IUR('IU-021'), 'C-b')]), True)
check(g, 'unknown business rule ref', fixture([C(BR('BR-99'))]), False)
check(g, 'unknown information unit ref', fixture([C(IUR('IU-999'))]), False)
check(g, 'ref to nested subInformationUnit (IU-012a)', fixture([C(IUR('IU-012a'))]), True)
check(g, 'top-level constraint -> IU in sub-ER (IU-S1)', fixture([C(IUR('IU-S1'))]), True)
check(g, 'sub-ER constraint -> its own IU', fixture(sub_constraints=[C(IUR('IU-S1'), 'C-s')]), True)
check(g, 'sub-ER constraint -> parent ER IU', fixture(sub_constraints=[C(IUR('IU-012'), 'C-s')]), True)
check(g, 'sub-ER constraint -> nested subInformationUnit of parent ER', fixture(sub_constraints=[C(IUR('IU-012a'), 'C-s')]), True)
check(g, 'sub-ER constraint -> unknown IU', fixture(sub_constraints=[C(IUR('IU-999'), 'C-s')]), False)
check(g, 'deep sub-ER (level 3) constraint -> top-level IU', fixture(chain=3, chain_constraints=[C(IUR('IU-021'), 'C-d')]), True)
check(g, 'top-level constraint -> IU in deep sub-ER (level 3)', fixture([C(IUR('IU-D2'))], chain=3), True)
check(g, 'same constraint id in two different sub-ERs (per-ER scope)', fixture([C('', 'C-x')], sub_constraints=[C('', 'C-x')]), True)
check(g, 'duplicate constraint id within one sub-ER', fixture(sub_constraints=[C('', 'C-y'), C('', 'C-y')]), False)
check(g, 'sub-ER constraint -> known business rule', fixture(sub_constraints=[C(BR('BR-07'), 'C-s')]), True)
check(g, 'sub-ER constraint -> unknown business rule', fixture(sub_constraints=[C(BR('BR-99'), 'C-s')]), False)
for depth, exp in ((5, False), (6, True)):
    # chain of `depth` nested ERs below top-level er (the first sits at sub-ER level 1, deepest at level `depth`)
    check(g, f'unknown business rule in sub-ER at nesting level {depth}' + (' (beyond XSD coverage -> app check)' if exp else ''),
          fixture(chain=depth, chain_constraints=[C(BR('BR-99'), 'C-d')]), exp)
check(g, 'duplicate constraint id in same ER', fixture([C('', 'C-x'), C('', 'C-x')]), False)
check(g, 'duplicate IU id across top ER and sub-ER',
      fixture(iu_ids_top=[IU('IU-012', 'a'), IU('IU-S1', 'clash')]), False)
check(g, 'ed.2 attribute form (removed)', fixture([f'<constraint xmlns="{NS}" id="C-old" associatedInformationUnit="IU-012" associatedBusinessRule="BR-07"/>']), False)
check(g, 'wrong child order (description before links)', fixture([C(DESC + BR('BR-07'))]), False)
check(g, 'wrong child order (expression before description)', fixture([C(EXPR(FRL(name='RuleML')) + DESC)]), False)
check(g, 'associatedBusinessRule without ref', fixture([C('<associatedBusinessRule/>')]), False)
check(g, 'associatedInformationUnit without ref', fixture([C('<associatedInformationUnit/>')]), False)

# ---------------------------------------------------------------- C. expression / formalRuleLanguage
g = 'C. expression'
ok_frl = FRL(name='RuleML')
check(g, 'formalRuleLanguage name only', fixture([C(EXPR(ok_frl))]), True)
check(g, 'formalRuleLanguage all attributes', fixture([C(EXPR(FRL(name='LegalRuleML', version='1.0', publicationYear='2021', uri='http://docs.oasis-open.org/legalruleml/ns/v1.0/')))]), True)
check(g, 'formalRuleLanguage without name', fixture([C(EXPR(FRL(version='1.0')))]), False)
check(g, 'publicationYear not a year ("21")', fixture([C(EXPR(FRL(name='RuleML', publicationYear='21')))]), False)
check(g, 'publicationYear as date ("2021-08-30")', fixture([C(EXPR(FRL(name='RuleML', publicationYear='2021-08-30')))]), False)
check(g, 'unknown attribute on formalRuleLanguage', fixture([C(EXPR(FRL(name='RuleML', vendor='x')))]), False)
check(g, 'expression without formalRuleLanguage', fixture([C('<expression>text</expression>')]), False)
check(g, 'two formalRuleLanguage in one expression', fixture([C(EXPR(ok_frl + ok_frl))]), False)
check(g, 'formalRuleLanguage after rule markup', fixture([C(f'<expression>{RULEML}{ok_frl}</expression>')]), False)
check(g, 'embedded RuleML', fixture([C(EXPR(ok_frl, RULEML))]), True)
check(g, 'embedded LegalRuleML', fixture([C(EXPR(FRL(name='LegalRuleML'), LRML))]), True)
check(g, 'two foreign-namespace roots in one expression', fixture([C(EXPR(ok_frl, RULEML + LRML))]), True)
check(g, 'CDATA text (SPARQL)', fixture([C(EXPR(FRL(name='SPARQL'), '<![CDATA[ SELECT * WHERE { ?s ?p ?o } ]]>'))]), True)
check(g, 'plain text with escaped markup', fixture([C(EXPR(FRL(name='Python'), 'assert rating &gt;= 2  # &lt;ok&gt;'))]), True)
check(g, 'external rule file via @uri, no body', fixture([C(EXPR(FRL(name='SHACL'), '', uri='rules/x.ttl'))]), True)
check(g, 'idm-namespace element inside expression', fixture([C(EXPR(ok_frl, '<description title="x"/>'))]), False)
check(g, 'no-namespace element inside expression (must use a namespace or CDATA)', fixture([C(EXPR(ok_frl, '<rule xmlns=""/>'))]), False)
check(g, 'bogus RuleML content accepted (lax, no RuleML schema loaded)', fixture([C(EXPR(ok_frl, '<NotARuleMLElement xmlns="http://ruleml.org/spec"/>'))]), True)
check(g, 'several expressions in the same language', fixture([C(EXPR(ok_frl, RULEML) + EXPR(ok_frl, RULEML))]), True)
check(g, 'expression outside constraint (on informationUnit)',
      fixture(iu_ids_top=[X(f'<informationUnit xmlns="{NS}" id="IU-012" name="a" dataType="x" isMandatory="true" definition="d">{EXPR(ok_frl)}</informationUnit>')]), False)

# ---------------------------------------------------------------- D. synonyms (Revision 10) + combination
g = 'D. synonyms'
def syn_iu(syns, extra=''):
    body = ''.join(f'<synonym{" xml:lang=%s" % chr(34) + l + chr(34) if l else ""}>{t}</synonym>' for t, l in syns)
    return X(f'<informationUnit xmlns="{NS}" id="IU-012" name="Fire rating" dataType="IfcLabel" isMandatory="true" definition="d">{body}{extra}</informationUnit>')
SYN = [('Fire resistance rating', 'en'), ('FRR', 'en'), ('Period of fire resistance', 'en-GB'), ('내화등급', 'ko'),
       ('耐火性能', 'ja'), ('耐火等级', 'zh-CN'), ('Feuerwiderstandsklasse', 'de'), ('Résistance au feu', 'fr'), ('untagged', None)]
check(g, 'multilingual synonyms', fixture(iu_ids_top=[syn_iu(SYN)]), True)
check(g, 'same text in two languages', fixture(iu_ids_top=[syn_iu([('Fire rating', 'en'), ('Fire rating', 'en-GB')])]), True)
check(g, 'duplicate synonym in same language', fixture(iu_ids_top=[syn_iu([('FRR', 'en'), ('FRR', 'en')])]), False)
check(g, 'duplicate untagged synonym (not caught -> app check)', fixture(iu_ids_top=[syn_iu([('FRR', None), ('FRR', None)])]), True,
      known={'xmlschema-py': 'checks xs:unique rows with an absent field; XSD 1.0 excludes them'})
check(g, 'invalid language tag', fixture(iu_ids_top=[syn_iu([('x', 'english language')])]), False)
check(g, 'empty synonym', fixture(iu_ids_top=[syn_iu([('', 'en')])]), False)
check(g, 'synonym after correspondingExternalElement', fixture(iu_ids_top=[syn_iu([], '<correspondingExternalElement basis="IFC4.3" name="Pset_WallCommon.FireRating"/><synonym>late</synonym>')]), False)
check(g, 'synonyms + full constraint together',
      fixture([FULL.replace(IUR('IU-003') + IUR('IU-021'), '')], iu_ids_top=[syn_iu(SYN, '<correspondingExternalElement basis="IFC4.3" name="Pset_WallCommon.FireRating"/>')]), True)

# ---------------------------------------------------------------- E. sub-IDM scoping
g = 'E. sub-IDM'
def with_sub_idm(outer_constraints=(), inner_constraints=(), inner_brs=('BR-07',)):
    t = fixture(outer_constraints); r = t.getroot()
    inner = fixture(inner_constraints, br_ids=inner_brs).getroot()
    E('subIdm', r).append(inner)
    return t
check(g, 'sub-IDM reuses business rule id BR-07 (own scope)', with_sub_idm([C(BR('BR-07'))], [C(BR('BR-07'))]), True,
      known={'libxml2': 'merges key tables of nested idm scopes -> reports ambiguous match (pre-existing, not Rev. 11)'})
check(g, 'sub-IDM constraint -> outer IDM business rule', with_sub_idm(inner_constraints=[C(BR('BR-08'))], inner_brs=('BR-X',)), False)
check(g, 'sub-IDM reuses information unit ids (own ER scope)', with_sub_idm([C(IUR('IU-012'))], [C(IUR('IU-012'))]), True)

# ---------------------------------------------------------------- F. businessRule/statement (Revision 12)
g = 'F. businessRule (Rev 12)'
def BRX(body, id_='BR-07'):
    return f'<businessRule xmlns="{NS}" id="{id_}" name="Fire resistance of load-bearing walls">{body}</businessRule>'
EN = 'Load-bearing walls in buildings over 12 storeys shall have a fire resistance of at least 2 hours.'
ST = f'<statement>{EN}</statement>'
IMG = '<image caption="Fire-rated wall section" filePath="img/br07.png"/>'
IMGS = f'<images>{IMG}</images>'
DSC = '<description title="Commentary: applies to walls that carry vertical loads."/>'
REF = '<reference>Building Act Enforcement Decree, Art. 56(1)</reference>'
check(g, 'statement only', fixture(br_xml=BRX(ST)), True)
check(g, 'statement + images + description + reference', fixture([C(BR('BR-07'))], br_xml=BRX(ST + IMGS + DSC + DSC + REF)), True)
check(g, 'images with two images', fixture(br_xml=BRX(ST + f'<images>{IMG}{IMG}</images>')), True)
check(g, 'statement + description (no images)', fixture(br_xml=BRX(ST + DSC)), True)
check(g, 'no statement', fixture(br_xml=BRX(IMGS + REF)), False)
check(g, 'empty statement', fixture(br_xml=BRX('<statement></statement>')), False)
check(g, 'two statements', fixture(br_xml=BRX(ST + ST)), False)
check(g, 'statement with xml:lang (translations out of scope)', fixture(br_xml=BRX(f'<statement xml:lang="en">{EN}</statement>')), False)
check(g, 'empty images', fixture(br_xml=BRX(ST + '<images/>')), False)
check(g, 'two images groups', fixture(br_xml=BRX(ST + IMGS + IMGS)), False)
check(g, 'image directly under businessRule', fixture(br_xml=BRX(ST + IMG)), False)
check(g, 'description before images', fixture(br_xml=BRX(ST + DSC + IMGS)), False)
check(g, 'reference before description', fixture(br_xml=BRX(ST + REF + DSC)), False)
check(g, 'statement after images', fixture(br_xml=BRX(IMGS + ST)), False)
check(g, 'ed.2 proposition wrapper (removed)', fixture(br_xml=BRX(f'<proposition><description title="{EN}"/></proposition>')), False)
check(g, 'constraint -> business rule defined with statement', fixture([C(BR('BR-07') + IUR('IU-012'))], br_xml=BRX(ST + REF)), True)

# ---------------------------------------------------------------- G. project phase + actor role (Revision 13)
g = 'G. phase + actor (Rev 13)'
def uc_variant(phases=None, actors=None):
    """Replace the fixture's standardProjectPhase/localProjectPhase (phases) and/or actor elements (actors)."""
    t = fixture(); uc = t.getroot().find(q('uc'))
    if phases is not None:
        old = [c for c in uc if etree.QName(c).localname in ('standardProjectPhase', 'localProjectPhase',
                                                            'standardProjectStage', 'localProjectStage')]
        pos = list(uc).index(old[0])
        for c in old: uc.remove(c)
        for i, p in enumerate(phases): uc.insert(pos + i, X(p))
    if actors is not None:
        old = uc.findall(q('actor')); pos = list(uc).index(old[0])
        for c in old: uc.remove(c)
        for i, a in enumerate(actors): uc.insert(pos + i, X(a))
    return t
SP = lambda n, tag='standardProjectPhase': f'<{tag} xmlns="{NS}"><name>{n}</name></{tag}>'
LP = lambda n, tag='localProjectPhase': (f'<{tag} xmlns="{NS}"><name>{n}</name>'
                                         f'<classification id="cls-riba" name="RIBA Plan of Work" publicationYear="2020"/></{tag}>')
A = lambda attrs='', body='': f'<actor xmlns="{NS}" id="a-{abs(hash(attrs + body)) % 10**6}" name="Role {abs(hash(attrs + body)) % 10**6}" {attrs}>{body}</actor>'
check(g, 'standardProjectPhase (two ISO 22263 phases)', uc_variant([SP('brief'), SP('design')]), True)
check(g, 'standardProjectPhase + localProjectPhase (RIBA)', uc_variant([SP('design'), LP('Stage 4 Technical Design')]), True)
check(g, 'standardProjectStage (renamed, removed)', uc_variant([SP('design', 'standardProjectStage')]), False)
check(g, 'localProjectStage (renamed, removed)', uc_variant([SP('design'), LP('Stage 4', 'localProjectStage')]), False)
check(g, 'no standardProjectPhase (1..* required)', uc_variant([LP('Stage 4')]), False)
check(g, 'duplicate standardProjectPhase name', uc_variant([SP('design'), SP('design')]), False)
check(g, 'standardProjectPhase name outside ISO 22263 list', uc_variant([SP('operation')]), False)
check(g, 'actor without external (default false)', uc_variant(actors=[A()]), True)
check(g, 'actor external="true" (external actor role)', uc_variant(actors=[A(), A('external="true"')]), True)
check(g, 'actor external="false"', uc_variant(actors=[A('external="false"')]), True)
check(g, 'actor external="1" (xs:boolean lexical form)', uc_variant(actors=[A('external="1"')]), True)
check(g, 'actor external="yes" (not xs:boolean)', uc_variant(actors=[A('external="yes"')]), False)
check(g, 'actor actorType="group" (removed)', uc_variant(actors=[A('actorType="group"')]), False)
check(g, 'external composite actor role with subActors',
      uc_variant(actors=[A('external="true"', '<subActor id="s-1" name="Plan reviewer"/><subActor id="s-2" name="Fire officer"/>')]), True)
check(g, 'external on subActor (only on actor)', uc_variant(actors=[A('', '<subActor id="s-1" name="x" external="true"/>')]), False)

# ---------------------------------------------------------------- engines
import shutil, subprocess, tempfile
tmp = tempfile.mkdtemp(prefix='idmxsd-tests-')
files = []
for i, (_, _, _, t, _) in enumerate(results):
    fp = os.path.join(tmp, f'case{i:03d}.xml'); t.write(fp, xml_declaration=True, encoding='UTF-8'); files.append(fp)

def run_lxml(key):
    out = []
    for fp in files:
        s = LXML[key]; ok = s.validate(etree.parse(fp))
        out.append((ok, '' if ok else s.error_log.last_error.message))
    return out

def run_java(key):
    java = shutil.which('java')
    if not java: return None
    p = subprocess.run([java, os.path.join(HERE, 'Validate.java'), SCHEMA_FILES[key]] + files,
                       capture_output=True, text=True)
    res = {}
    for line in p.stdout.splitlines():
        parts = line.split('\t')
        if parts[0] in ('OK', 'ERR'): res[parts[1]] = (parts[0] == 'OK', parts[2] if len(parts) > 2 else '')
    if len(res) != len(files): print('java validator error:', p.stderr[-500:]); return None
    return [res[f] for f in files]

def run_xmlschema(key):
    try: import xmlschema
    except ImportError: return None
    sch = xmlschema.XMLSchema10(SCHEMA_FILES[key])
    out = []
    for fp in files:
        errs = list(sch.iter_errors(fp))
        out.append((not errs, '' if not errs else str(errs[0].reason or errs[0].message)))
    return out

ENGINES = {}
for key in SCHEMA_FILES:
    ENGINES[f'libxml2/{key}'] = run_lxml(key)
    j = run_java(key)
    if j is not None: ENGINES[f'xerces-jdk/{key}'] = j
    x = run_xmlschema(key)
    if x is not None: ENGINES[f'xmlschema-py/{key}'] = x
shutil.rmtree(tmp, ignore_errors=True)
names = list(ENGINES)
print('Engines:', ', '.join(names))

# ---------------------------------------------------------------- report
fail = 0
cur = None
for i, (group, name, exp, _, known) in enumerate(results):
    if group != cur: print(f'\n## {group}'); cur = group
    def is_known(e): return any(e.startswith(k) for k in known)
    strict = [e for e in names if not is_known(e)]
    ref = ENGINES[strict[0]][i]
    vals = {ENGINES[e][i][0] for e in strict}
    agree = len(vals) == 1
    if exp is None: status = 'info' if agree else 'DISAGREE'
    else: status = 'pass' if (agree and ref[0] == exp) else ('DISAGREE' if not agree else 'FAIL')
    if status in ('FAIL', 'DISAGREE'): fail += 1
    v = 'valid' if ref[0] else 'INVALID'
    msg = '' if ref[0] else '  — ' + ref[1].replace('{%s}' % NS, 'idm:')[:100]
    print(f'[{status:8s}] {v:7s} {name}{msg}')
    for e in names:
        ok, m = ENGINES[e][i]
        if not agree or (is_known(e) and ok != ref[0]):
            note = ('  [known deviation: ' + next(r for k, r in known.items() if e.startswith(k)) + ']') if is_known(e) else ''
            print(f'             {e:22s} {"valid" if ok else "INVALID"}{note}  {m[:100]}')
n = sum(1 for x in results if x[2] is not None)
print(f'\n{n} expectation cases + {len(results) - n} sample files x {len(names)} engine/schema combinations; '
      f'{fail} failures or disagreements')
sys.exit(1 if fail else 0)
