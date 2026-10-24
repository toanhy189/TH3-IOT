"""Bai 3: interactive light controller."""

import argparse
import asyncio
import json

import aiocoap


async def main(uri):
    context = await aiocoap.Context.create_client_context()
    try:
        while True:
            try:
                command = (await asyncio.to_thread(input, "Nhap lenh (ON/OFF/STATUS/EXIT): ")).strip().upper()
            except EOFError:
                break
            if command == "EXIT":
                break
            if command not in ("ON", "OFF", "STATUS"):
                print("Lenh khong hop le. Chon ON, OFF, STATUS hoac EXIT.")
                continue

            if command == "STATUS":
                print("Sending GET request...")
                request = aiocoap.Message(code=aiocoap.GET, uri=uri)
            else:
                print("Sending PUT request...")
                payload = json.dumps({"device_id": "light01", "command": command}).encode("utf-8")
                request = aiocoap.Message(code=aiocoap.PUT, uri=uri, payload=payload, content_format=50)
            try:
                response = await asyncio.wait_for(context.request(request).response, timeout=10)
                print(f"Response Code: {response.code}\n{response.payload.decode('utf-8')}")
            except (asyncio.TimeoutError, aiocoap.error.Error, OSError) as exc:
                print(f"CoAP request failed: {exc}")
    finally:
        await context.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bai 3 smart light controller")
    parser.add_argument("--uri", default="coap://127.0.0.1:5683/iot/lab/light01/status")
    try:
        asyncio.run(main(parser.parse_args().uri))
    except KeyboardInterrupt:
        print("Controller stopped")
