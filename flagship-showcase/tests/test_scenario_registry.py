"""
scenario_registry.py is pure data, but it's data app.py and adapters.py
both trust blindly (e.g. adapters.py's _WORKSHOP_ATTACK_NAMES dispatch, or
app.py reading scenario["customer_message"] unconditionally). These tests
exist to catch a typo'd/missing key here before it surfaces as a confusing
runtime KeyError during a live demo instead.
"""

from scenario_registry import SCENARIOS, SCENARIOS_BY_ID

REQUIRED_KEYS = {
    "id", "number", "nav_label", "title", "category", "blurb",
    "technical_detail", "backend", "customer_message",
}
VALID_BACKENDS = {"workshop", "tool_chain", "rag"}


def test_exactly_five_scenarios():
    assert len(SCENARIOS) == 5


def test_every_scenario_has_required_keys():
    for s in SCENARIOS:
        missing = REQUIRED_KEYS - s.keys()
        assert not missing, f"scenario {s.get('id')!r} is missing keys: {missing}"


def test_ids_are_unique():
    ids = [s["id"] for s in SCENARIOS]
    assert len(ids) == len(set(ids))


def test_numbers_are_1_through_5_in_order():
    assert [s["number"] for s in SCENARIOS] == [1, 2, 3, 4, 5]


def test_backend_is_one_of_the_three_known_kinds():
    for s in SCENARIOS:
        assert s["backend"] in VALID_BACKENDS, s["id"]


def test_scenarios_by_id_is_consistent_with_scenarios():
    assert set(SCENARIOS_BY_ID.keys()) == {s["id"] for s in SCENARIOS}
    for s in SCENARIOS:
        assert SCENARIOS_BY_ID[s["id"]] is s


def test_workshop_backend_scenarios_declare_an_attack_name():
    # adapters._WORKSHOP_ATTACK_NAMES maps scenario id -> attack_name for
    # exactly these three -- if a "workshop" scenario ever lost this key,
    # run_scenario() would raise instead of degrading gracefully.
    for s in SCENARIOS:
        if s["backend"] == "workshop":
            assert "attack_name" in s, s["id"]


def test_attachment_scenario_sample_pdf_is_relative_not_absolute():
    scenario = SCENARIOS_BY_ID["attachment"]
    assert "sample_pdf" in scenario
    assert not scenario["sample_pdf"].startswith("/")
