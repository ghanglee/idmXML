# idmXML

This repository provides **idmXSD** (the XML Schema Definition for IDM data schema) as defined by **ISO 29481-3** (*Building information models - Information delivery manual - Part 3: Data schema*).

## Repository Structure

```
idmXML/
├── Modularized/          # Split XSD files (one per IDM component)
│   ├── idm.xsd           # Root element and cross-element constraints
│   ├── specId.xsd        # Specification identifier
│   ├── authoring.xsd     # Authoring metadata, change log, authors
│   ├── uc.xsd            # Use case, actors, project stages
│   ├── businessContextMap.xsd  # BCM, process/interaction/transaction maps
│   └── er.xsd            # Exchange requirements, information units
├── Monolithic/           # Consolidated single-file XSD (planned)
├── README.md
└── LICENSE
```

### Modularized

Individual XSD files that can be used independently or together. The modularized structure allows standalone validation of sub-schemas (e.g., validating an ER export against `er.xsd` alone).

### Monolithic

A consolidated single-file version of the complete idmXSD will be added here after all identified issues in the modularized version are resolved.

## Schema Version

- **idmXSD Version:** 2.0
- **Namespace:** `idmXML/2.0`
- **Base Standard:** ISO 29481-3

### Key Changes from v1.0 to v2.0

| Element | v1.0 | v2.0 |
|---------|------|------|
| Namespace | `idmXML/0.2` | `idmXML/2.0` |
| Project stage | `standardProjectPhase` | `standardProjectStage` |
| Author structure | Flat | Nested `author/person` and `author/organization` |
| Actor-shape mapping | N/A | `shapeAndActor` in `businessContextMap.xsd` |
| Association references | Empty elements | `ref` attribute for ID-based linking |

## Related Standards

| Standard | Title |
|----------|-------|
| **ISO 29481-1** | IDM - Methodology and format |
| **ISO 29481-3** | IDM - Data schema (idmXML) |
| **ISO/IEC 19510** | BPMN 2.0 representation |
| **ISO 16739-1** | Industry Foundation Classes (IFC) |

## License

This work is licensed under [CC BY 4.0](LICENSE).
