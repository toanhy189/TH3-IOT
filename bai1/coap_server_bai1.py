"""Bai 1: CoAP message server (GET and POST)."""

import argparse
import asyncio
from datetime import datetime

import aiocoap
from aiocoap import resource


PATH = ("iot", "lab", "message")


class MessageResource(resource.Resource):
    def __init__(self):
        super().__init__()
        self.last_message = None

    async def render_get(self, request):
        print("GET request received: /" + "/".join(PATH), flush=True)
        message = self.last_message or "Xin chao tu CoAP Server"
        return aiocoap.Message(code=aiocoap.CONTENT, payload=message.encode("utf-8"))

    async def render_post(self, request):
        try:
            message = request.payload.decode("utf-8").strip()
        except UnicodeDecodeError:
            return aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=b"Payload must be UTF-8")
        if not message:
            return aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=b"Payload must not be empty")

        self.last_message = message
        print(f"POST request received:\nPayload: {message}\nTime: {datetime.now():%H:%M:%S}", flush=True)
        return aiocoap.Message(code=aiocoap.CHANGED, payload=b"Server da nhan thong diep")


async def main(host):
    site = resource.Site()
    site.add_resource(PATH, MessageResource())
    context = await aiocoap.Context.create_server_context(site, bind=(host, 5683))
    print(f"CoAP Server started on {host}:5683", flush=True)
    try:
        await asyncio.Future()
    finally:
        await context.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bai 1 CoAP server")
    parser.add_argument("--host", default="127.0.0.1", help="Local IP address to bind")
    try:
        asyncio.run(main(parser.parse_args().host))
    except KeyboardInterrupt:
        print("Server stopped")
