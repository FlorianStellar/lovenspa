#!/usr/bin/env python3
"""
Validation de l'accès Google Search Console via compte de service.
Nécessite GSC_SA_JSON_B64 dans les variables d'environnement.

Usage:
    python3 tools/seo/gsc_validate.py
    python3 tools/seo/gsc_validate.py --site sc-domain:lovenspa.fr --days 7
"""
import os
import base64
import json
import argparse
from datetime import date, timedelta

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/webmasters.readonly',
]
SITE = 'sc-domain:lovenspa.fr'


def get_service():
    raw = os.environ.get('GSC_SA_JSON_B64')
    if not raw:
        raise EnvironmentError("GSC_SA_JSON_B64 non défini.")
    sa_info = json.loads(base64.b64decode(raw))
    creds = service_account.Credentials.from_service_account_info(sa_info, scopes=SCOPES)
    return build('searchconsole', 'v1', credentials=creds)


def list_sites(service):
    result = service.sites().list().execute()
    return result.get('siteEntry', [])


def query_performance(service, site, start, end, dimensions=('query',), row_limit=10):
    body = {
        'startDate': start,
        'endDate': end,
        'dimensions': list(dimensions),
        'rowLimit': row_limit,
        'startRow': 0,
    }
    return service.searchanalytics().query(siteUrl=site, body=body).execute()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--site', default=SITE)
    parser.add_argument('--days', type=int, default=28)
    args = parser.parse_args()

    service = get_service()

    # 1. Sites accessibles
    sites = list_sites(service)
    print(f"\n✓ Compte de service authentifié")
    print(f"Sites accessibles ({len(sites)}):")
    for s in sites:
        print(f"  • {s['siteUrl']} [{s['permissionLevel']}]")

    # 2. Top requêtes
    end = date.today() - timedelta(days=3)  # GSC a ~3j de délai
    start = end - timedelta(days=args.days)
    print(f"\nTop 10 requêtes — {start} → {end} ({args.site}):")
    resp = query_performance(service, args.site, str(start), str(end))
    rows = resp.get('rows', [])
    if not rows:
        print("  Aucune donnée (délai GSC ou site non indexé).")
    for r in rows:
        keys = r.get('keys', [])
        print(f"  {keys[0]:<40} clics:{r['clicks']:>4}  impr:{r['impressions']:>6}  pos:{r['position']:.1f}")


if __name__ == '__main__':
    main()
