# idmXML

This repository provides **idmXSD** (the XML Schema Definition for IDM data schema) as defined by **ISO 29481-3** (*Building information models - Information delivery manual - Part 3: Data schema*).

## Branches

| Branch | Contents | Link |
|--------|----------|------|
| **main** (this branch) | Original idmXSD as published with ISO/FDIS 29481-3 V2.0 (August 2022) | [Browse](https://github.com/ghanglee/idmXML/tree/main) |
| **Ver2.0** | Revised idmXSD with 9 revisions (see [REVISION_HISTORY.md](https://github.com/ghanglee/idmXML/blob/Ver2.0/REVISION_HISTORY.md)) | [Browse](https://github.com/ghanglee/idmXML/tree/Ver2.0) |

- **main** — The baseline schema as-is from the ISO standard. Use this as the reference for the current official schema.
- **Ver2.0** — The revised schema with enhancements and bug fixes applied to the baseline.

## Repository Structure (main branch)

```
idmXML/
├── IDM Schema/
│   ├── Class Diagram/              # UML class diagrams
│   └── idmXSD_20220822/            # Original modularized XSD files
│       ├── idm.xsd
│       ├── specId.xsd
│       ├── authoring.xsd
│       ├── uc.xsd
│       ├── businessContextMap.xsd
│       └── er.xsd
├── TestCases/                      # Example idmXML files
│   ├── Basic IDM_20210311/
│   ├── Bridge Data Handover/
│   └── idm_DesignAuthoring/
├── xPPM-neo                        # Link to IDM authoring tool
└── README.md
```

## Schema Version (Baseline)

- **idmXSD Version:** Original (as published August 2022)
- **Namespace:** `https://standards.buildingsmart.org/IDM/idmXML/0.2`
- **Base Standard:** ISO 29481-3

## Related Standards

| Standard | Title |
|----------|-------|
| **ISO 29481-1** | IDM - Methodology and format |
| **ISO 29481-3** | IDM - Data schema (idmXML) |
| **ISO/IEC 19510** | BPMN 2.0 representation |
| **ISO 16739-1** | Industry Foundation Classes (IFC) |

## License

This work is licensed under [CC BY 4.0](LICENSE).
