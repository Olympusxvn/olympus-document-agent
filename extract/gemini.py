from __future__ import annotations

import json
import os

from extract.plan import InvoicePlan, plan_from_mapping


EXTRACT_INSTRUCTION = (
    "Extract a Vietnamese VAT invoice (hóa đơn GTGT) from the image. "
    "Return JSON only with keys: invoice_number, seller_mst, buyer_mst, invoice_date "
    "(YYYY-MM-DD), seller_name, currency (VND), subtotal, vat_amount, total, "
    "confidence (0 to 1), notes. Money fields must be integers in VND. "
    "Do not fix arithmetic if the printed total is wrong — copy the printed numbers."
)


class GeminiPlanExtractor:
    def extract(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> InvoicePlan:
        from google import genai
        from google.genai import types

        model = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
        use_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "TRUE").lower() in {
            "1",
            "true",
            "yes",
        }
        kwargs: dict = {}
        if use_vertex:
            kwargs["vertexai"] = True
            kwargs["project"] = os.environ.get("GOOGLE_CLOUD_PROJECT")
            kwargs["location"] = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
        client = genai.Client(**kwargs)
        mime = mime_type or "image/jpeg"
        response = client.models.generate_content(
            model=model,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime),
                EXTRACT_INSTRUCTION,
            ],
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        text = response.text or "{}"
        return plan_from_mapping(json.loads(text))


def extract_with_one_retry(
    extractor: object,
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
) -> InvoicePlan:
    plan = extractor.extract(image_bytes, mime_type)
    if str(plan.invoice_number).strip() and str(plan.seller_mst).strip():
        return plan
    return extractor.extract(image_bytes, mime_type)
