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
| `idm2.0.xsd` | Monolithic (consolidated) version of the above 6 files |

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
**Affected files**: `er.xsd`, `idm2.0.xsd`

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
**Affected files**: `uc.xsd`, `idm2.0.xsd`

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
**Affected files**: `businessContextMap.xsd`, `idm2.0.xsd`

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
**Affected files**: `businessContextMap.xsd`, `uc.xsd`, `er.xsd`, `idm2.0.xsd`

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
**Affected files**: `uc.xsd` (image), `businessContextMap.xsd` (diagram), `idm2.0.xsd`

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
**Affected files**: `er.xsd`, `idm2.0.xsd`

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
**Affected files**: `uc.xsd`, `authoring.xsd`, `er.xsd`, `idm.xsd`, `idm2.0.xsd`

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
