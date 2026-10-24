"""Bai 1: send GET and POST to the message resource."""

import argparse
import asyncio

import aiocoap


async def send(context, method, uri, payload=b""):
    request = aiocoap.Message(code=method, uri=uri, payload=payload)
    return await asyncio.wait_for(context.request(request).response, timeout=10)


async def main(args):
    context = await aiocoap.Context.create_client_context()
    try:
        print("CoAP Client\nSending GET request...\nURI:", args.uri)
        response = await send(context, aiocoap.GET, args.uri)
        print(f"\nResponse:\nCode: {response.code}\nPayload: {response.payload.decode('utf-8')}")

        payload = f"{args.message} - {args.student_id} - {args.name}"
        print(f"\nSending POST request...\nPayload: {payload}")
        response = await send(context, aiocoap.POST, args.uri, payload.encode("utf-8"))
        print(f"\nResponse:\nCode: {response.code}\nPayload: {response.payload.decode('utf-8')}")
    except (asyncio.TimeoutError, aiocoap.error.Error, OSError) as exc:
        print(f"CoAP request failed: {exc}")
        raise SystemExit(1) from exc
    finally:
        await context.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bai 1 CoAP client")
    parser.add_argument("--name", required=True, help="Student's full name")
    parser.add_argument("--student-id", required=True, help="Student ID")
    parser.add_argument("--message", default="Xin chao tu CoAP Client")
    parser.add_argument("--uri", default="coap://127.0.0.1:5683/iot/lab/message")
    asyncio.run(main(parser.parse_args()))
