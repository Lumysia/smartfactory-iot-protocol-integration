"""Small CoAP-to-HTTP proxy used for the assignment header mapping check."""

import asyncio
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import aiocoap
from aiocoap import Code, Message


COAP_BASE = "coap://localhost"


async def _coap_get(path: str) -> Message:
    ctx = await aiocoap.Context.create_client_context()
    try:
        return await ctx.request(Message(code=Code.GET, uri=f"{COAP_BASE}{path}")).response
    finally:
        await ctx.shutdown()


class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        try:
            response = asyncio.run(_coap_get(self.path))
        except Exception as exc:
            payload = f"CoAP proxy error: {exc}".encode()
            self.send_response(502)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        payload = response.payload
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "max-age=60")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args) -> None:
        return


def main() -> None:
    server = ThreadingHTTPServer(("localhost", 8080), ProxyHandler)
    print("HTTP proxy running on http://localhost:8080")
    server.serve_forever()


if __name__ == "__main__":
    main()
