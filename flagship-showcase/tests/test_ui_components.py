"""
ui_components.py is mostly Streamlit rendering (st.container/st.expander/
etc.), which needs a live Streamlit script run to test meaningfully and
isn't covered here. What's tested is the pure logic: _format_result's
str-vs-JSON branching, extract_pdf_text's real (not mocked) subprocess
call, and that doc_identity/doc_content are genuinely the same functions
adapters.py defines -- not a second, silently-diverging copy.
"""

import json

import adapters
import ui_components


# ---------------------------------------------------------------------------
# _format_result
# ---------------------------------------------------------------------------

def test_format_result_none_stays_none():
    assert ui_components._format_result(None) is None


def test_format_result_string_passed_through_unchanged():
    assert ui_components._format_result("already text") == "already text"


def test_format_result_dict_becomes_readable_json():
    formatted = ui_components._format_result({"status": "success", "amount_usd": 2450.0})
    assert json.loads(formatted) == {"status": "success", "amount_usd": 2450.0}


# ---------------------------------------------------------------------------
# doc_identity / doc_content re-export
#
# Guards against the exact duplication this quality pass removed: two
# independent copies of "how do I read a retrieved doc" silently drifting
# apart between adapters.py (retrieval) and ui_components.py (rendering).
# ---------------------------------------------------------------------------

def test_doc_identity_and_doc_content_are_the_same_object_as_adapters():
    assert ui_components.doc_identity is adapters.doc_identity
    assert ui_components.doc_content is adapters.doc_content


# ---------------------------------------------------------------------------
# extract_pdf_text -- genuine subprocess call, no mocking of pdftotext
# ---------------------------------------------------------------------------

def test_extract_pdf_text_on_garbage_bytes_does_not_raise():
    # Not a real PDF -- pdftotext should just fail to extract anything
    # rather than crash the app; this asserts the function surfaces that
    # as an empty-ish string, not an exception.
    result = ui_components.extract_pdf_text(b"not a real pdf")
    assert isinstance(result, str)
