import math


def _to_number(text):
    """Turn text into a normal finite number, or return None if that is not possible.

    float() alone is not safe enough: it also accepts "nan", "inf" and
    huge values like "1e999", which are not real readings.
    """
    try:
        value = float(text)
    except (ValueError, TypeError):
        return None
    if math.isnan(value) or math.isinf(value):
        return None
    return value


def parse_vitals_summary(vitals_csv):
    # FIX: None or a non-string used to crash on .split() (AttributeError)
    if not isinstance(vitals_csv, str):
        return "Invalid input: vitals must be text like 80,98,37.0"

    parts = vitals_csv.split(',')
    # FIX: fewer than 3 values used to crash with IndexError
    if len(parts) != 3:
        return "Invalid input: expected exactly 3 values (HR,SpO2,Temp)"

    # FIX: text like "abc" or "" used to crash float() with ValueError
    hr = _to_number(parts[0])
    spo2 = _to_number(parts[1])
    temp = _to_number(parts[2])
    if hr is None or spo2 is None or temp is None:
        return "Invalid input: HR, SpO2 and Temp must be numbers"

    # FIX: reject impossible readings (negative heart rate, SpO2 above 100%, etc.)
    if hr <= 0 or spo2 <= 0 or spo2 > 100 or temp <= 0:
        return "Invalid input: vitals out of possible range"

    critical = hr > 120 or spo2 < 90 or temp > 39.0
    return f"Vitals: HR={hr}, SpO2={spo2}% - {'CRITICAL' if critical else 'STABLE'}"


def compute_patient_bmi(bmi_string):
    # FIX: None or a non-string used to crash on .split() (AttributeError)
    if not isinstance(bmi_string, str):
        return "Invalid input: expected text like 70/1.75"

    # FIX: no "/" or more than one "/" used to crash the unpacking with ValueError
    parts = bmi_string.split('/')
    if len(parts) != 2:
        return "Invalid input: expected weight/height like 70/1.75"

    weight = _to_number(parts[0])
    height = _to_number(parts[1])
    if weight is None or height is None:
        return "Invalid input: weight and height must be numbers"

    # FIX: height 0 used to crash with ZeroDivisionError; negative values make no sense
    if weight <= 0 or height <= 0:
        return "Invalid input: weight and height must be greater than 0"

    # FIX: huge heights like 1e200 used to crash height ** 2 with OverflowError
    try:
        bmi = weight / (height ** 2)
    except (OverflowError, ZeroDivisionError):
        return "Invalid input: values are too large or too small"
    if math.isinf(bmi) or math.isnan(bmi):
        return "Invalid input: values are too large or too small"
    return round(bmi, 2)


def assign_ward_bed(allocation_code):
    # FIX: None or a non-string used to crash on .strip() (AttributeError)
    if not isinstance(allocation_code, str):
        return "Invalid input: expected text like ICU-05"

    # FIX: no "-" or more than one "-" used to crash the unpacking with ValueError
    parts = allocation_code.strip().split('-')
    if len(parts) != 2:
        return "Invalid input: expected WARD-BED like ICU-05"
    ward, bed_str = parts

    ward_names = {
        "ER": "Emergency Room",
        "ICU": "Intensive Care Unit",
        "GEN": "General Ward",
        "PED": "Pediatrics"
    }
    # FIX: an unknown ward like "XYZ" used to crash with KeyError
    ward_name = ward_names.get(ward.strip().upper())
    if ward_name is None:
        return "Invalid input: unknown ward (use ER, ICU, GEN or PED)"

    # FIX: a bed like "abc" used to crash int() with ValueError
    bed_str = bed_str.strip()
    if not (bed_str.isascii() and bed_str.isdigit()):
        return "Invalid input: bed number must be digits"
    bed_num = int(bed_str)
    if bed_num <= 0:
        return "Invalid input: bed number must be greater than 0"

    return f"{ward_name} Bed #{bed_num}"


def main():
    print("==== Running parse_vitals_summary ====")
    v_input = input("Enter vitals (HR,SpO2,Temp): ")
    print("Summary:", parse_vitals_summary(v_input))

    print("\n==== Running compute_patient_bmi ====")
    b_input = input("Enter weight/height (e.g. 70/1.75): ")
    print("BMI:", compute_patient_bmi(b_input))

    print("\n==== Running assign_ward_bed ====")
    w_input = input("Enter allocation (e.g. ICU-05): ")
    print("Assignment:", assign_ward_bed(w_input))


if __name__ == "__main__":
    main()
