from hypothesis import given, strategies as st
from processor import parse_vitals_summary, compute_patient_bmi, assign_ward_bed


# Hypothesis feeds each test hundreds of random inputs: any text at all, or None.
# The property we check: the function must NEVER crash, whatever it is given.
# If it raises any exception, the test fails and Hypothesis shows the input that broke it.

@given(st.text() | st.none())
def test_parse_vitals_summary_no_crash(s):
    try:
        result = parse_vitals_summary(s)
        assert isinstance(result, str)
    except Exception as e:
        assert False, f"parse_vitals_summary crashed on {s!r} with: {type(e).__name__}: {e}"


@given(st.text() | st.none())
def test_compute_patient_bmi_safe(s):
    try:
        compute_patient_bmi(s)
    except Exception as e:
        assert False, f"compute_patient_bmi crashed on {s!r} with: {type(e).__name__}: {e}"


@given(st.text() | st.none())
def test_assign_ward_bed_safe(s):
    try:
        result = assign_ward_bed(s)
        assert isinstance(result, str)
    except Exception as e:
        assert False, f"assign_ward_bed crashed on {s!r} with: {type(e).__name__}: {e}"
