from extractor import extract_fields
from extractor import HEADER_FIELDS
from .base import BaseTemplate


class SilkTemplate(BaseTemplate):

    NAME = "SILK"
    PROCEDURE = "SILK"

    def match(self, text):

        upper = text.upper()

        return (
            "SILK" in upper
            and "MANIFEST SPHERE" in upper
        )

    def parse(self, text, config):

        rows = []

        fields = config["fields"]

        # Header (Patient, Surgeon, ID, Treatment Date...)
        header = extract_fields(
            text,
            HEADER_FIELDS
        )

        # Treatment data
        row = extract_fields(
            text,
            fields
        )

        # Merge header
        row.update(header)

        # Procedure
        row["Procedure"] = self.PROCEDURE

        upper = text.upper()

        if "SILK OD" in upper:

            row["Eye"] = "OD"

        elif "SILK OS" in upper:

            row["Eye"] = "OS"

        else:

            return rows

        rows.append(row)

        return rows