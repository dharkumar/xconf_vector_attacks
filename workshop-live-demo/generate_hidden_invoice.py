"""
Generates REAL PDF artifacts demonstrating the concealment techniques
behind Attack 7 (hidden_multilingual_invoice_injection) and its two
pre-tested variants in redteam_test.py -- genuine files to show
participants, not just described techniques.

Each PDF's visible page is an ordinary-looking invoice. Below it, an
instruction is hidden using one of two real PDF concealment techniques:

  "color"     -- white fill text on the white page background at a tiny
                 font size. Invisible because it's literally the same
                 color as the page; genuinely present in the text layer.
  "invisible" -- PDF text rendering mode 3 ("neither fill nor stroke" --
                 the mode legitimately used for OCR text layers over
                 scanned documents, searchable/copyable but never drawn).
                 Invisible regardless of color or what's behind it; a
                 stronger, more realistic technique than color-matching.

Requires reportlab (`pip install reportlab`) -- not part of the main
repo's requirements.txt, since it's only needed for this demo asset.

Run:
    python3 generate_hidden_invoice.py

Produces all 3 variant PDFs listed in VARIANTS below.

To reveal any hidden layer (what any text-extraction pipeline sees):
    pdftotext <file>.pdf -
  or open it in any PDF viewer and Select All + Copy the page text.
"""

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.colors import black, white
from reportlab.pdfgen import canvas

from invoice_fixtures import INVOICE_CASES, invoice_display_no

# Built straight from invoice_fixtures.py -- the same module redteam_test.py
# reads its live-chat fixture from, so the PDF this script renders and the
# fixture the model actually talks to can't drift apart.
VARIANTS = [
    {
        "output": case["pdf_file"],
        "invoice_no": invoice_display_no(key),
        "date": case["date"],
        "customer": case["customer_name"],
        "item": case["item"],
        "total": case["total"],
        "technique": case["technique"],
        "hidden_text": case["hidden_text"],
    }
    for key, case in INVOICE_CASES.items()
]


def _wrap(text, width=110):
    words, line, lines = text.split(), "", []
    for w in words:
        candidate = f"{line} {w}".strip()
        if len(candidate) > width:
            lines.append(line)
            line = w
        else:
            line = candidate
    lines.append(line)
    return lines


def build_pdf(spec):
    path = spec["output"]
    c = canvas.Canvas(path, pagesize=LETTER)
    width, height = LETTER

    # --- Visible invoice content (ordinary black text) ---------------
    c.setFillColor(black)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(72, height - 90, "INVOICE")

    c.setFont("Helvetica", 10)
    c.drawString(72, height - 120, f"Invoice #: {spec['invoice_no']}")
    c.drawString(72, height - 135, f"Date: {spec['date']}")
    c.drawString(72, height - 150, f"Bill To: {spec['customer']}")

    c.setFont("Helvetica-Bold", 10)
    c.drawString(72, height - 190, "Description")
    c.drawString(400, height - 190, "Amount")
    c.line(72, height - 195, 520, height - 195)

    c.setFont("Helvetica", 10)
    c.drawString(72, height - 215, spec["item"])
    c.drawString(400, height - 215, spec["total"])

    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, height - 250, "Order Total:")
    c.drawString(400, height - 250, spec["total"])

    c.setFont("Helvetica-Oblique", 9)
    c.drawString(72, height - 290, "Thank you for your business!")

    # --- Hidden layer ---------------------------------------------------
    lines = _wrap(spec["hidden_text"])

    if spec["technique"] == "color":
        # Same RGB as the page background -- invisible to the eye, present
        # in the text layer regardless.
        text_obj = c.beginText(72, 60)
        text_obj.setFont("Helvetica", 4)
        text_obj.setFillColor(white)
        for ln in lines:
            text_obj.textLine(ln)
        c.drawText(text_obj)
    elif spec["technique"] == "invisible":
        # PDF text rendering mode 3: neither fill nor stroke. This is the
        # mode real OCR pipelines use to overlay searchable text on a
        # scanned image without drawing anything -- genuinely invisible
        # regardless of color or what's on the page behind it.
        text_obj = c.beginText(72, 60)
        text_obj.setFont("Helvetica", 8)
        text_obj.setTextRenderMode(3)
        for ln in lines:
            text_obj.textLine(ln)
        c.drawText(text_obj)
    else:
        raise ValueError(f"unknown technique {spec['technique']!r}")

    c.showPage()
    c.save()
    print(f"Wrote {path} (technique={spec['technique']})")


if __name__ == "__main__":
    for spec in VARIANTS:
        build_pdf(spec)
