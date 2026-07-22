from openpyxl import Workbook


# ==========================================================
# Fixed column order
# ==========================================================

FIXED_HEADERS = [
    "File",
    "Procedure",
    "Eye",

    "Patient",
    "ID",
    "Surgeon",
    "Treatment Date",
]

COLUMN_NAMES = {
    "Lenticule Energy Posterior": "PE",
    "Lenticule Energy Anterior": "AE",
    "Ring Energy": "RE",
    "Entry Energy": "EE",
}

SILK_HEADERS = [

    "Manifest Sphere",
    "Manifest Cylinder",
    "Manifest Axis",

    "Sphere Adjustment",
    "Cylinder Adjustment",

    "Sphere Correction",
    "Cylinder Correction",

    "Flat K1",
    "Steep K2",

    "Cyclotorsion",

    "Centration Offset X",
    "Centration Offset Y",

    "Lenticule Energy Posterior",
    "Lenticule Energy Anterior",

    "Ring Energy",
    "Entry Energy",

    "Anterior Depth",

    "Optical Zone",

    "Laser Time"
]

FLAP_HEADERS = [

    "Diameter",
    "Depth",

    "Hinge Position",
    "Hinge Angle",

    "Oversize",

    "Side Cut Angle",
    "Side Cut Energy",

    "Bed Energy",

    "Pocket"
]


# ==========================================================
# Build column order
# ==========================================================

def build_headers(rows):

    headers = []

    # Fixed columns
    for h in FIXED_HEADERS:
        if h not in headers:
            headers.append(h)

    # SILK columns
    for h in SILK_HEADERS:
        if h not in headers:
            headers.append(h)

    # FLAP columns
    for h in FLAP_HEADERS:
        if h not in headers:
            headers.append(h)

    # Append remaining columns automatically
    for row in rows:

        for key in row.keys():

            if key not in headers:
                headers.append(key)

    return headers


# ==========================================================
# Auto fit
# ==========================================================

def autofit(ws):

    for column_cells in ws.columns:

        max_length = max(
            len(str(cell.value)) if cell.value is not None else 0
            for cell in column_cells
        )

        ws.column_dimensions[
            column_cells[0].column_letter
        ].width = max_length + 3


# ==========================================================
# Write Excel
# ==========================================================

def write_excel(output_path, rows):

    wb = Workbook()

    ws = wb.active
    ws.title = "ELITA"

    if not rows:

        ws.append(FIXED_HEADERS)

    else:

        headers = build_headers(rows)

        excel_headers = [
            COLUMN_NAMES.get(h, h)
            for h in headers
        ]

        ws.append(excel_headers)

        for row in rows:

            ws.append([
                row.get(header, "")
                for header in headers
            ])

        autofit(ws)

    try:

        wb.save(output_path)

    except PermissionError:

        raise PermissionError(
            "The output Excel file is currently open.\n\n"
            "Please close the Excel file and try again."
        )