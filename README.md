# idmXML

This repository provides **idmXSD**, the XML Schema Definition of the IDM data schema defined by **ISO 29481-3** (*Building information models — Information delivery manual — Part 3: Data schema*).

## Branches

| Branch | Contents | Link |
|--------|----------|------|
| **[main](https://github.com/ghanglee/idmXML/tree/main)** | Original idmXSD as published with ISO/FDIS 29481-3 V2.0 (August 2022) | [Browse](https://github.com/ghanglee/idmXML/tree/main) |
| **Ver2.0** (this branch) | Revised idmXSD with 13 revisions (see REVISION_HISTORY.md) | [Browse](https://github.com/ghanglee/idmXML/tree/Ver2.0) |

- **main** — The baseline schema as-is from the ISO standard. Use this as the reference for the current official schema.
- **Ver2.0** — The revised schema with enhancements and bug fixes. See [REVISION_HISTORY.md](https://github.com/ghanglee/idmXML/blob/Ver2.0/REVISION_HISTORY.md) for the full list of changes and rationale.

## Ver2.0 Repository Structure

```
idmXML/
├── Class Diagram/                # (empty on Ver2.0; UML diagrams on main — see Figures/)
├── Modularized/                  # Split XSD files (one per IDM component)
│   ├── idm.xsd                   # Root element and cross-element constraints
│   ├── specId.xsd                # Specification identifier
│   ├── authoring.xsd             # Authoring metadata, change log, authors
│   ├── uc.xsd                    # Use case, actors, project stages, business rules
│   ├── businessContextMap.xsd    # BCM, process/interaction/transaction maps
│   ├── er.xsd                    # Exchange requirements, information units, constraints
│   └── xml.xsd                   # Minimal W3C XML-namespace schema (xml:lang), imported by er.xsd
├── Monolithic/
│   ├── idm_monolithic_V2.0.xsd   # Consolidated single-file XSD
│   └── xml.xsd                   # Same xml.xsd, imported by the monolithic schema
├── Figures/                      # Editable SVG figures for ISO 29481-3 (Figures 1–8)
│   └── generator/                # Scripts that regenerate the figures from the schema
├── TestCases/
│   └── businessRule/r12/         # Rev 12 business-rule samples (valid + invalid/)
├── tests/                        # Multi-validator regression test suite
├── docs/
│   └── idmXSD_v2.0_Rev10-12_Summary.md   # Summary of Revisions 10–12 with examples
├── REVISION_HISTORY.md           # Detailed changelog with rationale
├── README.md
└── LICENSE
```

### Modularized

Individual XSD files linked via `xs:include`. The modularized structure allows standalone validation of sub-schemas (e.g., validating an ER export against `er.xsd` alone).

### Monolithic

A consolidated single-file version (`idm_monolithic_V2.0.xsd`) containing all element definitions from the 6 modularized files. Functionally identical to the modularized version.

> **Note:** Since Revision 10 both versions import `xml.xsd` (for `xml:lang` on information-unit synonyms). Keep `xml.xsd` next to the schema files; it is a local copy of the W3C schema for the XML namespace so that validation works offline.

## Schema Version

- **idmXSD Version:** 2.0 (Edition 2)
- **Namespace:** `https://standards.iso.org/iso/29481/-3/ed-2/en`
- **Base Standard:** ISO 29481-3

### Summary of Revisions (Ver2.0)

| Rev | Change | Category |
|-----|--------|----------|
| 1 | Namespace: `buildingsmart.org/0.2` → `iso.org/ed-2` | Alignment |
| 2 | ER non-empty enforcement via `xs:choice` | ISO compliance |
| 3 | Actor: added `subActor`, `actorType` (`actorType` removed in Rev 13) | Enhancement |
| 4 | Added `shapeAndActor` to Process Map | Enhancement |
| 5 | Association elements use `ref` attribute; removed global `associatedEr` | Consistency |
| 6 | Embedded content: inline base64 images + inline diagram CDATA | Enhancement |
| 7 | `description` child in `informationUnit` | Enhancement |
| 8 | Fixed 5 identity constraint bugs | Bug fix |
| 9 | Added `targetNamespace`, `elementFormDefault`, `idm:` prefixes | Namespace fix |
| 10 | `informationUnit/synonym` with `xml:lang` (multilingual alternative names) | Enhancement |
| 11 | `constraint` links become repeatable `associatedBusinessRule` / `associatedInformationUnit` elements with `ref`; new `expression` + `formalRuleLanguage` for formal rules (RuleML, LegalRuleML, SPARQL, SHACL, …); information-unit IDs unique across the ER tree | Enhancement (breaking) |
| 12 | `businessRule`: `statement` (the rule in natural language), optional `images` and `description` (commentary) replace `proposition` | Enhancement (breaking) |
| 13 | `standardProjectStage`/`localProjectStage` → `standardProjectPhase`/`localProjectPhase` (ISO 29481-1:2025 "project phase"); `actor/@actorType` removed, optional `actor/@external` marks an external actor role | Alignment (breaking) |

Revisions 11–13 change element structure: idmXML files using the earlier `constraint` attributes, `businessRule/proposition`, `…ProjectStage` or `actorType` need conversion (see the *Migration* notes in REVISION_HISTORY.md).

### Example (Rev 11–12): a business rule and the constraint that checks it

```xml
<!-- in uc -->
<businessRule id="BR-07" name="Fire resistance of load-bearing walls">
  <statement>Load-bearing walls in buildings over 12 storeys shall have a fire resistance of at least 2 hours.</statement>
  <images><image caption="Wall section" filePath="images/BR-07.png"/></images>
  <description title="Commentary: storeys are counted above ground level."/>
  <reference>Building Act Enforcement Decree, Art. 56(1) (illustrative)</reference>
</businessRule>

<!-- in er -->
<constraint id="C-07a">
  <associatedBusinessRule ref="BR-07"/>
  <associatedInformationUnit ref="IU-012"/>   <!-- Fire rating -->
  <associatedInformationUnit ref="IU-003"/>   <!-- Is load-bearing -->
  <associatedInformationUnit ref="IU-021"/>   <!-- Number of storeys -->
  <description title="IU-012 &gt;= 2h WHERE IU-003 = true AND IU-021 &gt; 12"/>
  <expression>
    <formalRuleLanguage name="SPARQL" version="1.1" publicationYear="2013"/>
    <![CDATA[ ASK { ?w :isLoadBearing true ; :fireRating ?r ; :inBuilding ?b .
                  ?b :numberOfStoreys ?n . FILTER (?n > 12 && ?r < "PT2H"^^xsd:duration) } ]]>
  </expression>
  <expression uri="rules/BR-07.shacl.ttl">
    <formalRuleLanguage name="SHACL" publicationYear="2017" uri="http://www.w3.org/ns/shacl#"/>
  </expression>
</constraint>
```

More examples: [docs/idmXSD_v2.0_Rev10-12_Summary.md](docs/idmXSD_v2.0_Rev10-12_Summary.md) and [TestCases/businessRule/r12/](TestCases/businessRule/r12/).

## Tests

`tests/run_tests.py` validates every case against **both** the monolithic and the modularized schema with three independent XSD 1.0 validators — libxml2 (`lxml`), Xerces (JDK `javax.xml.validation`, via `tests/Validate.java`) and Python `xmlschema` — and passes only if all of them agree with the expected result. It covers constraint links and scoping, `expression`/`formalRuleLanguage`, synonyms, sub-IDM scoping, business-rule statements, project phases and actor roles, and all files in `TestCases/` (files under an `invalid/` folder must be rejected).

```bash
pip install lxml xmlschema        # Java 11+ on PATH enables the Xerces check
python3 tests/run_tests.py        # last result: tests/last_run.txt
```

Current result: 101 expectation cases × 3 validators × 2 schema versions, 0 failures or disagreements. Two documented validator deviations (libxml2 with sub-IDM key scopes; `xmlschema` with `xs:unique` rows that lack a field) are reported but not counted as failures.

`tests/make_br_samples.py` regenerates the business-rule samples in `TestCases/businessRule/r12/`.

## Figures

`Figures/` holds editable SVG versions (real text, not outlines) of the ISO 29481-3 figures: the UML class diagram (Figure 1), the XSD diagrams of idm, specId, authoring, uc, businessContextMap and er (Figures 2–7, generated from the monolithic schema), and the IDM code (Figure 8). Regenerate with:

```bash
pip install xmlschema pillow cairosvg
python3 Figures/generator/mkfigs.py    # Figures 2–7
python3 Figures/generator/uml.py       # Figure 1
python3 Figures/generator/fig8.py      # Figure 8
```

The generators measure text with Liberation Sans / Carlito fonts (metric-compatible with Arial / Calibri).

## Note on AI assistance

An AI assistant (Claude, Anthropic) was used to help draft and validate Revisions 10–13, the test suite and the samples, and to generate the summary in `docs/` and the figures.

## Related Standards

| Standard | Title |
|----------|-------|
| **ISO 29481-1** | IDM - Methodology and format |
| **ISO 29481-3** | IDM - Data schema (idmXML) |
| **ISO/IEC 19510** | BPMN 2.0 representation |
| **ISO 16739-1** | Industry Foundation Classes (IFC) |

## License

This work is licensed under [CC BY 4.0](LICENSE).
