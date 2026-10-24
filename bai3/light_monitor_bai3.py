"""Bai 3: receive CoAP Observe notifications, without GET polling."""

import argparse
import asyncio
from datetime import datetime
import json

import aiocoap


def show_status(response, title):
    data = json.loads(response.payload.decode("utf-8"))
    print(f"[{datetime.now():%H:%M:%S}] {title}")
    print(f"Device: {data['device_id']}\nStatus: {data['status']}\n", flush=True)


async def main(uri):
    context = await aiocoap.Context.create_client_context()
    observation = None
    try:
        print("Registering CoAP Observe...", flush=True)
        request = aiocoap.Message(code=aiocoap.GET, uri=uri, observe=0)
        pending = context.request(request)
        initial = await asyncio.wait_for(pending.response, timeout=10)
        if not initial.code.is_successful() or pending.observation is None:
            raise RuntimeError(f"Observe registration failed: {initial.code}")
        observation = pending.observation
        print("Observe registration successful", flush=True)
        show_status(initial, "Initial State")
        async for notification in observation:
            show_status(notification, "State Updated")
    except (asyncio.TimeoutError, aiocoap.error.Error, OSError, ValueError, KeyError, RuntimeError) as exc:
        print(f"Observe failed: {exc}")
        raise SystemExit(1) from exc
    finally:
        if observation is not None:
            observation.cancel()
        await context.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bai 3 smart light monitor")
    parser.add_argument("--uri", default="coap://127.0.0.1:5683/iot/lab/light01/status")
    try:
        asyncio.run(main(parser.parse_args().uri))
    except KeyboardInterrupt:
        print("Monitoring stopped")
