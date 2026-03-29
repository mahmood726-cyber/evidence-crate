Mahmood Ahmad
Tahir Heart Institute
author@example.com

Protocol: EvidenceCrate - Static Metadata Packaging Audit

This protocol describes a snapshot-first packaging study built on the bundled `data-source/portfolio-data.snapshot.json` copied from `ResearchConstellation`. Eligible records are all 134 indexed project rows preserved in that snapshot across 12 portfolio tiers. The primary estimand is explicit lifecycle coverage in packaged entities, defined as the proportion of project records that can be exported with an explicit lifecycle label instead of a generic needs-triage placeholder. Secondary outputs will count crate graph nodes, tier collections, project entities, status-incomplete entities, and cleanly exportable tiers. The build process will emit `data.json`, `data.js`, `ro-crate-metadata.json`, `codemeta.json`, and a static dashboard for browser review. Project and tier entities will be generated deterministically from the bundled source so the repository remains rebuildable without access to the parent atlas or the live C drive index. Anticipated limitations include upstream status ambiguity, incomplete folder inspection, the absence of profile-level RO-Crate validation, and no automatic correction of mislabeled source rows.

Outside Notes

Type: protocol
Primary estimand: explicit lifecycle coverage in packaged entities
App: EvidenceCrate v0.1
Code: repository root, scripts/build_evidence_crate.py, data-source/portfolio-data.snapshot.json, ro-crate-metadata.json, and codemeta.json
Date: 2026-03-29
Validation: DRAFT

References

1. RO-Crate Specification 1.1. Research Object Crate contributors; 2024.
2. The CodeMeta Project. Software metadata crosswalk and terms; accessed 2026.
3. Wilkinson MD, Dumontier M, Aalbersberg IJJ, et al. The FAIR Guiding Principles for scientific data management and stewardship. Sci Data. 2016;3:160018.

AI Disclosure

This protocol was drafted from versioned local artifacts and deterministic build logic. AI was used as a drafting and implementation assistant under author supervision, with the author retaining responsibility for scope, methods, and reporting choices.
