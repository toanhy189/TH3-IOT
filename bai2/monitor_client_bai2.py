"""Bai 2: periodically query the sensor and report warnings."""

import argparse
import asyncio
from datetime import datetime
import json

import aiocoap


def show_reading(data):
    print(f"[{datetime.now():%H:%M:%S}] Received sensor data\n")
    print(f"Device: {data['device_id']}")
    print(f"Temperature: {data['temperature']} C")
    print(f"Humidity: {data['humidity']} %\n")
    warnings = []
    if data["temperature"] > 35:
        warnings.append("CANH BAO: Nhiet do cao")
    if data["humidity"] < 40:
        warnings.append("CANH BAO: Do am thap")
    print("\n".join(warnings) if warnings else "Trang thai: Binh thuong")
    print("\n" + "-" * 30 + "\n")


async def main(args):
    context = await aiocoap.Context.create_client_context()
    try:
        count = 0
        while args.count is None or count < args.count:
            try:
                request = aiocoap.Message(code=aiocoap.GET, uri=args.uri)
                response = await asyncio.wait_for(context.request(request).response, timeout=10)
                if not response.code.is_successful():
                    print(f"Server returned: {response.code}")
                else:
                    if response.opt.content_format != 50:
                        raise ValueError("Expected application/json response")
                    show_reading(json.loads(response.payload.decode("utf-8")))
            except (asyncio.TimeoutError, aiocoap.error.Error, OSError, ValueError, KeyError) as exc:
                print(f"Sensor request failed: {exc}")
            count += 1
            if args.count is None or count < args.count:
                await asyncio.sleep(3)
    finally:
        await context.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bai 2 sensor monitor")
    parser.add_argument("--uri", default="coap://127.0.0.1:5683/iot/lab/sensor01/data")
    parser.add_argument("--count", type=int, help="Stop after this many requests (default: Ctrl+C)")
    try:
        asyncio.run(main(parser.parse_args()))
    except KeyboardInterrupt:
        print("Monitoring stopped")
