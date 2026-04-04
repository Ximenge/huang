import requests
import json
import sys
from typing import List

INDEXNOW_KEY = "de748853d6e24417b898bb2b3d2c62d8"
SITE_HOST = "91tutu.cc"
SITE_URL = "https://91tutu.cc"

INDEXNOW_ENDPOINTS = [
    "https://www.bing.com/indexnow",
    "https://yandex.com/indexnow",
    "https://searchadvisor.naver.com/indexnow",
]

def notify_indexnow(urls: List[str], verbose: bool = True) -> dict:
    results = {}
    
    payload = {
        "host": SITE_HOST,
        "key": INDEXNOW_KEY,
        "urlList": urls
    }
    
    for endpoint in INDEXNOW_ENDPOINTS:
        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers={"Content-Type": "application/json; charset=utf-8"},
                timeout=30
            )
            results[endpoint] = {
                "status_code": response.status_code,
                "success": response.status_code in [200, 202]
            }
            if verbose:
                status = "✓" if response.status_code in [200, 202] else "✗"
                print(f"{status} {endpoint}: HTTP {response.status_code}")
        except Exception as e:
            results[endpoint] = {
                "status_code": None,
                "error": str(e),
                "success": False
            }
            if verbose:
                print(f"✗ {endpoint}: {e}")
    
    return results

def notify_single_url(url: str, verbose: bool = True) -> dict:
    results = {}
    
    full_url = url if url.startswith("http") else f"{SITE_URL}{url}"
    
    for endpoint in INDEXNOW_ENDPOINTS:
        try:
            api_url = f"{endpoint}?url={full_url}&key={INDEXNOW_KEY}"
            response = requests.get(api_url, timeout=30)
            results[endpoint] = {
                "status_code": response.status_code,
                "success": response.status_code in [200, 202]
            }
            if verbose:
                status = "✓" if response.status_code in [200, 202] else "✗"
                print(f"{status} {endpoint}: HTTP {response.status_code}")
        except Exception as e:
            results[endpoint] = {
                "status_code": None,
                "error": str(e),
                "success": False
            }
            if verbose:
                print(f"✗ {endpoint}: {e}")
    
    return results

def notify_sitemap(verbose: bool = True) -> dict:
    sitemap_url = f"{SITE_URL}/sitemap-index.xml"
    return notify_single_url(sitemap_url, verbose)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python indexnow_notify.py <url>           # Notify single URL")
        print("  python indexnow_notify.py --sitemap       # Notify sitemap")
        print("  python indexnow_notify.py --urls url1 url2 ...  # Notify multiple URLs")
        sys.exit(1)
    
    if sys.argv[1] == "--sitemap":
        print(f"Notifying IndexNow about sitemap...")
        notify_sitemap()
    elif sys.argv[1] == "--urls":
        urls = sys.argv[2:]
        if not urls:
            print("Error: No URLs provided")
            sys.exit(1)
        print(f"Notifying IndexNow about {len(urls)} URLs...")
        notify_indexnow(urls)
    else:
        url = sys.argv[1]
        print(f"Notifying IndexNow about: {url}")
        notify_single_url(url)
    
    print("\nDone!")
