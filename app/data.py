"""Static teaching content and synthetic data. No real citizen data is used anywhere."""
import random

SERVICES = [
    {"id": "birth-cert", "name": "Birth certificate copy (simulated)"},
    {"id": "address-change", "name": "Address change request (simulated)"},
    {"id": "water-conn", "name": "New water connection (simulated)"},
    {"id": "trade-licence", "name": "Small trade licence (simulated)"},
    {"id": "grievance", "name": "Public grievance (simulated)"},
]

STATUS_STEPS = ["Submitted", "Document check", "Under review", "Approved"]

MODELS = [
    {"id": "waterfall", "name": "Waterfall"},
    {"id": "incremental", "name": "Incremental"},
    {"id": "agile", "name": "Agile"},
]

COMPARISON = [
    {"dimension": "Flexibility to change",
     "waterfall": "Low. Requirements are frozen early; changes are costly and need formal change control.",
     "incremental": "Medium. Each increment can absorb change, but the overall architecture is planned up front.",
     "agile": "High. Change is expected; the backlog is reprioritised every sprint."},
    {"dimension": "Delivery frequency",
     "waterfall": "One main delivery at the end of the project.",
     "incremental": "Several planned releases, each adding a working slice of the system.",
     "agile": "Frequent, short iterations (typically 1-4 weeks) producing a potentially releasable product."},
    {"dimension": "Testing",
     "waterfall": "A dedicated phase after implementation; defects are found late.",
     "incremental": "Each increment is tested, followed by integration testing with earlier increments.",
     "agile": "Continuous: unit tests, automated regression and acceptance tests in every sprint."},
    {"dimension": "Documentation",
     "waterfall": "Extensive, formal, and approved at each phase gate.",
     "incremental": "Moderate; core design documents plus per-increment documentation.",
     "agile": "Lightweight and just-in-time; working software is preferred over comprehensive documents."},
    {"dimension": "Stakeholder involvement",
     "waterfall": "Mostly at the start (requirements) and end (acceptance).",
     "incremental": "At each increment review.",
     "agile": "Continuous collaboration with a product owner and regular sprint reviews."},
    {"dimension": "Risks",
     "waterfall": "Late discovery of misunderstood requirements and integration problems.",
     "incremental": "Architecture or integration issues if early design is weak; scope creep across increments.",
     "agile": "Scope drift, uneven documentation, and difficulty with fixed-price or fixed-scope contracts."},
    {"dimension": "Advantages",
     "waterfall": "Clear structure, easy progress tracking, strong audit trail.",
     "incremental": "Early partial value, easier risk management, simpler testing per slice.",
     "agile": "Fast feedback, adaptability, early and continuous value, good fit with DevSecOps automation."},
    {"dimension": "Limitations",
     "waterfall": "Poor fit for evolving needs; no working software until late.",
     "incremental": "Needs good up-front planning and modular design; integration effort grows.",
     "agile": "Needs engaged stakeholders and disciplined teams; formal approvals may conflict with procurement rules."},
    {"dimension": "Suitability for e-governance",
     "waterfall": "Suits stable, legally fixed processes (e.g. statutory forms) with heavy compliance sign-off.",
     "incremental": "Suits phased rollouts: launch one service or district at a time.",
     "agile": "Suits citizen-facing services where user feedback should shape the product."},
]


def synthetic_applications(n=60, seed=42):
    """Deterministic synthetic records for the admin dashboard demo."""
    rng = random.Random(seed)
    statuses = STATUS_STEPS + ["Rejected (simulated)"]
    weights = [15, 20, 30, 30, 5]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    rows = []
    for i in range(n):
        rows.append({
            "ref": f"SYN-{i + 1:04d}",
            "service": rng.choice(SERVICES)["name"],
            "status": rng.choices(statuses, weights)[0],
            "month": rng.choice(months),
            "days_to_process": rng.randint(1, 14),
        })
    return rows


def admin_summary():
    rows = synthetic_applications()
    by_service, by_status, by_month = {}, {}, {}
    for r in rows:
        by_service[r["service"]] = by_service.get(r["service"], 0) + 1
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
        by_month[r["month"]] = by_month.get(r["month"], 0) + 1
    avg = round(sum(r["days_to_process"] for r in rows) / len(rows), 1)
    return {"synthetic": True, "total": len(rows), "avg_days_to_process": avg,
            "by_service": by_service, "by_status": by_status, "by_month": by_month,
            "recent": rows[-8:]}
