import httpx


def fetch_status(url, transport=None):
    with httpx.Client(transport=transport, timeout=5, follow_redirects=False) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text[:2000]


def post_summary(summary, transport=None):
    with httpx.Client(transport=transport, timeout=5, follow_redirects=False) as client:
        response = client.post("https://hooks.example.invalid/triage", json=summary)
        response.raise_for_status()
