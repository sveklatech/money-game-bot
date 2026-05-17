import json
import os

CONTENT_DIR = os.path.join(os.path.dirname(__file__), "..", "content")


def _load(filename: str):
    with open(os.path.join(CONTENT_DIR, filename), encoding="utf-8") as f:
        return json.load(f)


_days = None
_process = None
_manifesto = None
_concepts = None
_scenarios = None


def get_days():
    global _days
    if _days is None:
        _days = _load("days.json")
    return _days


def get_process():
    global _process
    if _process is None:
        _process = _load("process.json")
    return _process


def get_manifesto():
    global _manifesto
    if _manifesto is None:
        _manifesto = _load("manifesto.json")
    return _manifesto


def get_concepts():
    global _concepts
    if _concepts is None:
        _concepts = _load("concepts.json")
    return _concepts


def get_scenarios():
    global _scenarios
    if _scenarios is None:
        _scenarios = _load("scenarios.json")
    return _scenarios


def get_day(day_number: int) -> dict | None:
    days = get_days()
    for d in days:
        if d["day"] == day_number:
            return d
    return None


def get_process_step(step_number: int) -> dict | None:
    data = get_process()
    steps = data["full_process"]["steps"]
    for s in steps:
        if s["number"] == step_number:
            return s
    return None


def get_mini_process_text() -> str:
    data = get_process()
    steps = data["mini_process"]["steps"]
    lines = "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps))
    return f"✨ *Мини-Процесс*\n\n{lines}"


def get_manifesto_part(part_id: str) -> dict | None:
    data = get_manifesto()
    for part in data["parts"]:
        if part["id"] == part_id:
            return part
    return None


def get_concept(concept_id: str) -> dict | None:
    data = get_concepts()
    if concept_id == "phases":
        return {
            "name": "Фаза 1 vs Фаза 2",
            "description": (
                "Фаза 1 — состояние неведения: внешний мир реален, деньги ограничены, другие люди — источник или угроза.\n\n"
                "Фаза 2 — состояние пробуждения: ты создаёшь голограмму, дискомфорт — ресурс, деньги — форма Признательности."
            )
        }
    if concept_id == "dictionary":
        pairs = data["phase_comparison"]["pairs"]
        lines = "\n".join(f"• _{p['phase1']}_ → *{p['phase2']}*" for p in pairs)
        return {
            "name": "Словарь Фазы 1 → Фазы 2",
            "description": lines
        }
    for c in data["concepts"]:
        if c["id"] == concept_id:
            return c
    return None


def get_scenario(scenario_id: int) -> dict | None:
    scenarios = get_scenarios()
    for s in scenarios:
        if s["id"] == scenario_id:
            return s
    return None


def get_morning_ritual() -> str:
    data = get_manifesto()
    return data["morning_ritual"]


def get_evening_ritual() -> str:
    data = get_manifesto()
    return data["evening_ritual"]


def get_core_affirmation() -> str:
    data = get_manifesto()
    return data["core_affirmation"]
