# idmXSD v2.0 — Revisions 10–12: Summary of Changes and Examples

**Standard:** ISO 29481-3 (ed. 2) — Information delivery manual — Data schema (idmXML)
**Schema files:** `monolithic/idm_monolithic_V2.0.xsd`, `modularized/*.xsd` (+ new `xml.xsd` in both folders)
**Date:** 9 October 2026

---

## 1. Overview

| Rev | Change | Kind |
|---|---|---|
| 10 | `informationUnit/synonym` — alternative names and translations, tagged with `xml:lang` | Extension (backward compatible) |
| 11 | `constraint` links become repeatable child elements (`associatedBusinessRule`, `associatedInformationUnit`); the old attributes are removed | **Breaking** |
| 11 | New `expression` and `formalRuleLanguage` elements for formal statements of a constraint (RuleML, LegalRuleML, SPARQL, SHACL, …) | Extension |
| 11 | Information-unit ids unique across the whole ER tree; `er` gets a named type `erType` | Identity constraints |
| 12 | `businessRule/proposition` replaced by `statement` (1..1), optional `images` and optional `description` (commentary) | **Breaking** |

**Conceptual model:**

```
uc/businessRule  ◄── associatedBusinessRule/@ref ──  er/constraint  ── associatedInformationUnit/@ref ──►  informationUnit
 (statement = rule in natural language)                 │
                                                        ├── description   (informal statement)
                                                        └── expression*   (formal statement, one rule language each)
                                                              └── formalRuleLanguage (name, version, publicationYear, uri)
```

- A **business rule** in the use case can be represented by one or more **constraints** in the ER.
- A **constraint** is one logical restriction. It is stated informally (`description`) and/or formally in one or more rule languages (`expression`).
- **Equivalent formal expressions** of the same restriction belong to the same constraint.
- **A rule that breaks down into separate checks** is referenced by several constraints.

---

## 2. Schema changes

### 2.1 Revision 10 — Synonyms (`informationUnit/synonym`)

- **New element:** `synonym` (0..\*), placed directly after `description` inside `informationUnit`.
- **Content:** `idm:synonymText`, an `xs:normalizedString` with `minLength` 1, so it cannot be empty.
- **Attribute:** `xml:lang` (optional). The value is a BCP 47 language tag such as `en`, `en-GB`, `ko`, `ja` or `zh-CN`.
- **Uniqueness rule:** `unique_synonymPerLanguage` rejects the same synonym twice within one language. The same text in different languages is allowed.
- **Preferred term:** the `name` attribute remains the preferred term.
- **`xml.xsd`:** a minimal local copy of the W3C schema for the XML namespace (`xml:lang` only), imported so that validation works offline. It must be distributed with the schema files.

```xml
<xs:element name="synonym" minOccurs="0" maxOccurs="unbounded">
  <xs:complexType>
    <xs:simpleContent>
      <xs:extension base="idm:synonymText">
        <xs:attribute ref="xml:lang" use="optional"/>
      </xs:extension>
    </xs:simpleContent>
  </xs:complexType>
</xs:element>
```

### 2.2 Revision 11 — Constraint links (breaking)

**Before (ed. 2 draft):** single-valued attributes

```xml
<constraint id="C-1" associatedInformationUnit="IU-012" associatedBusinessRule="BR-07"/>
```

**After:** repeatable child elements, each with a required `ref` attribute

```xml
<constraint id="C-1">
  <associatedBusinessRule ref="BR-07"/>
  <associatedInformationUnit ref="IU-012"/>
  <associatedInformationUnit ref="IU-021"/>
</constraint>
```

The new child order is: `associatedBusinessRule` (0..\*), then `associatedInformationUnit` (0..\*), then `description` (0..\*), then `expression` (0..\*).

**Migration (importer/exporter):**

- `@associatedBusinessRule="X"` becomes `<associatedBusinessRule ref="X"/>`.
- `@associatedInformationUnit="Y"` becomes `<associatedInformationUnit ref="Y"/>`.

### 2.3 Revision 11 — `expression` and `formalRuleLanguage`

```xml
<xs:element name="expression">
  <xs:complexType mixed="true">
    <xs:sequence>
      <xs:element ref="idm:formalRuleLanguage" minOccurs="1" maxOccurs="1"/>
      <xs:any namespace="##other" processContents="lax" minOccurs="0" maxOccurs="unbounded"/>
    </xs:sequence>
    <xs:attribute name="id"  type="xs:string" use="optional"/>
    <xs:attribute name="uri" type="xs:anyURI" use="optional"/>
  </xs:complexType>
</xs:element>

<xs:element name="formalRuleLanguage">
  <xs:complexType>
    <xs:attribute name="name"            type="xs:string" use="required"/>
    <xs:attribute name="version"         type="xs:string" use="optional"/>
    <xs:attribute name="publicationYear" type="xs:gYear"  use="optional"/>
    <xs:attribute name="uri"             type="xs:anyURI" use="optional"/>
  </xs:complexType>
</xs:element>
```

An `expression` holds the rule in one of three forms:

| Form | Example languages | How |
|---|---|---|
| XML markup in its own namespace | RuleML, LegalRuleML | embedded elements (`xs:any ##other`, `lax`) |
| Text | SPARQL, SHACL (Turtle), Python | character data, preferably CDATA (`mixed="true"`) |
| External file | any | empty body plus `@uri` |

Rules on the content:

- Elements in the IDM namespace are not allowed inside `expression`.
- XML without a namespace is also not allowed; it must be put in CDATA instead.
- Embedded rule markup is only checked if the validator has that language's schema loaded.

### 2.4 Revision 11 — Identity constraints

| Constraint | Declared on | Scope / rule |
|---|---|---|
| `key_informationUnitId` | top-level `er` | `.//idm:informationUnit`: ids are **unique across the whole ER tree** (nested `subInformationUnit`s and all sub-ERs) |
| `keyref_associatedInformationUnitRef` | top-level `er` | `.//idm:constraint/idm:associatedInformationUnit/@ref`: a constraint anywhere in the tree may reference any information unit in it |
| `key_constraint`, `key_subErConstraint` | each ER | constraint ids are unique **per ER** |
| `key_subErGuid` | each sub-ER | one `specId` guid per ER |
| `keyref_associatedBusinessRuleRef` | `idm` | `associatedBusinessRule/@ref` must point to `uc/businessRule/@id`; checked for the top-level ER and sub-ERs up to 5 levels deep |

**Structural change:** `er` now has the named type `idm:erType`. Sub-ERs use a local `er` declaration of the same type, so the information-unit key is declared only once, on the top-level `er`. Declaring it on every nested `er` made libxml2 (`xmllint`) report false "ambiguous match" errors.

**Removed:** `keyref_associatedInformationUnit`, `keyref_associatedBusinessRule` (the attribute-based versions).

### 2.5 Revision 12 — Business rule statement (breaking)

The `proposition` wrapper only contained `description` (1..\*), whose text had to go into the `title` attribute. It is replaced by:

```
businessRule (id, name)
├── statement      1..1   the rule in natural language (non-empty text; translations are out of scope)
├── images         0..1   graphical examples (plural group element, naming convention c)
│   └── image      1..*
├── description    0..*   commentary on the rule (scope, exceptions, interpretation)
└── reference      0..*   sources, e.g. a legal clause
```

- `statement` uses `idm:nonEmptyText`. This is the Rev 10 `idm:synonymText`, renamed and now shared with `synonym`; instance documents are not affected.
- The informal rule lives in the UC (`statement`). Formal versions live in the ER (`constraint/expression`, Rev 11).

```xml
<!-- Before (Rev 11) -->
<businessRule id="BR-07" name="Fire resistance of load-bearing walls">
  <proposition>
    <description title="Load-bearing walls in buildings over 12 storeys shall have a fire resistance of at least 2 hours."/>
  </proposition>
  <reference>Building Act Enforcement Decree, Art. 56(1)</reference>
</businessRule>
```

**Migration (importer):**

- The first `proposition/description/@title` becomes the `statement` text.
- Any further descriptions become `description` elements.
- Images move into `images/image`.
- If several statements in different languages exist, the English one is kept.

`samples/IDM/businessRule/r12/WindowCostIDM_BusinessRules_r12.xml` is the Rev 12 conversion of `samples/WindowCostIDM_BusinessRules.xml`.

**JSON form** (illustrative; the standard does not define a JSON binding):

```json
{
  "id": "BR-07",
  "name": "Fire resistance of load-bearing walls",
  "statement": "Load-bearing walls in buildings over 12 storeys shall have a fire resistance of at least 2 hours.",
  "images": [ { "caption": "Section of a fire-rated load-bearing wall", "filePath": "images/BR-07_wall_section.png" } ],
  "description": [ { "title": "Commentary: applies to walls that carry vertical loads, including shear walls." } ],
  "reference": [ "Building Act Enforcement Decree, Art. 56(1)" ]
}
```

**Samples:** `samples/IDM/businessRule/r12/` contains:

- `BR_minimal_r12.xml`: the smallest valid business rule.
- `BR_full_r12.xml`: all elements, linked from constraints with RuleML, LegalRuleML, SPARQL and SHACL expressions.
- `WindowCostIDM_BusinessRules_r12.xml`: the converted window-cost sample.
- `invalid/`: eight one-defect files that the schema must reject.

All were checked with three validators against both schema versions. They are regenerated with `tests/make_br_samples.py`.

---

## 3. Validation and tests

**Schema validity:**

- Both versions are valid XSD 1.0. Every schema file was checked against the W3C schema for XSD files.
- They compile without errors in libxml2, Xerces (JDK) and Python `xmlschema` (strict mode).
- Monolithic and modularized are identical: the same 22 global components, the same 26 identity constraints and the same content models.

**Test suite:** `tests/run_tests.py`

- **Coverage:** 86 expectation cases (including the business-rule sample files) plus the other v2 sample files, each run against both schema versions with all three validators. A case passes only if all validators agree with the expected result.
- **Groups:** sample regression, constraint links and scoping, `expression`/`formalRuleLanguage`, synonyms, sub-IDM scoping, and business-rule statements (Rev 12).
- **Result:** 0 failures, 0 disagreements.
- **Known validator deviations** (reported, not counted as failures):
  - libxml2 reports an ambiguous match when a sub-IDM reuses a business-rule id of the outer IDM. This predates Rev 11.
  - Python `xmlschema` flags duplicate synonyms that have no `xml:lang`; XSD 1.0 excludes such rows from `xs:unique`.

**Effect on existing files:** `idmPhase319Phasenabnahme_export.xml` is now invalid. The app's generator (`src/utils/idmXmlGenerator.js`) writes `id="iu-placeholder"` into every empty leaf ER, and these ids now clash across the ER tree. With unique placeholder ids the file validates.

---

## 4. Changes to ISO 29481-3 (tracked changes, author "Claude")

| Clause | Change |
|---|---|
| 4 (overall structure, versioning note) | `xml.xsd` is imported by both schema versions and distributed with them |
| 10.1 General (ER) | Information-unit ids unique across the ER hierarchy; constraint ids unique per ER |
| 10.2.1 Information unit | `synonym` added to the element list, with a paragraph on preferred term, `xml:lang` and no duplicates per language |
| Table 41 | New `synonym` row; `description` restriction corrected from 0:1 to 0:\* |
| 10.3 Constraint | Paragraph rewritten (logical restriction; `ref`-based links; informal and formal statements) |
| Table 44 | `associatedInformationUnit` and `associatedBusinessRule` changed from string attributes to elements (0:\*) with `ref`; new `expression` row |
| **New 10.3.1 Expression** + Table 45 | Three content forms; several expressions per constraint; no IDM-namespace elements inside |
| **New 10.3.2 Formal rule language** + Table 46 | `name` (required), `version`, `publicationYear` (gYear), `uri` |
| 8.9 Business rule | Sentence linking business rules to constraints; composition changed to id, name, statement, optional images, optional descriptions (commentary) and references (Rev 12) |
| Table 19 | `proposition` (1:1) changed to `statement` (1:1); new `images` (0:1) and `description` (0:\*) rows |
| Table 20 | Now "The images’ element": `image` (1:\*), replacing the proposition’s `description` |
| Tables / 8.5 text | Element names aligned with the schema: `standardProjectPhase` → `standardProjectStage`, `localProjectPhase` → `localProjectStage`, `imagFilePath` → `imageFilePath`, `asscoiatedER` → `associatedEr` |
| Figures 1–8 | Replaced by editable SVGs (real text, PNG fallback). Figures 2–7 are generated from the schema and reflect Rev 1–12; Figure 1 (UML) is redrawn; Figure 8 (IDM code) is redrawn with unchanged content |

After opening the document, update all fields (select all, then F9). The new Tables 45–46 renumber the following tables and the cross-references.

---

## 5. Examples

The XML below validates against idmXSD v2.0 (Rev 12). In real files, prefix the elements with `idm:` or set the IDM namespace as default (`https://standards.iso.org/iso/29481/-3/ed-2/en`).

### 5.1 Business rule in the use case (Rev 12)

```xml
<businessRule id="BR-07" name="Fire resistance of load-bearing walls">
  <statement>Load-bearing walls in buildings over 12 storeys shall have a fire resistance of at least 2 hours.</statement>
  <images>
    <image caption="Section of a fire-rated load-bearing wall" filePath="images/BR-07_wall_section.png"/>
    <image caption="Building over 12 storeys with load-bearing walls highlighted" filePath="images/BR-07_building.png"/>
  </images>
  <description title="Commentary: applies to walls that carry vertical loads, including shear walls. Non-load-bearing partitions are covered by BR-08."/>
  <description title="Commentary: the number of storeys is counted above ground level."/>
  <reference>Building Act Enforcement Decree, Art. 56(1) (illustrative)</reference>
  <reference>EN 13501-2 (classification of fire resistance)</reference>
</businessRule>
```

The minimal form is a single `<statement>` (see `BR_minimal_r12.xml`).

### 5.2 Information unit with multilingual synonyms

```xml
<informationUnit id="IU-012" name="Fire rating" dataType="IfcLabel" isMandatory="true"
                 definition="Fire resistance rating of the element, expressed as the period it maintains load-bearing capacity, integrity and insulation under standard fire test conditions.">
  <!-- English (incl. abbreviation and regional variants) -->
  <synonym xml:lang="en">Fire resistance rating</synonym>
  <synonym xml:lang="en">FRR</synonym>
  <synonym xml:lang="en-US">Hourly rating</synonym>
  <synonym xml:lang="en-GB">Period of fire resistance</synonym>
  <!-- Other languages -->
  <synonym xml:lang="ko">내화등급</synonym>
  <synonym xml:lang="ko">내화성능</synonym>
  <synonym xml:lang="ja">耐火性能</synonym>
  <synonym xml:lang="zh-CN">耐火等级</synonym>
  <synonym xml:lang="de">Feuerwiderstandsklasse</synonym>
  <synonym xml:lang="fr">Résistance au feu</synonym>
  <correspondingExternalElement basis="IFC4.3" name="Pset_WallCommon.FireRating"/>
</informationUnit>
```

The non-English terms are illustrative and should be reviewed by native-speaking domain experts before being used as reference data. Some differ slightly in meaning: 내화등급 is a rating class, while 내화시간 would be a duration.

### 5.3 Constraint with informal and formal expressions

```xml
<constraint id="C-07a">
  <associatedBusinessRule ref="BR-07"/>
  <associatedInformationUnit ref="IU-012"/>   <!-- Fire rating -->
  <associatedInformationUnit ref="IU-003"/>   <!-- Is load-bearing -->
  <associatedInformationUnit ref="IU-021"/>   <!-- Number of storeys -->

  <!-- Informal -->
  <description title="IU-012 &gt;= 2h WHERE IU-003 = true AND IU-021 &gt; 12"/>

  <!-- Formal 1: RuleML (embedded XML) -->
  <expression id="C-07a-ruleml">
    <formalRuleLanguage name="RuleML" version="1.03" uri="http://ruleml.org/spec"/>
    <Implies xmlns="http://ruleml.org/spec">
      <if>
        <And>
          <Atom><Rel>isLoadBearing</Rel><Var>wall</Var><Data>true</Data></Atom>
          <Atom><Rel>numberOfStoreys</Rel><Var>bldg</Var><Var>n</Var></Atom>
          <Atom><Rel>greaterThan</Rel><Var>n</Var><Data>12</Data></Atom>
        </And>
      </if>
      <then>
        <Atom><Rel>fireRatingAtLeast</Rel><Var>wall</Var><Data>PT2H</Data></Atom>
      </then>
    </Implies>
  </expression>

  <!-- Formal 2: LegalRuleML (normative statement; embedded XML) -->
  <expression id="C-07a-lrml">
    <formalRuleLanguage name="LegalRuleML" version="1.0" publicationYear="2021"
                        uri="http://docs.oasis-open.org/legalruleml/ns/v1.0/"/>
    <lrml:LegalRuleML xmlns:lrml="http://docs.oasis-open.org/legalruleml/ns/v1.0/"
                      xmlns:ruleml="http://ruleml.org/spec">
      <lrml:Statements key="stmts-br07">
        <lrml:PrescriptiveStatement key="ps-br07">
          <ruleml:Rule closure="universal">
            <!-- conditions as in the RuleML expression; conclusion wrapped in lrml:Obligation -->
          </ruleml:Rule>
        </lrml:PrescriptiveStatement>
      </lrml:Statements>
    </lrml:LegalRuleML>
  </expression>

  <!-- Formal 3: SPARQL (text in CDATA) -->
  <expression id="C-07a-sparql">
    <formalRuleLanguage name="SPARQL" version="1.1" publicationYear="2013"/>
    <![CDATA[
      ASK { ?w :isLoadBearing true ; :fireRating ?r ; :inBuilding ?b .
            ?b :numberOfStoreys ?n .
            FILTER (?n > 12 && ?r < "PT2H"^^xsd:duration) }   # true = violation
    ]]>
  </expression>

  <!-- Formal 4: SHACL in an external file -->
  <expression id="C-07a-shacl" uri="rules/BR-07.shacl.ttl">
    <formalRuleLanguage name="SHACL" publicationYear="2017" uri="http://www.w3.org/ns/shacl#"/>
  </expression>
</constraint>
```

The RuleML and LegalRuleML markup shows the structure only and has not been validated against the RuleML or LegalRuleML schemas. Validate it against those schemas before using it as reference data.

### 5.4 Invalid cases (rejected by the schema)

| Case | Why |
|---|---|
| `<constraint id="C" associatedBusinessRule="BR-07"/>` | Attribute form removed in Rev 11 |
| `<associatedInformationUnit ref="IU-999"/>` | No information unit with that id in the ER tree |
| `<associatedBusinessRule ref="BR-99"/>` | No business rule with that id in the use case |
| `<expression>…</expression>` without `formalRuleLanguage` | `formalRuleLanguage` is required and must come first |
| `<formalRuleLanguage version="1.0"/>` | `name` is required |
| `publicationYear="21"` or `"2021-08-30"` | Must be an `xs:gYear` (e.g. `2021`) |
| `<description>` inside `expression` | IDM-namespace elements are not allowed in rule content |
| Two `<synonym xml:lang="en">FRR</synonym>` | Duplicate synonym within one language |
| `<synonym xml:lang="english language">` | Invalid language tag |
| Same information-unit id in the top ER and a sub-ER | Ids must be unique across the ER tree |
| `<businessRule …><proposition>…</proposition></businessRule>` | `proposition` removed in Rev 12; use `statement` |
| `businessRule` without `statement`, two `statement`s, or `xml:lang` on `statement` | Exactly one statement; translations are out of scope |
| `<images/>` (empty) or `image` directly under `businessRule` | `images` needs at least one `image`; images go inside `images` |

---

## 6. Open issues (flagged as comments in the document, not changed)

1. **`description` cannot hold text:** it has only a `title` attribute and `image` children and is not mixed. Business rules no longer depend on it (Rev 12), but other elements still do.
2. **`businessRule/reference` is untyped:** it has no link to `uc/reference`. Consider a `fullCitation` keyref plus a `clause` attribute for legal sources.
3. **Table 19 contradicts itself:** it calls the business-rule `name` both "required, unique" and "not unique". The schema enforces uniqueness.
4. **Deep sub-ERs are not fully checked:** business-rule references in sub-ERs deeper than 5 levels, and duplicate synonyms without `xml:lang`, need application-level checks.
5. **Possible typo in Figure 8:** the example code reads `CostEstimatipmforPC`, probably meant as `CostEstimationforPC`.
6. **Missing list of changes in the Foreword:** ISO normally expects a list of main changes from the first edition in a second edition.

## 7. Next steps (app)

1. **Generator:** make the `iu-placeholder` ids unique per ER.
2. **Importer:** map the old `constraint` attributes to the new elements, and `proposition/description/@title` to `statement`.
3. **Generator and parser:** read and write `synonym`, `statement`, `images`, `associatedBusinessRule`, `associatedInformationUnit`, `expression` and `formalRuleLanguage`.
4. **Editor UI:** support synonyms with language tags, business-rule statements, images and commentary, and linking business rules, constraints and information units, with rule-language expressions.
