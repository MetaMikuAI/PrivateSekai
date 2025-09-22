from mitmproxy import http
from time import time

if_redirect = True

redirects = {
    "https://production-game-api.sekai.colorfulpalette.org": "http://127.0.0.1:5000",
    # "https://issue.sekai.colorfulpalette.org/api/signature": "http://127.0.0.1:65535" # -> drop
}

def request(flow: http.HTTPFlow) -> None:
    if not if_redirect:
        return
    for original_url, redirected_url in redirects.items():
        if flow.request.pretty_url.startswith(original_url):
            flow.request.url = flow.request.pretty_url.replace(original_url, redirected_url)
            print(f"Redirecting {original_url} to {redirected_url}")
            return

# mitmweb -m wireguard --no-http2 -s ./mitm.py --set termlog_verbosity=info --ignore 127.0.0.1