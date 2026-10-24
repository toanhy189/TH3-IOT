"""Bai 2: simulated temperature and humidity sensor."""

import argparse
import asyncio
import json
import random

import aiocoap
from aiocoap import resource


class SensorResource(resource.Resource):
    def __init__(self):
        super().__init__()
        self.data = self.new_reading()

    @staticmethod
    def new_reading():
        return {
            "device_id": "sensor01",
            "temperature": round(random.uniform(20, 40), 1),
            "humidity": round(random.uniform(30, 80), 1),
        }

    async def render_get(self, request):
        print(f"GET /iot/lab/sensor01/data: {self.data}", flush=True)
        return aiocoap.Message(
            code=aiocoap.CONTENT,
            payload=json.dumps(self.data).encode("utf-8"),
            content_format=50,  # application/json
        )


async def update_sensor(sensor):
    while True:
        await asyncio.sleep(3)
        sensor.data = sensor.new_reading()
        print(f"Sensor updated: {sensor.data}", flush=True)


async def main(host):
    sensor = SensorResource()
    site = resource.Site()
    site.add_resource(("iot", "lab", "sensor01", "data"), sensor)
    context = await aiocoap.Context.create_server_context(site, bind=(host, 5683))
    update_task = asyncio.create_task(update_sensor(sensor))
    print(f"Sensor CoAP Server started on {host}:5683", flush=True)
    try:
        await asyncio.Future()
    finally:
        update_task.cancel()
        await asyncio.gather(update_task, return_exceptions=True)
        await context.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bai 2 sensor server")
    parser.add_argument("--host", default="127.0.0.1", help="Local IP address to bind")
    try:
        asyncio.run(main(parser.parse_args().host))
    except KeyboardInterrupt:
        print("Server stopped")
