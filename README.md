# EvidenceCrate

EvidenceCrate is a new standalone project that turns the `ResearchConstellation` portfolio snapshot into a packaging-first repository.

## Why this exists

The portfolio atlas now shows where the C-drive evidence stack is visible, but it still leaves a metadata gap:

- the portfolio needs a reproducible package format
- project-level records need machine-readable context
- GitHub Pages readers need a human-facing surface without a build chain

EvidenceCrate addresses that gap by bundling the snapshot locally and exporting:

- `data.json` and `data.js` for the dashboard
- `ro-crate-metadata.json` for crate-style metadata
- `codemeta.json` for software description
- an `e156-submission/` bundle for publication-facing review

## Inputs

- `data-source/portfolio-data.snapshot.json` - bundled snapshot copied from `ResearchConstellation`

## Outputs

- `data.json` - derived dashboard payload
- `data.js` - browser-ready payload for file and Pages serving
- `ro-crate-metadata.json` - linked metadata graph
- `codemeta.json` - software metadata record
- `index.html` - static dashboard
- `e156-submission/` - paper, protocol, metadata, and reader page

## Rebuild

Run:

`python C:\Users\user\EvidenceCrate\scripts\build_evidence_crate.py`

For a custom source file:

`python C:\Users\user\EvidenceCrate\scripts\build_evidence_crate.py --source path\to\portfolio-data.json`

## Standards basis

This project is informed by:

- RO-Crate 1.1 for repo-level research packaging
- CodeMeta for software metadata exchange

The implementation is deliberately lightweight and static-host friendly rather than a full validator or registry service.
