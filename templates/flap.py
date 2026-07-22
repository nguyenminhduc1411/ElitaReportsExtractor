from extractor import extract_fields
from extractor import HEADER_FIELDS
from .base import BaseTemplate


class FlapTemplate(BaseTemplate):

    NAME = "FLAP"
    PROCEDURE = "FLAP"

    def match(self, text):

        upper = text.upper()

        return (
            "FLAP" in upper
            and "DIAMETER" in upper
        )

    def parse(self, text, config):

        rows = []

        fields = config["fields"]

        header = extract_fields(
            text,
            HEADER_FIELDS
        )

        upper = text.upper()

        # Không phải report FLAP
        if "FLAP" not in upper:
            return rows

        # Không tìm thấy OD
        if "FLAP OD" not in upper:

            print("\n========== FLAP REPORT ==========")
            print(text)
            print("=================================\n")

            return rows

        # Tách OD an toàn
        parts = text.split("FLAP OD", 1)

        if len(parts) < 2:

            print("\nCannot split FLAP OD")
            print(text)

            return rows

        part = parts[1]

        # Có OS hay không
        if "FLAP OS" in part:

            od_text, os_text = part.split(
                "FLAP OS",
                1
            )

        else:

            od_text = part
            os_text = ""

        # ---------- OD ----------

        row = extract_fields(
            od_text,
            fields
        )

        row.update(header)

        row["Procedure"] = self.PROCEDURE
        row["Eye"] = "OD"

        rows.append(row)

        # ---------- OS ----------

        if os_text:

            row = extract_fields(
                os_text,
                fields
            )

            row["Procedure"] = self.PROCEDURE
            row["Eye"] = "OS"

            row.update(header)

            rows.append(row)

        return rows