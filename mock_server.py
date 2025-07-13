import asyncio
import websockets
import os
import json

DATA_DIR = "data"

def load_available_chunks():
    chunk_ids = []
    for f in os.listdir(DATA_DIR):
        if f.endswith(".txt"):
            base = f.replace(".txt", "")
            if os.path.exists(os.path.join(DATA_DIR, f"{base}.mp3")):
                chunk_ids.append(base)
    return sorted(chunk_ids)

async def send_chunk(ws, chunk_id: str):
    text_path = os.path.join(DATA_DIR, f"{chunk_id}.txt")
    audio_path = os.path.join(DATA_DIR, f"{chunk_id}.mp3")

    with open(text_path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    with open(audio_path, "rb") as f:
        audio = f.read()

    # 1. Send text JSON frame
    await ws.send(json.dumps({
        "chunkId": int(chunk_id),
        "text": text
    }))

    # 2. Simulate a short delay
    await asyncio.sleep(0.2)

    # 3. Send audio binary frame
    await ws.send(audio)

async def handler(ws):  # Removed 'path' parameter
    print("[+] Client connected")

    chunk_ids = load_available_chunks()
    chunk_index = 0

    try:
        async for message in ws:
            print(f"[>] Received: {message}")

            if chunk_index >= len(chunk_ids):
                print("[!] No more chunks")
                await ws.close()
                break

            chunk_id = chunk_ids[chunk_index]
            await send_chunk(ws, chunk_id)
            chunk_index += 1

    except websockets.ConnectionClosed:
        print("[-] Client disconnected")

async def main():
    async with websockets.serve(handler, "0.0.0.0", 9001):  # Changed port to 9001
        print("🚀 WebSocket server running at ws://localhost:9001")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
