"""End-to-end checks over local UDP for the three CoAP resources."""

import asyncio
import json
import unittest

import aiocoap
from aiocoap import resource

from bai1.coap_server_bai1 import MessageResource
from bai2.sensor_server_bai2 import SensorResource, update_sensor
from bai3.light_server_bai3 import LightResource


BASE = "coap://127.0.0.1:5683"


class CoAPIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        asyncio.get_running_loop().slow_callback_duration = 1.0
        self.client = await aiocoap.Context.create_client_context()
        self.server = None

    async def asyncTearDown(self):
        await self.client.shutdown()
        if self.server is not None:
            await self.server.shutdown()

    async def start_server(self, path, implementation):
        site = resource.Site()
        site.add_resource(path, implementation)
        self.server = await aiocoap.Context.create_server_context(site, bind=("127.0.0.1", 5683))

    async def request(self, code, path, payload=b"", content_format=None):
        options = {"content_format": content_format} if content_format is not None else {}
        message = aiocoap.Message(code=code, uri=BASE + path, payload=payload, **options)
        return await asyncio.wait_for(self.client.request(message).response, timeout=3)

    async def test_bai1_get_post_and_latest_message(self):
        await self.start_server(("iot", "lab", "message"), MessageResource())
        path = "/iot/lab/message"
        initial = await self.request(aiocoap.GET, path)
        self.assertEqual(initial.code, aiocoap.CONTENT)
        self.assertEqual(initial.payload.decode(), "Xin chao tu CoAP Server")

        message = "Xin chao tu CoAP Client - B23DCCN834 - Phạm Khánh Toàn"
        posted = await self.request(aiocoap.POST, path, message.encode("utf-8"))
        self.assertEqual(posted.code, aiocoap.CHANGED)
        self.assertEqual((await self.request(aiocoap.GET, path)).payload.decode("utf-8"), message)
        self.assertEqual((await self.request(aiocoap.POST, path)).code, aiocoap.BAD_REQUEST)

    async def test_bai2_sensor_json_and_refresh(self):
        sensor = SensorResource()
        await self.start_server(("iot", "lab", "sensor01", "data"), sensor)
        path = "/iot/lab/sensor01/data"
        first = await self.request(aiocoap.GET, path)
        self.assertEqual(first.code, aiocoap.CONTENT)
        self.assertEqual(first.opt.content_format, 50)
        data = json.loads(first.payload)
        self.assertEqual(data["device_id"], "sensor01")
        self.assertTrue(20 <= data["temperature"] <= 40)
        self.assertTrue(30 <= data["humidity"] <= 80)

        task = asyncio.create_task(update_sensor(sensor))
        try:
            await asyncio.sleep(3.2)
            self.assertNotEqual(sensor.data, data)
            later = await self.request(aiocoap.GET, path)
            self.assertEqual(json.loads(later.payload), sensor.data)
        finally:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    async def test_bai3_get_put_and_observe_two_clients(self):
        await self.start_server(("iot", "lab", "light01", "status"), LightResource())
        path = "/iot/lab/light01/status"
        observers = []
        try:
            for _ in range(2):
                pending = self.client.request(aiocoap.Message(code=aiocoap.GET, uri=BASE + path, observe=0))
                initial = await asyncio.wait_for(pending.response, timeout=3)
                self.assertEqual(json.loads(initial.payload)["status"], "OFF")
                self.assertIsNotNone(pending.observation)
                observers.append(pending.observation)

            put = await self.request(
                aiocoap.PUT,
                path,
                json.dumps({"device_id": "light01", "command": "ON"}).encode(),
                50,
            )
            self.assertEqual(put.code, aiocoap.CHANGED)
            for observation in observers:
                notification = await asyncio.wait_for(anext(aiter(observation)), timeout=3)
                self.assertEqual(json.loads(notification.payload)["status"], "ON")

            self.assertEqual(json.loads((await self.request(aiocoap.GET, path)).payload)["status"], "ON")
            bad = await self.request(
                aiocoap.PUT,
                path,
                json.dumps({"device_id": "light01", "command": "BLINK"}).encode(),
                50,
            )
            self.assertEqual(bad.code, aiocoap.BAD_REQUEST)
        finally:
            for observation in observers:
                observation.cancel()


if __name__ == "__main__":
    unittest.main()
