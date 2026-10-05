import os

import httpx
from dotenv import load_dotenv


load_dotenv()


def trigger_n8n(batch_id: str, results: list[dict]) -> dict:

    webhook_url = os.getenv("N8N_WEBHOOK_URL")

    if not webhook_url:
        raise RuntimeError(
            "N8N_WEBHOOK_URL is not configured."
        )

    payload = {
        "batch_id": batch_id,
        "results": results
    }

    response = httpx.post(
        webhook_url,
        json=payload,
        timeout=30.0
    )

    response.raise_for_status()

    return {
        "success": True,
        "status_code": response.status_code
    }