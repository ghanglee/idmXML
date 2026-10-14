# idmXSD v2.0 Schema Revision History

**Standard**: ISO 29481-3 Information Delivery Manual — Data schema (idmXML)
**Schema Version**: 2.0
**Baseline**: idmXSD_20220822 (main branch of ghanglee/idmXML)
**Schema Files**: 6 modularized XSD files + 1 monolithic XSD

| File | Scope |
|------|-------|
| `specId.xsd` | Specification identifier and UUID type |
| `authoring.xsd` | Authors, change log, committee, publisher |
| `uc.xsd` | Use case, actors, project stages, classification, description, image |
| `businessContextMap.xsd` | BCM, process map, interaction map, transaction map, diagram |
| `er.xsd` | Exchange requirement, information unit |
| `idm.xsd` | Root IDM element with cross-element constraints |
| `idm_monolithic_V2.0.xsd` | Monolithic (consolidated) version of the above 6 files |
| `xml.xsd` | Minimal W3C XML-namespace schema (`xml:lang`), imported by `er.xsd` / monolithic (Rev. 10) |

---

## Baseline — idmXSD_20220822 (main branch)

**Date**: August 22, 2022

Original modularized schema as uploaded to the `main` branch. Key characteristics:

- **Namespace**: `https://standards.buildingsmart.org/IDM/idmXML/0.2`
- **Terminology**: Already uses `standardProjectStage`/`localProjectStage` (changed from "phase" on 2022-08-22)
- **ER structure**: `informationUnit` as direct required child (`minOccurs="1"`), separate optional `subEr`
- **Actor**: Simple element with `id`, `name` attributes and optional `classification` child
- **Associations**: `associatedDataObject`, `associatedEr`, `associatedMessage` as simple/empty elements (no `ref` attribute); global `<xs:element name="associatedEr"/>` in `er.xsd`
- **Image**: File reference only (`filePath` required)
- **Diagram**: File reference only (`diagramFilePath` required), no inline content
- **Identity constraints**: `key_businessRuleId`/`keyref_associatedBusinessRules` placed inside `uc` element; `keyref_associatedEr` in `er` element

### Known bugs in baseline
1. `uc.xsd` — `unique_standardprojectStageName`: XPath selector is `standardPhase` (wrong element name), field is `@name` (should be child element `name`)
2. `uc.xsd` — `key_businessRuleId`: selector is `busuinessRule` (typo for `businessRule`)
3. `uc.xsd` — `keyref_associatedBusinessRules`: placed inside `uc` but references `./constraint` which is a child of `er`, not `uc` (wrong scope)
4. `er.xsd` — `keyref_associatedEr`: selector `./associatedEr` with field `associatedEr` is a self-referencing tautology (non-functional)
5. `authoring.xsd` — `keyref_member`/`keyref_leader`: selector `./author/committee` should be `./committee` (committee is a direct child of authoring, not of author)
6. `businessContextMap.xsd` — missing `xmlns:idm` namespace declaration (present in all other files)

---

## Revision 1 — Namespace Migration to ISO URL

**Date**: February 13, 2026
**Affected files**: All 6 modularized XSD files + monolithic

### Change
| Before | After |
|--------|-------|
| `xmlns:idm="https://standards.buildingsmart.org/IDM/idmXML/0.2"` | `xmlns:idm="https://standards.iso.org/iso/29481/-3/ed-2/en"` |

### Reason
The buildingSMART namespace URL (`idmXML/0.2`) was a placeholder used during standard development. Migrated to the official ISO namespace URL structure (`standards.iso.org/iso/{standard-number}/{part}/ed-{edition}/{language}`) for alignment with ISO publication conventions.

---

## Revision 2 — ER Non-Empty Enforcement via `xs:choice`

**Date**: February 13, 2026
**Affected files**: `er.xsd`, `idm_monolithic_V2.0.xsd`

### Change
```xml
<!-- Before -->
<xs:element ref="informationUnit" minOccurs="1" maxOccurs="unbounded"/>
<!-- ... other elements ... -->
<xs:element name="subEr" minOccurs="0" maxOccurs="unbounded">
  ...
</xs:element>

<!-- After -->
<xs:choice minOccurs="1" maxOccurs="unbounded">
  <xs:element ref="informationUnit"/>
  <xs:element name="subEr">
    ...
  </xs:element>
</xs:choice>
```

Also reordered ER child elements: `constraint` and `correspondingMvd` now come before the `choice`, grouping metadata before content.

### Reason
Explicit enforcement of ISO 29481-3 Clause 10: "An ER shall not be empty and shall have at least one information unit or a sub-ER." The baseline required at least one `informationUnit`; the revised schema allows an ER with only sub-ERs (no direct IUs), which is valid per the standard.

---

## Revision 3 — Actor Restructuring (subActor + actorType)

**Date**: February 13, 2026
**Affected files**: `uc.xsd`, `idm_monolithic_V2.0.xsd`

### Change
```xml
<!-- Before -->
<xs:element name="actor" minOccurs="0" maxOccurs="unbounded">
  <xs:complexType>
    <xs:sequence>
      <xs:element ref="classification" minOccurs="0" maxOccurs="1"/>
    </xs:sequence>
    <xs:attribute name="id" type="xs:string" use="required"/>
    <xs:attribute name="name" type="xs:string" use="required"/>
  </xs:complexType>
</xs:element>

<!-- After -->
<xs:element name="actor" minOccurs="0" maxOccurs="unbounded">
  <xs:complexType>
    <xs:sequence>
      <xs:element ref="classification" minOccurs="0" maxOccurs="1"/>
      <xs:element name="subActor" minOccurs="0" maxOccurs="unbounded">
        <xs:complexType>
          <xs:sequence>
            <xs:element ref="classification" minOccurs="0" maxOccurs="1"/>
          </xs:sequence>
          <xs:attribute name="id" type="xs:string" use="required"/>
          <xs:attribute name="name" type="xs:string" use="required"/>
        </xs:complexType>
      </xs:element>
    </xs:sequence>
    <xs:attribute name="id" type="xs:string" use="required"/>
    <xs:attribute name="name" type="xs:string" use="required"/>
    <xs:attribute name="actorType" use="optional">  <!-- "group" | "individual" -->
      ...
    </xs:attribute>
  </xs:complexType>
</xs:element>
```

### Reason
BPMN process maps use Pools (participants) containing Lanes (roles/teams). The `actor` element models Pools, and `subActor` models Lanes within those Pools. Both have direct `id`/`name` attributes and optional `classification`. The `actorType` attribute distinguishes organizations (`group`) from individuals (`individual`), supporting ISO 29481-1 actor role semantics.

---

## Revision 4 — Actor-Shape Mapping via `shapeAndActor` in Process Map

**Date**: February 13, 2026
**Affected files**: `businessContextMap.xsd`, `idm_monolithic_V2.0.xsd`

### Change
Added `shapeAndActor` element to `pm` (Process Map):

```xml
<xs:element name="shapeAndActor" minOccurs="0" maxOccurs="unbounded">
  <xs:complexType>
    <xs:sequence>
      <xs:element name="associatedShape" minOccurs="1" maxOccurs="1">
        <xs:complexType>
          <xs:attribute name="ref" type="xs:string" use="required"/>
        </xs:complexType>
      </xs:element>
      <xs:element name="associatedActor" minOccurs="1" maxOccurs="1">
        <xs:complexType>
          <xs:attribute name="ref" type="xs:string" use="required"/>
        </xs:complexType>
      </xs:element>
    </xs:sequence>
    <xs:attribute name="id" type="xs:string" use="required"/>
  </xs:complexType>
</xs:element>
```

### Reason
Follows the same architectural pattern as `dataObjectAndEr` (which maps BPMN Data Objects to ERs). The `shapeAndActor` element maps BPMN Pools/Lanes to actors/subActors defined in the Use Case, keeping all BPMN-to-IDM mappings in the Business Context Map where they belong. This is consistent with ISO 29481-3's BCM concept of mapping diagram elements to IDM semantic elements.

### Example
```xml
<pm>
  <diagram id="PM-1" name="Main Process" notation="BPMN 2.0" .../>
  <dataObjectAndEr id="DOER-1">
    <associatedDataObject ref="DataObject_abc123"/>
    <associatedEr ref="er-uuid-456"/>
  </dataObjectAndEr>
  <shapeAndActor id="SA-1">
    <associatedShape ref="Participant_pool1"/>
    <associatedActor ref="actor-1"/>
  </shapeAndActor>
  <shapeAndActor id="SA-2">
    <associatedShape ref="Lane_lane1"/>
    <associatedActor ref="actor-1-sub-1"/>
  </shapeAndActor>
</pm>
```

---

## Revision 5 — Association Elements Use `ref` Attribute

**Date**: February 13, 2026
**Affected files**: `businessContextMap.xsd`, `uc.xsd`, `er.xsd`, `idm_monolithic_V2.0.xsd`

### Change
All association elements changed from simple/empty elements to complex types with a `ref` attribute:

| Element | Before | After |
|---------|--------|-------|
| `associatedDataObject` | `<associatedDataObject/>` (empty) | `<associatedDataObject ref="DataObject_id"/>` |
| `associatedEr` (in PM) | `<xs:element ref="associatedEr"/>` (global) | Inline complex type with `ref` attribute |
| `associatedEr` (in TM) | `<xs:element ref="associatedEr"/>` (global) | Inline complex type with `ref` attribute |
| `associatedEr` (in UC) | `<xs:element ref="associatedEr"/>` (global) | Inline complex type with `ref` attribute |
| `associatedMessage` | `<associatedMessage/>` (empty) | `<associatedMessage ref="msg_id"/>` |

The global `<xs:element name="associatedEr"/>` in `er.xsd` was removed. Each context now defines its own inline `associatedEr` element.

### Reason
- **Consistency**: All associations now follow the same `ref` attribute pattern
- **Type safety**: `ref` is declared as `xs:string` with `use="required"`, providing explicit XSD-level validation
- **Self-documenting**: Each context defines its own association element rather than sharing a typeless global element
- **Removes broken constraint**: The global `associatedEr` had a non-functional `keyref_associatedEr` (see baseline bug #4); removing it eliminates the broken constraint

---

## Revision 6 — Embedded Content Support (Image + Diagram)

**Date**: February 13, 2026
**Affected files**: `uc.xsd` (image), `businessContextMap.xsd` (diagram), `idm_monolithic_V2.0.xsd`

### Changes

#### 6a. Image element: inline base64 support
```xml
<!-- Before -->
<xs:element name="image">
  <xs:complexType>
    <xs:attribute name="caption" type="xs:string" use="required"/>
    <xs:attribute name="filePath" type="xs:string" use="required"/>
  </xs:complexType>
</xs:element>

<!-- After -->
<xs:element name="image">
  <xs:complexType mixed="true">
    <xs:attribute name="caption" type="xs:string" use="required"/>
    <xs:attribute name="filePath" type="xs:string" use="optional"/>
    <xs:attribute name="mimeType" type="xs:string" use="optional"/>
    <xs:attribute name="encoding" use="optional">  <!-- restricted to "base64" -->
      ...
    </xs:attribute>
  </xs:complexType>
</xs:element>
```

**Reason**: Enables self-contained idmXML files by embedding image data directly as base64 text content. `filePath` is retained as optional for external file references. `mimeType` (e.g., `image/png`) and `encoding` (restricted to `base64`) provide metadata for decoding. `mixed="true"` allows the element to contain both text content and child elements.

#### 6b. Diagram element: inline content support
```xml
<!-- Before -->
<xs:element name="diagram">
  <xs:complexType>
    <xs:sequence>
      <xs:element ref="description" minOccurs="0" maxOccurs="unbounded"/>
    </xs:sequence>
    <xs:attribute name="diagramFilePath" type="xs:string" use="required"/>
    ...
  </xs:complexType>
</xs:element>

<!-- After -->
<xs:element name="diagram">
  <xs:complexType>
    <xs:sequence>
      <xs:element ref="description" minOccurs="0" maxOccurs="unbounded"/>
      <xs:element name="diagramContent" type="xs:string" minOccurs="0" maxOccurs="1"/>
    </xs:sequence>
    <xs:attribute name="diagramFilePath" type="xs:string" use="optional"/>
    ...
  </xs:complexType>
</xs:element>
```

**Reason**: Enables embedding BPMN XML directly within idmXML using a `<diagramContent>` child element (typically with CDATA). `diagramFilePath` changes from required to optional. This produces self-contained idmXML files that don't require accompanying BPMN files.

---

## Revision 7 — Description in Information Unit

**Date**: February 14, 2026
**Affected files**: `er.xsd`, `idm_monolithic_V2.0.xsd`

### Change
Added `<description>` as the first child element of `<informationUnit>`:

```xml
<!-- Before -->
<xs:element name="informationUnit">
  <xs:complexType>
    <xs:sequence>
      <xs:element name="examples" minOccurs="0" maxOccurs="1">
        ...

<!-- After -->
<xs:element name="informationUnit">
  <xs:complexType>
    <xs:sequence>
      <xs:element ref="description" minOccurs="0" maxOccurs="unbounded"/>
      <xs:element name="examples" minOccurs="0" maxOccurs="1">
        ...
```

### Reason
Information Units have a `definition` attribute for text-based definitions. However, some definitions benefit from visual explanations (diagrams, photos, annotated screenshots). The `description` element — which can contain `image` children — provides this capability, following the same pattern used by other elements in the schema (summary, aimAndScope, benefits, limitations).

---

## Revision 8 — Bug Fixes: Identity Constraints

**Date**: February 13, 2026
**Affected files**: `uc.xsd`, `authoring.xsd`, `er.xsd`, `idm.xsd`, `idm_monolithic_V2.0.xsd`

### Changes

#### 8a. Fixed `unique_standardprojectStageName` (uc.xsd)
```xml
<!-- Before (bug: wrong element name and field) -->
<xs:unique name="unique_standardprojectStageName">
  <xs:selector xpath="standardPhase"/>
  <xs:field xpath="@name"/>
</xs:unique>

<!-- After -->
<xs:unique name="unique_standardprojectStageName">
  <xs:selector xpath="standardProjectStage"/>
  <xs:field xpath="name"/>
</xs:unique>
```
**Bug**: Selector `standardPhase` did not match any element. Field `@name` targeted an attribute, but the actual value is a child element `<name>`. Constraint was silently never applied.

#### 8b. Moved business rule constraint from `uc` to `idm` (uc.xsd → idm.xsd)
```xml
<!-- Before (in uc.xsd — wrong scope, typo) -->
<xs:key name="key_businessRuleId">
  <xs:selector xpath="busuinessRule"/>     <!-- typo: "busuiness" -->
  <xs:field xpath="@id"/>
</xs:key>
<xs:keyref name="keyref_associatedBusinessRules" refer="key_businessRuleId">
  <xs:selector xpath="./constraint"/>       <!-- constraint is in er, not uc -->
  <xs:field xpath="@associatedBusinessRule"/>
</xs:keyref>

<!-- After (in idm.xsd — correct scope) -->
<xs:key name="key_businessRuleId">
  <xs:selector xpath="uc/businessRule"/>
  <xs:field xpath="@id"/>
</xs:key>
<xs:keyref name="keyref_associatedBusinessRule" refer="key_businessRuleId">
  <xs:selector xpath="er/constraint"/>
  <xs:field xpath="@associatedBusinessRule"/>
</xs:keyref>
```
**Bug**: Selector had a typo (`busuinessRule`). The keyref referenced `./constraint` inside `uc`, but constraints are children of `er`. Moved to `idm.xsd` where it can properly span the `uc` and `er` subtrees.

> **Superseded by Revision 11:** `keyref_associatedBusinessRule` (on the `@associatedBusinessRule` attribute) was replaced by `keyref_associatedBusinessRuleRef` on `constraint/associatedBusinessRule/@ref`. `key_businessRuleId` is unchanged.

#### 8c. Fixed `keyref_member`/`keyref_leader` selectors (authoring.xsd)
```xml
<!-- Before (bug: wrong selector path) -->
<xs:keyref name="keyref_member" refer="key_authorId">
  <xs:selector xpath="./author/committee"/>   <!-- committee is not under author -->
  <xs:field xpath="member"/>
</xs:keyref>

<!-- After -->
<xs:keyref name="keyref_member" refer="key_authorId">
  <xs:selector xpath="./committee"/>
  <xs:field xpath="member"/>
</xs:keyref>
```
**Bug**: `committee` is a direct child of `authoring`, not a child of `author`. Same fix applied to `keyref_leader`.

#### 8d. Removed broken `keyref_associatedEr` (er.xsd)
```xml
<!-- Before (bug: self-referencing tautology) -->
<xs:keyref name="keyref_associatedEr" refer="key_erGuid">
  <xs:selector xpath="./associatedEr"/>
  <xs:field xpath="associatedEr"/>
</xs:keyref>
```
**Bug**: Field `associatedEr` references itself rather than a meaningful value. The global `associatedEr` element was also removed in Revision 5. Constraint deleted entirely.

#### 8e. Added `xmlns:idm` namespace to `businessContextMap.xsd`
**Bug**: The baseline `businessContextMap.xsd` was the only modularized file missing the `xmlns:idm` namespace declaration. Added for consistency.

---

## Revision 9 — Target Namespace Declaration

**Date**: February 14, 2026
**Affected files**: All 6 modularized XSD files + monolithic

### Change
Added `targetNamespace` and `elementFormDefault="qualified"` to all schema files, and prefixed all `ref`, `type`, and XPath element references with the `idm:` namespace prefix:

```xml
<!-- Before -->
<xs:schema xmlns:idm="https://standards.iso.org/iso/29481/-3/ed-2/en"
    xmlns:xs="http://www.w3.org/2001/XMLSchema">
  ...
  <xs:element ref="specId" .../>
  <xs:attribute name="guid" type="uuid" .../>
  <xs:selector xpath="./specId"/>

<!-- After -->
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:idm="https://standards.iso.org/iso/29481/-3/ed-2/en"
    targetNamespace="https://standards.iso.org/iso/29481/-3/ed-2/en"
    elementFormDefault="qualified">
  ...
  <xs:element ref="idm:specId" .../>
  <xs:attribute name="guid" type="idm:uuid" .../>
  <xs:selector xpath="./idm:specId"/>
```

### Specific changes
- **Header**: Added `targetNamespace` and `elementFormDefault="qualified"` to all 7 XSD files
- **Element references**: All `ref="elementName"` → `ref="idm:elementName"` (e.g., `ref="specId"` → `ref="idm:specId"`)
- **Custom type**: `type="uuid"` → `type="idm:uuid"` in `specId.xsd`
- **XPath selectors**: All element names in `xs:selector` and `xs:field` XPath expressions prefixed with `idm:` (e.g., `xpath="businessRule"` → `xpath="idm:businessRule"`)
- **Attribute references**: `@guid`, `@id`, `@name`, etc. remain unprefixed (attributes are unqualified by default)

### Reason
Without `targetNamespace`, the schema defines elements in **no namespace**. However, the generated idmXML output uses `<idm xmlns="https://standards.iso.org/iso/29481/-3/ed-2/en">`, placing all elements **in the namespace**. This mismatch causes XML validators to report `cvc-elt.1.a: Cannot find the declaration of element 'idm'` because the schema has no declaration for elements in that namespace.

Adding `targetNamespace` ensures the schema declares elements in the same namespace that instance documents use. `elementFormDefault="qualified"` ensures all child elements (not just the root) are namespace-qualified.

---

## Revision 10 — Information Unit Synonyms (Multilingual)

**Date**: October 9, 2026
**Affected files**: `er.xsd`, `idm_monolithic_V2.0.xsd`; new `xml.xsd` in `modularized/` and `monolithic/`

### Change
Added an optional, repeatable `synonym` element to `informationUnit`, carrying alternative names and translations. Each synonym may be tagged with `xml:lang` (BCP 47 language tag). The `name` attribute remains the preferred term.

```xml
<idm:informationUnit id="IU-012" name="Fire rating" dataType="IfcLabel" isMandatory="true" definition="...">
  <idm:synonym xml:lang="en">Fire resistance rating</idm:synonym>
  <idm:synonym xml:lang="en-GB">Period of fire resistance</idm:synonym>
  <idm:synonym xml:lang="ko">내화등급</idm:synonym>
  <idm:synonym xml:lang="ja">耐火性能</idm:synonym>
  <idm:correspondingExternalElement basis="IFC4.3" name="Pset_WallCommon.FireRating"/>
</idm:informationUnit>
```

### Specific changes
- **`informationUnit` sequence**: `description` → **`synonym` (0..*)** → `examples` → `correspondingExternalElement` → `subInformationUnit`
- **`synonym` content**: new simple type `idm:synonymText` (`xs:normalizedString`, `minLength` 1); optional `xml:lang` attribute
- **Identity constraint**: `unique_synonymPerLanguage` on `informationUnit` — no duplicate synonym text within the same language. Synonyms without `xml:lang` are not covered (XSD skips absent fields); the authoring app should check those.
- **`xml:lang` import**: `xs:import` of the XML namespace from a local `xml.xsd` (minimal copy of the W3C schema, `xml:lang` only), so validation works offline. Distribute `xml.xsd` alongside the schema files.

### Reason
ISO 29481-3 gives an information unit a single `name` and `definition` with no language tag, so an IDM cannot record alternative terms or translations. Synonyms are stored as plain strings on the information unit rather than as links between information units, which avoids having to keep symmetric/transitive links consistent and handles translations in the same structure.

### Compatibility
Backward compatible: the element is optional, so existing idmXML files remain valid (checked against `samples/IDM/idmNachtragsmeldung_export.xml` and `samples/IDM/KillianReyer/Roundtrip/WindowCostIDM.xml`). Files that use `synonym` will **not** validate against the published ISO 29481-3 ed. 2 schema; this is an extension pending proposal to the standard.

---

## Revision 11 — Constraint Links, Formal Rule Expressions, ER-Tree Identity

**Date**: October 9, 2026
**Affected files**: `er.xsd`, `idm.xsd`, `idm_monolithic_V2.0.xsd`; new `tests/`

### Changes

**1. `constraint` links (breaking)**
- The single-valued attributes `associatedInformationUnit` and `associatedBusinessRule` are **removed**.
- Replaced by repeatable child elements, each with a required `ref` attribute:
  `associatedBusinessRule` (0..\*) → `associatedInformationUnit` (0..\*) → `description` (0..\*) → `expression` (0..\*).
- Old files are converted by the importer: `@associatedBusinessRule="X"` → `<associatedBusinessRule ref="X"/>`, same for information units.

**2. New global elements `expression` and `formalRuleLanguage`**
- `expression`: one formal statement of a constraint. Required first child `formalRuleLanguage`, then either foreign-namespace XML (`xs:any namespace="##other" processContents="lax"`, e.g. RuleML, LegalRuleML), character data / CDATA (`mixed="true"`, e.g. SPARQL, SHACL), or nothing with `@uri` pointing to an external rule file. Optional `@id`, `@uri`.
- `formalRuleLanguage`: `name` (required), `version`, `publicationYear` (`xs:gYear`), `uri` (`xs:anyURI`) — same pattern as `classification`.

**3. Identity constraints**
- `er` now has a named type `idm:erType`. The global `er` (top-level ER) declares `key_informationUnitId` over `.//idm:informationUnit` and `keyref_associatedInformationUnitRef` over `.//idm:constraint/idm:associatedInformationUnit`: information unit ids are **unique across the whole ER tree**, and a constraint anywhere in the tree may reference any information unit in it (nested `subInformationUnit`s and sub-ERs included).
- Sub-ERs use a local `er` declaration of the same type with `key_subErGuid` and `key_subErConstraint` (constraint ids stay unique per ER). Declaring the information-unit key on every nested `er` made libxml2 report ambiguous matches.
- `idm`: `keyref_associatedBusinessRuleRef` checks `associatedBusinessRule/@ref` for constraints in the top-level ER and in sub-ERs up to 5 levels deep (XSD 1.0 selectors cannot reach arbitrary depth without also entering `subIdm`). Deeper levels are checked by the application.
- Removed: `keyref_associatedInformationUnit`, `keyref_associatedBusinessRule` (attribute-based).

### Impact on existing files
- `idmPhase319Phasenabnahme_export.xml` is now **invalid**: the generator writes `id="iu-placeholder"` in every empty leaf ER, which now collides across the ER tree. Fix in `src/utils/idmXmlGenerator.js` (make placeholder ids unique per ER); with unique ids the file validates.
- Other v2 samples: unchanged results (`WindowCostIDM_Figures.xml` and the legacy `idm-specification.xml` were already invalid for unrelated reasons).

### Tests (`tests/run_tests.py`)
59 expectation cases plus all v2 sample files, each validated against both the monolithic and modularized schema with three independent XSD 1.0 validators: libxml2 (lxml), Xerces (JDK `javax.xml.validation`, `tests/Validate.java`) and `xmlschema` (Python). A case passes only if all validators agree with the expected result. Groups: sample regression, constraint links and scoping, `expression`/`formalRuleLanguage`, synonyms (Rev. 10), sub-IDM scoping. Run: `python3 tests/run_tests.py <repo root>`; last output in `tests/last_run.txt`.

Documented validator deviations (reported, not counted as failures):
- libxml2 reports an ambiguous match when a sub-IDM reuses a business rule id of the outer IDM (pre-existing; Xerces and xmlschema accept, as XSD 1.0 specifies).
- xmlschema (Python) flags duplicate synonyms without `xml:lang`; XSD 1.0 excludes rows with an absent field from `xs:unique`.

---

## Revision 12 — Business Rule Statement (replaces proposition)

**Date**: October 9, 2026
**Affected files**: `uc.xsd`, `er.xsd` (type rename), `idm_monolithic_V2.0.xsd`, `tests/run_tests.py`; samples in `samples/IDM/businessRule/r12/`

### Change
The `proposition` wrapper of `businessRule` (which only contained `description` 1..\*) is replaced by a `statement` (the rule in natural language), optional `images`, and an optional `description` for commentary:

```xml
<!-- Before -->
<businessRule id="BR-07" name="Fire resistance of load-bearing walls">
  <proposition>
    <description title="Load-bearing walls in buildings over 12 storeys shall have a fire resistance of at least 2 hours."/>
  </proposition>
  <reference>Building Act Enforcement Decree, Art. 56(1)</reference>
</businessRule>

<!-- After -->
<businessRule id="BR-07" name="Fire resistance of load-bearing walls">
  <statement>Load-bearing walls in buildings over 12 storeys shall have a fire resistance of at least 2 hours.</statement>
  <images>
    <image caption="Fire-rated wall section" filePath="img/br07.png"/>
  </images>
  <description title="Commentary: applies to walls that carry vertical loads; non-load-bearing partitions are covered by BR-08."/>
  <reference>Building Act Enforcement Decree, Art. 56(1)</reference>
</businessRule>
```

### Specific changes
- **`businessRule` sequence**: `statement` (1..1) → `images` (0..1) → `description` (0..\*) → `reference` (0..\*)
- **`statement`**: non-empty text (`idm:nonEmptyText`); one statement per business rule (translations are out of scope)
- **`images`**: group element (plural per naming convention c) containing `image` (1..\*, global `idm:image`)
- **`description`**: global `idm:description`, used for commentary on the rule (scope, exceptions, interpretation)
- **Type rename**: `idm:synonymText` (Rev. 10) → `idm:nonEmptyText`, now shared by `synonym` and `statement` (no effect on instance documents)

### Reason
"Proposition" was unclear to users, and the wrapper added a nesting level whose only content was `description`, whose text could only go into the `title` attribute. A business rule is now: id, name, statement, optional images, optional commentary, references. The informal rule lives in the UC (`statement`); formal versions live in the ER (`constraint/expression`, Rev. 11).

### Migration
Importers map `proposition/description/@title` → `statement` text (several descriptions: first → statement, the others → `description`), and images under the old description → `images/image`. Example: `samples/WindowCostIDM_BusinessRules.xml` (Rev. 11) and its converted counterpart `samples/IDM/businessRule/r12/WindowCostIDM_BusinessRules_r12.xml`.

### Tests
Group F covers statement, images, description, element order, the removed `proposition` and constraint → business rule links. See `tests/last_run.txt` for counts.

---

## Summary of All Changes

| Rev | Date | Files | Change | Category |
|-----|------|-------|--------|----------|
| — | Aug 2022 | All | Baseline: idmXSD_20220822 | Baseline |
| 1 | Feb 13, 2026 | All | Namespace: `buildingsmart.org/0.2` → `iso.org/ed-2` | Alignment |
| 2 | Feb 13, 2026 | er.xsd | ER non-empty enforcement via `xs:choice` | ISO compliance |
| 3 | Feb 13, 2026 | uc.xsd | Actor: added `subActor`, `actorType` | Enhancement |
| 4 | Feb 13, 2026 | businessContextMap.xsd | Added `shapeAndActor` to Process Map | Enhancement |
| 5 | Feb 13, 2026 | businessContextMap.xsd, uc.xsd, er.xsd | Association elements use `ref` attribute; removed global `associatedEr` | Consistency |
| 6 | Feb 13, 2026 | uc.xsd, businessContextMap.xsd | Embedded content: inline base64 images + inline diagram CDATA | Enhancement |
| 7 | Feb 14, 2026 | er.xsd | `description` child in `informationUnit` | Enhancement |
| 8 | Feb 13, 2026 | uc.xsd, authoring.xsd, er.xsd, idm.xsd | Fixed 5 identity constraint bugs | Bug fix |
| 9 | Feb 14, 2026 | All | Added `targetNamespace`, `elementFormDefault`, `idm:` prefixes | Namespace fix |
| 10 | Oct 9, 2026 | er.xsd, monolithic, xml.xsd (new) | `informationUnit/synonym` with `xml:lang`; `unique_synonymPerLanguage` | Enhancement (extension) |
| 11 | Oct 9, 2026 | er.xsd, idm.xsd, monolithic, tests/ (new) | Constraint link elements (attributes removed); `expression` + `formalRuleLanguage`; ER-tree-wide information-unit identity; `erType`; multi-validator test suite | Enhancement (breaking) |
| 12 | Oct 9, 2026 | uc.xsd, er.xsd, monolithic, tests | `businessRule`: `statement` + optional `images` and `description` replace `proposition`; `synonymText` → `nonEmptyText` | Enhancement (breaking) |
