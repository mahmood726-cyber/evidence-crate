from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = PROJECT_ROOT / "data-source" / "portfolio-data.snapshot.json"
DATA_JSON = PROJECT_ROOT / "data.json"
DATA_JS = PROJECT_ROOT / "data.js"
RO_CRATE_JSON = PROJECT_ROOT / "ro-crate-metadata.json"
CODEMETA_JSON = PROJECT_ROOT / "codemeta.json"


def slugify(value: str) -> str:
    return re.sub(r"(^-|-$)", "", re.sub(r"[^a-z0-9]+", "-", value.lower()))


def load_portfolio(source_path: Path) -> dict[str, object]:
    return json.loads(source_path.read_text(encoding="utf-8"))


def build_status_breakdown(status_order: list[dict[str, str]], counts: dict[str, int]) -> list[dict[str, object]]:
    return [
        {
            "key": item["key"],
            "label": item["label"],
            "count": counts.get(item["key"], 0),
        }
        for item in status_order
        if counts.get(item["key"], 0)
    ]


def build_tier_breakdown(tiers: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "key": tier["key"],
            "name": tier["shortName"],
            "fullName": tier["name"],
            "count": tier["count"],
            "coveragePercent": float(str(tier["opportunity"]).split("%", 1)[0]),
            "needsTriage": int(tier["statusCounts"].get("needs-triage", 0)),
            "statusSummary": tier["statusSummary"],
        }
        for tier in tiers
    ]


def build_type_breakdown(portfolio: list[dict[str, object]]) -> list[dict[str, object]]:
    counts = Counter(project["type"] for project in portfolio)
    return [
        {"type": project_type, "count": count}
        for project_type, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def build_ro_crate(payload: dict[str, object]) -> dict[str, object]:
    portfolio = payload["portfolio"]
    tiers = payload["tiers"]
    overview = payload["overview"]
    today = date.today().isoformat()
    graph: list[dict[str, object]] = [
        {
            "@id": "ro-crate-metadata.json",
            "@type": "CreativeWork",
            "about": {"@id": "./"},
            "conformsTo": {"@id": "https://w3id.org/ro/crate/1.1"},
            "name": "EvidenceCrate metadata",
        },
        {
            "@id": "./",
            "@type": "Dataset",
            "name": "EvidenceCrate",
            "description": (
                "A repo-local packaging layer that repackages the ResearchConstellation "
                "portfolio snapshot into RO-Crate style metadata, summary JSON, and a static dashboard."
            ),
            "license": "https://creativecommons.org/licenses/by/4.0/",
            "datePublished": today,
            "dateModified": today,
            "creator": {"@id": "#author"},
            "hasPart": [],
        },
        {
            "@id": "#author",
            "@type": "Person",
            "name": "Mahmood Ahmad",
        },
        {
            "@id": "#builder",
            "@type": ["SoftwareApplication", "CreativeWork"],
            "name": "build_evidence_crate.py",
            "programmingLanguage": "Python",
            "creator": {"@id": "#author"},
        },
    ]

    file_entities = [
        ("data-source/portfolio-data.snapshot.json", "File", "Bundled ResearchConstellation portfolio snapshot", "application/json"),
        ("scripts/build_evidence_crate.py", "SoftwareSourceCode", "EvidenceCrate builder", "text/x-python"),
        ("data.json", "File", "Derived dashboard data", "application/json"),
        ("index.html", "File", "Static dashboard", "text/html"),
        ("e156-submission/index.html", "File", "E156 reader", "text/html"),
        ("codemeta.json", "File", "CodeMeta description", "application/json"),
    ]
    for path, entity_type, name, media_type in file_entities:
        graph.append(
            {
                "@id": path,
                "@type": entity_type,
                "name": name,
                "encodingFormat": media_type,
            }
        )

    tier_ids: list[dict[str, str]] = []
    project_ids: list[dict[str, str]] = []
    for tier in tiers:
        tier_id = {"@id": f"#tier-{tier['key']}"}
        tier_ids.append(tier_id)
        graph.append(
            {
                "@id": tier_id["@id"],
                "@type": "Collection",
                "name": tier["name"],
                "description": tier["summary"],
                "size": tier["count"],
                "keywords": [tier["shortName"], "portfolio tier"],
            }
        )

    for project in portfolio:
        entity_id = f"#project-{slugify(project['id'] + '-' + project['name'])}"
        project_ids.append({"@id": entity_id})
        graph.append(
            {
                "@id": entity_id,
                "@type": ["SoftwareSourceCode", "CreativeWork"],
                "name": project["name"],
                "identifier": project["path"],
                "description": project["detail"],
                "additionalType": project["type"],
                "creativeWorkStatus": project["statusLabel"],
                "isPartOf": {"@id": f"#tier-{project['tierKey']}"},
                "keywords": [project["tierShortName"], project["type"], project["statusLabel"]],
            }
        )

    graph[1]["hasPart"] = [item for item in file_entities for _ in ()]
    graph[1]["hasPart"] = [{"@id": path} for path, *_rest in file_entities] + tier_ids + project_ids
    graph[1]["variableMeasured"] = [
        "trackedProjects",
        "tierCount",
        "statusLabeled",
        "needsTriage",
        "explicitCoveragePercent",
    ]
    graph[1]["measurementTechnique"] = (
        f"Snapshot-first packaging from {overview['sourcePath']} into RO-Crate style metadata."
    )

    return {
        "@context": "https://w3id.org/ro/crate/1.1/context",
        "@graph": graph,
    }


def build_codemeta(data: dict[str, object]) -> dict[str, object]:
    metrics = data["metrics"]
    return {
        "@context": "https://doi.org/10.5063/schema/codemeta-2.0",
        "@type": "SoftwareSourceCode",
        "name": "EvidenceCrate",
        "description": (
            "Static packaging project that transforms a bundled ResearchConstellation snapshot "
            "into RO-Crate style metadata, a CodeMeta record, and a browser dashboard."
        ),
        "author": {
            "@type": "Person",
            "givenName": "Mahmood",
            "familyName": "Ahmad",
        },
        "dateCreated": date.today().isoformat(),
        "programmingLanguage": ["Python", "HTML", "CSS", "JavaScript"],
        "applicationCategory": "Research",
        "keywords": [
            "RO-Crate",
            "CodeMeta",
            "portfolio metadata",
            "evidence synthesis",
            "GitHub Pages",
        ],
        "softwareRequirements": [
            "Python 3.11+",
            "Static browser host",
        ],
        "developmentStatus": "active",
        "version": "0.1.0",
        "runtimePlatform": "Any browser for dashboard; Python for rebuilds",
        "readme": "README.md",
        "identifier": f"tracked-projects:{metrics['trackedProjects']}",
    }


def build_dashboard_data(payload: dict[str, object], ro_crate: dict[str, object]) -> dict[str, object]:
    portfolio = payload["portfolio"]
    overview = payload["overview"]
    tier_breakdown = build_tier_breakdown(payload["tiers"])
    status_breakdown = build_status_breakdown(payload["statusOrder"], overview["statusCounts"])
    type_breakdown = build_type_breakdown(portfolio)
    explicit_projects = [project for project in portfolio if project["statusExplicit"]]
    triage_projects = [project for project in portfolio if not project["statusExplicit"]]
    crate_graph_size = len(ro_crate["@graph"])

    return {
        "project": {
            "name": "EvidenceCrate",
            "version": "0.1.0",
            "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "sourcePath": payload["overview"]["sourcePath"],
            "sourceProject": "ResearchConstellation",
            "designBasis": [
                "RO-Crate style root dataset and file graph",
                "CodeMeta software description",
                "Static GitHub Pages dashboard",
            ],
        },
        "metrics": {
            "trackedProjects": overview["trackedProjects"],
            "tierCount": overview["tierCount"],
            "explicitStatusCount": overview["statusLabeled"],
            "needsTriage": overview["needsTriage"],
            "explicitCoveragePercent": overview["explicitCoveragePercent"],
            "crateGraphNodes": crate_graph_size,
            "crateCollections": len(payload["tiers"]),
            "crateProjectEntities": len(portfolio),
            "crateFileEntities": 6,
            "crateContextualEntities": crate_graph_size - len(portfolio) - len(payload["tiers"]) - 6,
        },
        "statusBreakdown": status_breakdown,
        "typeBreakdown": type_breakdown,
        "tierBreakdown": tier_breakdown,
        "highlights": {
            "bestCoveredTiers": sorted(tier_breakdown, key=lambda item: (-item["coveragePercent"], item["name"]))[:4],
            "weakestCoveredTiers": sorted(tier_breakdown, key=lambda item: (item["coveragePercent"], -item["needsTriage"], item["name"]))[:4],
            "triageQueue": [
                {
                    "name": project["name"],
                    "tier": project["tierShortName"],
                    "type": project["type"],
                    "path": project["path"],
                }
                for project in triage_projects[:12]
            ],
            "readySet": [
                {
                    "name": project["name"],
                    "tier": project["tierShortName"],
                    "status": project["statusLabel"],
                    "path": project["path"],
                }
                for project in explicit_projects[:12]
            ],
        },
    }


def write_outputs(data: dict[str, object], ro_crate: dict[str, object], codemeta: dict[str, object]) -> None:
    DATA_JSON.write_text(json.dumps(data, indent=2), encoding="utf-8")
    DATA_JS.write_text("window.EVIDENCE_CRATE_DATA = " + json.dumps(data, indent=2) + ";\n", encoding="utf-8")
    RO_CRATE_JSON.write_text(json.dumps(ro_crate, indent=2), encoding="utf-8")
    CODEMETA_JSON.write_text(json.dumps(codemeta, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build EvidenceCrate artifacts.")
    parser.add_argument(
        "--source",
        help="Optional path to a portfolio-data.json file. Relative paths resolve from the repository root.",
    )
    args = parser.parse_args()

    source_path = Path(args.source) if args.source else DEFAULT_SOURCE
    if not source_path.is_absolute():
        source_path = PROJECT_ROOT / source_path
    if not source_path.exists():
        raise SystemExit(f"Source data not found: {source_path}")

    payload = load_portfolio(source_path)
    ro_crate = build_ro_crate(payload)
    data = build_dashboard_data(payload, ro_crate)
    codemeta = build_codemeta(data)
    write_outputs(data, ro_crate, codemeta)

    metrics = data["metrics"]
    print(
        "Built EvidenceCrate "
        f"({metrics['trackedProjects']} projects, "
        f"{metrics['crateGraphNodes']} graph nodes, "
        f"{metrics['explicitCoveragePercent']}% coverage)."
    )


if __name__ == "__main__":
    main()
