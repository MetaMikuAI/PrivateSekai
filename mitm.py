from mitmproxy import http
from time import time

if_redirect = False
if_redirect = True

redirects = {
    "https://production-game-api.sekai.colorfulpalette.org": "http://127.0.0.1:5000",
    # "https://production-game-api.sekai.colorfulpalette.org/api/suitemasterfile": "http://127.0.0.1:5000/api/suitemasterfile",
    # "https://issue.sekai.colorfulpalette.org/api/signature": "http://127.0.0.1:65535"
}

def request(flow: http.HTTPFlow) -> None:
    # if "suitemasterfile" in flow.request.pretty_url: # for test
    #     return
    if not if_redirect:
        return
    for original_url, redirected_url in redirects.items():
        if flow.request.pretty_url.startswith(original_url):
            flow.request.url = flow.request.pretty_url.replace(original_url, redirected_url)
            print(f"Redirecting {original_url} to {redirected_url}")
            return

# mitmweb -m wireguard --no-http2 -s ./mitm.py --set termlog_verbosity=info --ignore 127.0.0.1 --set connection_strategy=lazy