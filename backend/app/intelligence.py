import json
from datetime import datetime, timedelta, timezone

import httpx


async def fetch_nvd(cpe_name: str, api_key: str | None = None) -> list[dict]:
    headers = {"apiKey": api_key} if api_key else {}
    params = {"cpeName": cpe_name}
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get("https://services.nvd.nist.gov/rest/json/cves/2.0", params=params, headers=headers)
        response.raise_for_status()
        return response.json().get("vulnerabilities", [])


async def fetch_kev() -> set[str]:
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get("https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json")
        response.raise_for_status()
        return {item["cveID"] for item in response.json().get("vulnerabilities", [])}


def cache_is_fresh(fetched_at: datetime | None, hours: int = 24) -> bool:
    return bool(fetched_at and fetched_at > datetime.now(timezone.utc) - timedelta(hours=hours))
