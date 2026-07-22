import pdfplumber


def read_pdf(pdf_path):

    pages = []

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            text = page.extract_text()

            if text is None:
                text = ""

            pages.append(text)

    return pages