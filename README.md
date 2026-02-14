# idmXML

This repository provides **idmXSD** (the XML Schema Definition for IDM data schema) as defined by **ISO 29481-3** (*Building information models - Information delivery manual - Part 3: Data schema*).

## Branches

| Branch | Contents | Link |
|--------|----------|------|
| **[main](https://github.com/ghanglee/idmXML/tree/main)** | Original idmXSD as published with ISO/FDIS 29481-3 V2.0 (August 2022) | [Browse](https://github.com/ghanglee/idmXML/tree/main) |
| **[Ver2.0](https://github.com/ghanglee/idmXML/tree/Ver2.0)** | Revised idmXSD with 8 revisions (see REVISION_HISTORY.md) | [Browse](https://github.com/ghanglee/idmXML/tree/Ver2.0) |

- **main** — The baseline schema as-is from the ISO standard. Use this as the reference for the current official schema.
- **Ver2.0** — The revised schema with enhancements and bug fixes. See [REVISION_HISTORY.md](https://github.com/ghanglee/idmXML/blob/Ver2.0/REVISION_HISTORY.md) for the full list of changes and rationale.

## Ver2.0 Repository Structure

```
idmXML/
├── Modularized/                  # Split XSD files (one per IDM component)
│   ├── idm.xsd                   # Root element and cross-element constraints
│   ├── specId.xsd                # Specification identifier
│   ├── authoring.xsd             # Authoring metadata, change log, authors
│   ├── uc.xsd                    # Use case, actors, project stages
│   ├── businessContextMap.xsd    # BCM, process/interaction/transaction maps
│   └── er.xsd                    # Exchange requirements, information units
├── Monolithic/
│   └── idm_monolithic_V2.0.xsd   # Consolidated single-file XSD
├── REVISION_HISTORY.md           # Detailed changelog with rationale
├── README.md
└── LICENSE
```

### Modularized

Individual XSD files linked via `xs:include`. The modularized structure allows standalone validation of sub-schemas (e.g., validating an ER export against `er.xsd` alone).

### Monolithic

A consolidated single-file version (`idm_monolithic_V2.0.xsd`) containing all element definitions from the 6 modularized files. Functionally identical to the modularized version.

## Schema Version

- **idmXSD Version:** 2.0 (Edition 2)
- **Namespace:** `https://standards.iso.org/iso/29481/-3/ed-2/en`
- **Base Standard:** ISO 29481-3

### Summary of Revisions (Ver2.0)

| Rev | Change | Category |
|-----|--------|----------|
| 1 | Namespace: `buildingsmart.org/0.2` → `iso.org/ed-2` | Alignment |
| 2 | ER non-empty enforcement via `xs:choice` | ISO compliance |
| 3 | Actor: added `subActor`, `actorType` | Enhancement |
| 4 | Added `shapeAndActor` to Process Map | Enhancement |
| 5 | Association elements use `ref` attribute; removed global `associatedEr` | Consistency |
| 6 | Embedded content: inline base64 images + inline diagram CDATA | Enhancement |
| 7 | `description` child in `informationUnit` | Enhancement |
| 8 | Fixed 5 identity constraint bugs | Bug fix |

## Related Standards

| Standard | Title |
|----------|-------|
| **ISO 29481-1** | IDM - Methodology and format |
| **ISO 29481-3** | IDM - Data schema (idmXML) |
| **ISO/IEC 19510** | BPMN 2.0 representation |
| **ISO 16739-1** | Industry Foundation Classes (IFC) |

## License

This work is licensed under [CC BY 4.0](LICENSE).
