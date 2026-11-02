# Lab 6 - CODE (line) coverage tests for hospital_triage_priority.py
# Goal of this file: execute at least 90% of the lines in the application.

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
