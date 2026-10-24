"""Bai 3: smart light with CoAP GET, PUT, and Observe."""

import argparse
import asyncio
import json

import aiocoap
from aiocoap import resource


class LightResource(resource.ObservableResource):
    def __init__(self):
        super().__init__()
        self.status = "OFF"

    def update_observation_count(self, newcount):
        print(f"Active Observe clients: {newcount}", flush=True)

    async def render_get(self, request):
        payload = {"device_id": "light01", "status": self.status}
        return aiocoap.Message(
            code=aiocoap.CONTENT,
            payload=json.dumps(payload).encode("utf-8"),
            content_format=50,  # application/json
        )

    async def render_put(self, request):
        try:
            data = json.loads(request.payload.decode("utf-8"))
            if not isinstance(data, dict):
                raise ValueError("Expected a JSON object")
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
            return aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=b"Invalid JSON payload")

        if data.get("device_id") != "light01" or data.get("command") not in ("ON", "OFF"):
            return aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=b"Expected light01 and ON or OFF")

        command = data["command"]
        print(f"PUT request received:\nDevice: light01\nCommand: {command}", flush=True)
        if self.status != command:
            previous = self.status
            self.status = command
            print(f"Light state changed: {previous} -> {command}\nNotify observers: {command}", flush=True)
            self.updated_state()
        else:
            print(f"Light already {command}; no notification", flush=True)
        message = "Da bat den light01" if command == "ON" else "Da tat den light01"
        return aiocoap.Message(code=aiocoap.CHANGED, payload=message.encode("utf-8"))


async def main(host):
    site = resource.Site()
    site.add_resource(("iot", "lab", "light01", "status"), LightResource())
    context = await aiocoap.Context.create_server_context(site, bind=(host, 5683))
    print(f"CoAP Smart Light Server started on {host}:5683\nResource: /iot/lab/light01/status", flush=True)
    try:
        await asyncio.Future()
    finally:
        await context.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bai 3 smart light server")
    parser.add_argument("--host", default="127.0.0.1", help="Local IP address to bind")
    try:
        asyncio.run(main(parser.parse_args().host))
    except KeyboardInterrupt:
        print("Server stopped")
