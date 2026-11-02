# Lab 6 - BRANCH coverage tests for hospital_triage_priority.py
# Goal of this file: every decision goes BOTH ways (True and False).
# Part 1 is the code coverage suite. Part 2 adds the missing decision paths.

import pytest
from hospital_triage_priority import process_triage_wards, monitor_oxygen_manifolds


def make_ward(patients, tier="general", icu_standby=False):
    """Small helper so every test does not repeat the whole ward dictionary."""
    return {
        "is_accepting": True,
        "tier": tier,
        "icu_standby": icu_standby,
        "patients": patients,
    }


# Starter test given in the repo
def test_single_normal_patient():
    wards = [
        {
            "is_accepting": True,
            "tier": "general",
            "icu_standby": False,
            "patients": [{"spo2": 98, "hr": 72, "unconscious": False}],
        }
    ]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 10
    assert result["status"] == "TRIAGE_STABLE"


# Line 3: the ValueError
def test_wards_not_a_list_raises_error():
    with pytest.raises(ValueError):
        process_triage_wards("not a list", 10)


# Line 10: a ward that is not accepting is skipped
def test_ward_not_accepting_is_skipped():
    ward = make_ward([{"spo2": 80, "hr": 130}])
    ward["is_accepting"] = False
    result = process_triage_wards([ward], 10)
    assert result == {"acuity_score": 0, "status": "NO_URGENT_CASES"}


# Lines 21-22: impossible vitals are flagged and not scored
def test_invalid_vitals_are_flagged_not_scored():
    wards = [make_ward([{"spo2": 0, "hr": 80}, {"spo2": 98, "hr": 72}])]
    result = process_triage_wards(wards, 10)
    assert result == {"acuity_score": 10, "status": "TRIAGE_STABLE"}


# Lines 25, 26, 29: unconscious patient in a normal ward scores 100
def test_unconscious_patient_in_general_ward():
    wards = [make_ward([{"spo2": 98, "hr": 72, "unconscious": True}])]
    result = process_triage_wards(wards, 10)
    assert result == {"acuity_score": 100, "status": "TRIAGE_STABLE"}


# Lines 27-28: unconscious patient in an outpatient ward resets the score and stops the ward
def test_unconscious_patient_in_outpatient_ward_resets_score():
    patients = [
        {"spo2": 98, "hr": 72},
        {"spo2": 98, "hr": 72, "unconscious": True},
        {"spo2": 98, "hr": 72},
    ]
    result = process_triage_wards([make_ward(patients, tier="outpatient")], 10)
    assert result == {"acuity_score": 0, "status": "NO_URGENT_CASES"}


# Line 31: low oxygen scores 60
def test_low_spo2_scores_60():
    wards = [make_ward([{"spo2": 85, "hr": 80}])]
    result = process_triage_wards(wards, 10)
    assert result == {"acuity_score": 60, "status": "TRIAGE_STABLE"}


# Line 36: ICU standby adds 25
def test_icu_standby_adds_25():
    wards = [make_ward([{"spo2": 98, "hr": 72}], icu_standby=True)]
    result = process_triage_wards(wards, 10)
    assert result == {"acuity_score": 35, "status": "TRIAGE_STABLE"}


# Line 39: more than 4 flagged entries raises the alert
def test_five_flagged_entries_gives_ward_alert():
    wards = [make_ward([{"spo2": 0, "hr": 80}] * 5)]
    result = process_triage_wards(wards, 10)
    assert result == {"acuity_score": 0, "status": "WARD_ALERT"}


# Line 47: no sensor data
def test_oxygen_no_data():
    assert monitor_oxygen_manifolds([]) == "NO_DATA"


# Lines 53, 55: two low readings in a row
def test_oxygen_two_low_readings_in_a_row_fails():
    assert monitor_oxygen_manifolds([[3.5, 3.0]]) == "PRESSURE_FAILURE"


# ---------------- Part 2: tests added for branch coverage ----------------


# Line 2, second half of the "or": negative score is rejected
def test_negative_default_score_raises_error():
    with pytest.raises(ValueError):
        process_triage_wards([], -1)


# Line 2 False + loop on line 8 never entered
def test_empty_wards_list():
    result = process_triage_wards([], 10)
    assert result == {"acuity_score": 0, "status": "NO_URGENT_CASES"}


# Line 9: "is_accepting" missing means the ward is treated as closed
def test_ward_without_is_accepting_key_is_skipped():
    result = process_triage_wards([{"patients": [{"spo2": 98, "hr": 72}]}], 10)
    assert result == {"acuity_score": 0, "status": "NO_URGENT_CASES"}


# Line 15: patient loop never entered, then ICU standby still applies
def test_accepting_ward_with_no_patients_and_icu_standby():
    result = process_triage_wards([make_ward([], icu_standby=True)], 10)
    assert result == {"acuity_score": 25, "status": "TRIAGE_STABLE"}


# Line 20, second half of the "or": spo2 is fine but heart rate is invalid
def test_invalid_heart_rate_is_flagged():
    wards = [make_ward([{"spo2": 98, "hr": 0}])]
    result = process_triage_wards(wards, 10)
    assert result == {"acuity_score": 0, "status": "NO_URGENT_CASES"}


# Line 30, second half of the "or": spo2 is fine but heart rate is high
def test_high_heart_rate_scores_60():
    wards = [make_ward([{"spo2": 98, "hr": 121}])]
    result = process_triage_wards(wards, 10)
    assert result == {"acuity_score": 60, "status": "TRIAGE_STABLE"}


# Line 30 boundaries: spo2 of exactly 90 and hr of exactly 120 are still normal
def test_boundary_vitals_are_normal():
    wards = [make_ward([{"spo2": 90, "hr": 120}])]
    result = process_triage_wards(wards, 10)
    assert result == {"acuity_score": 10, "status": "TRIAGE_STABLE"}


# Lines 16-18: missing vitals use the safe defaults
def test_patient_with_missing_vitals_uses_defaults():
    result = process_triage_wards([make_ward([{}])], 10)
    assert result == {"acuity_score": 10, "status": "TRIAGE_STABLE"}


# Line 26 False in an outpatient ward: a conscious patient is scored normally
def test_conscious_patient_in_outpatient_ward():
    wards = [make_ward([{"spo2": 98, "hr": 72}], tier="outpatient")]
    result = process_triage_wards(wards, 10)
    assert result == {"acuity_score": 10, "status": "TRIAGE_STABLE"}


# Line 38 boundary: exactly 4 flagged entries is not an alert
def test_exactly_four_flagged_entries_is_not_an_alert():
    wards = [make_ward([{"spo2": 98, "hr": 72, "unconscious": True}] * 4)]
    result = process_triage_wards(wards, 10)
    assert result == {"acuity_score": 400, "status": "TRIAGE_STABLE"}


# Line 8: loop goes round for more than one ward
def test_scores_add_up_across_wards():
    wards = [make_ward([{"spo2": 98, "hr": 72}]), make_ward([{"spo2": 85, "hr": 80}])]
    result = process_triage_wards(wards, 10)
    assert result == {"acuity_score": 70, "status": "TRIAGE_STABLE"}


# Lines 52, 57, 58: all readings healthy
def test_oxygen_all_readings_normal():
    assert monitor_oxygen_manifolds([[5.0, 4.5]]) == "PRESSURE_NORMAL"


# Line 52 boundary: exactly 4.0 is not low
def test_oxygen_exactly_four_is_not_low():
    assert monitor_oxygen_manifolds([[4.0, 4.0]]) == "PRESSURE_NORMAL"


# Line 57: a good reading resets the streak, so low-good-low is not a failure
def test_oxygen_streak_resets_after_good_reading():
    assert monitor_oxygen_manifolds([[3.0, 5.0, 3.0]]) == "PRESSURE_NORMAL"


# Line 50: the streak restarts for each manifold, and line 51 handles an empty manifold
def test_oxygen_streak_does_not_carry_between_manifolds():
    assert monitor_oxygen_manifolds([[3.0], [], [3.0]]) == "PRESSURE_NORMAL"


# Line 49: the failure can be in a later manifold
def test_oxygen_failure_in_second_manifold():
    assert monitor_oxygen_manifolds([[5.0], [3.0, 3.0]]) == "PRESSURE_FAILURE"
