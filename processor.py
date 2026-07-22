import json
from pathlib import Path

from parser import read_pdf
from excel import write_excel
from utils import resource_path
from template_engine import TemplateEngine


CONFIG_FILE = resource_path("config.json")

with open(CONFIG_FILE, "r", encoding="utf8") as f:
    config = json.load(f)


engine = TemplateEngine()


def process(
    pdf_folder,
    output_file,
    progress_callback=None,
    status_callback=None,
):

    rows = []

    pdf_files = sorted(Path(pdf_folder).glob("*.pdf"))

    total = len(pdf_files)

    if total == 0:
        raise Exception("No PDF files found.")

    for i, pdf in enumerate(pdf_files):

        if status_callback:
            status_callback(f"Reading {pdf.name}...")

        pages = read_pdf(str(pdf))

        for page in pages:

            page_rows = engine.parse_page(
                page,
                config
            )

            for row in page_rows:

                row["File"] = pdf.name

                rows.append(row)

        if progress_callback:
            progress_callback(
                i + 1,
                total
            )

    if status_callback:
        status_callback("Writing Excel...")

    write_excel(
        output_file,
        rows
    )

    return total, len(rows), output_file