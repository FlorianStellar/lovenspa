#!/usr/bin/env python3
"""
Client Google Search Console pour l'agent SEO Love'nSpa.

Propriété : sc-domain:lovenspa.fr
Auth      : variable d'environnement GSC_SA_JSON_B64 (base64) ou GSC_SA_JSON (JSON brut)
Latence   : 3 jours (utiliser dataState='final')
Limites   : URL Inspection 2 000/jour, 600/min

Usage rapide :
    from gsc_client import GSCClient
    c = GSCClient()
    rows = c.search_analytics(start='2026-10-01', end='2026-10-28', dimensions=['page'])
"""
import os
import base64
import json
import time
from datetime import date, timedelta
from typing import Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SITE = "sc-domain:lovenspa.fr"
SITE_URL = "https://www.lovenspa.fr"
SCOPES = ["https://www.googleapis.com/auth/webmasters"]


class GSCClient:
    def __init__(self, site: str = SITE):
        self.site = site
        self._service = None

    def _get_service(self):
        if self._service:
            return self._service
        raw = os.environ.get("GSC_SA_JSON_B64") or os.environ.get("GSC_SA_JSON")
        if not raw:
            raise EnvironmentError("GSC_SA_JSON_B64 ou GSC_SA_JSON non défini.")
        try:
            sa_info = json.loads(base64.b64decode(raw))
        except Exception:
            sa_info = json.loads(raw)
        creds = service_account.Credentials.from_service_account_info(
            sa_info, scopes=SCOPES
        )
        self._service = build("searchconsole", "v1", credentials=creds)
        return self._service

    # ------------------------------------------------------------------ #
    # Search Analytics                                                     #
    # ------------------------------------------------------------------ #

    def search_analytics(
        self,
        start: str,
        end: str,
        dimensions: list[str] = ("page",),
        row_limit: int = 25_000,
        data_state: str = "final",
        start_row: int = 0,
        filters: Optional[list[dict]] = None,
        aggregate_type: str = "byPage",
    ) -> list[dict]:
        """Retourne les lignes GSC brutes."""
        body = {
            "startDate": start,
            "endDate": end,
            "dimensions": list(dimensions),
            "rowLimit": min(row_limit, 25_000),
            "startRow": start_row,
            "dataState": data_state,
            "aggregationType": aggregate_type,
        }
        if filters:
            body["dimensionFilterGroups"] = [{"filters": filters}]
        svc = self._get_service()
        resp = (
            svc.searchanalytics()
            .query(siteUrl=self.site, body=body)
            .execute()
        )
        return resp.get("rows", [])

    def search_analytics_all(
        self,
        start: str,
        end: str,
        dimensions: list[str] = ("page",),
        data_state: str = "final",
        filters: Optional[list[dict]] = None,
    ) -> list[dict]:
        """Pagine automatiquement jusqu'à 25 000 * N lignes."""
        all_rows: list[dict] = []
        start_row = 0
        batch = 25_000
        while True:
            rows = self.search_analytics(
                start=start,
                end=end,
                dimensions=dimensions,
                row_limit=batch,
                data_state=data_state,
                start_row=start_row,
                filters=filters,
            )
            all_rows.extend(rows)
            if len(rows) < batch:
                break
            start_row += batch
        return all_rows

    # ------------------------------------------------------------------ #
    # URL Inspection                                                        #
    # ------------------------------------------------------------------ #

    def inspect_url(self, url: str, retries: int = 3) -> dict:
        """
        Inspecte une URL via l'API URL Inspection.
        Retourne le dict `indexStatusResult` aplati + champ `url`.
        """
        svc = self._get_service()
        body = {"inspectionUrl": url, "siteUrl": self.site}
        for attempt in range(retries):
            try:
                resp = (
                    svc.urlInspection()
                    .index()
                    .inspect(body=body)
                    .execute()
                )
                res = resp.get("inspectionResult", {})
                idx = res.get("indexStatusResult", {})
                return {
                    "url": url,
                    "verdict": idx.get("verdict", ""),
                    "coverageState": idx.get("coverageState", ""),
                    "robotsTxtState": idx.get("robotsTxtState", ""),
                    "indexingState": idx.get("indexingState", ""),
                    "lastCrawlTime": (idx.get("lastCrawlTime") or "")[:10],
                    "pageFetchState": idx.get("pageFetchState", ""),
                    "googleCanonical": idx.get("googleCanonical", ""),
                    "userCanonical": idx.get("userCanonical", ""),
                    "referringUrls": idx.get("referringUrls", []),
                    "sitemap": idx.get("sitemap", []),
                    "crawledAs": idx.get("crawledAs", ""),
                }
            except HttpError as e:
                if e.resp.status in (429, 500, 503) and attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return {"url": url, "error": str(e)}
            except (ConnectionResetError, OSError) as e:
                if attempt < retries - 1:
                    time.sleep(2 ** (attempt + 1))
                    self._service = None  # force reconnect
                    continue
                return {"url": url, "error": f"connection_reset: {e}"}
        return {"url": url, "error": "max_retries"}

    def inspect_urls_batch(
        self,
        urls: list[str],
        delay: float = 0.12,
        progress_every: int = 50,
    ) -> list[dict]:
        """
        Inspecte une liste d'URLs en respectant 600/min.
        delay=0.12 s → 500/min (marge de sécurité).
        """
        results = []
        for i, url in enumerate(urls):
            results.append(self.inspect_url(url))
            if (i + 1) % progress_every == 0:
                print(f"  {i+1}/{len(urls)} inspectés…", flush=True)
            time.sleep(delay)
        return results

    # ------------------------------------------------------------------ #
    # Sitemaps                                                              #
    # ------------------------------------------------------------------ #

    def list_sitemaps(self) -> list[dict]:
        svc = self._get_service()
        resp = svc.sitemaps().list(siteUrl=self.site).execute()
        return resp.get("sitemap", [])

    # ------------------------------------------------------------------ #
    # Helpers dates                                                         #
    # ------------------------------------------------------------------ #

    @staticmethod
    def window(days_back: int, lag: int = 3) -> tuple[str, str]:
        """Retourne (start, end) en tenant compte du délai GSC de 3 jours."""
        end = date.today() - timedelta(days=lag)
        start = end - timedelta(days=days_back)
        return str(start), str(end)

    @staticmethod
    def week_window(monday_iso: str) -> tuple[str, str]:
        """Retourne (lundi, dimanche) pour une semaine donnée (format YYYY-MM-DD)."""
        start = date.fromisoformat(monday_iso)
        end = start + timedelta(days=6)
        return str(start), str(end)
