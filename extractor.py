import re


UNITS = [
    " D",
    " µm",
    " °",
    " deg",
    " mm",
    " s",
    " nJ",
    " %"
]


TEXT_FIELDS = {
    "Template Name",
    "Pocket",
    "Hinge Position",
}


HEADER_FIELDS = {
    "Patient",
    "Surgeon",
    "ID",
    "Treatment Date",
}


def clean_value(value):

    value = value.replace("*", "").strip()

    for unit in UNITS:
        value = value.replace(unit, "")

    return value.strip()


# ---------------------------------------------------------
# Numeric field
# ---------------------------------------------------------

def extract_numeric(text, field):

    pattern = rf"{re.escape(field)}:\s*\*?\s*([-+]?\d+(?:\.\d+)?)"

    match = re.search(pattern, text)

    if not match:
        return ""

    return clean_value(match.group(1))


# ---------------------------------------------------------
# Text field
# ---------------------------------------------------------

def extract_text(text, field):

    pattern = rf"{re.escape(field)}:\s*([A-Za-z ]+)"

    match = re.search(pattern, text)

    if not match:
        return ""

    return clean_value(match.group(1))


# ---------------------------------------------------------
# Header field
# ---------------------------------------------------------

def extract_header(text, field):

    if field == "Patient":

        pattern = r"Patient:\s*(.*?)\s+Date of Birth:"

    elif field == "Surgeon":

        pattern = r"Surgeon:\s*(.*?)\s+Treatment Date:"

    elif field == "ID":

        pattern = r"ID:\s*(.*?)\s+Eye Treated:"

    elif field == "Treatment Date":

        pattern = r"Treatment Date:\s*([0-9/]+)"

    else:

        return ""

    match = re.search(
        pattern,
        text,
        re.IGNORECASE | re.DOTALL
    )

    if not match:
        return ""

    return clean_value(match.group(1))


# ---------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------

def extract_value(text, field):

    if field in HEADER_FIELDS:
        return extract_header(text, field)

    if field in TEXT_FIELDS:
        return extract_text(text, field)

    return extract_numeric(text, field)


# ---------------------------------------------------------
# Extract all fields
# ---------------------------------------------------------

def extract_fields(text, fields):

    result = {}

    for field in fields:

        result[field] = extract_value(text, field)

    return result