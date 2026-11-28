import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
app = FastAPI()
STREAM_URL = "http://79.111.14.76:8000/beatdown".strip()
clients = set()
ffmpeg_task = None
async def broadcast():
 global ffmpeg_task
 cmd = ["ffmpeg", "-reconnect", "1", "-reconnect_streamed", "1", "-reconnect_delay_max", "5", "-i", STREAM_URL, "-vn", "-c:a", "libmp3lame", "-b:a", "64k", "-q:a", "5", "-ar", "44100", "-ac", "2", "-f", "mp3", "pipe:1"]
 proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
 try:
  while clients:
   chunk = await proc.stdout.read(2048)
   if not chunk: break
   for q in list(clients):
    if q.full(): q.get_nowait()
    q.put_nowait(chunk)
 finally:
  proc.kill()
  await proc.wait()
  ffmpeg_task = None
@app.get("/")
def health(): return {"listeners": len(clients)}
@app.get("/{name}.mp3")
async def stream(name: str):
 global ffmpeg_task
 q = asyncio.Queue(maxsize=16)
 clients.add(q)
 if ffmpeg_task is None: ffmpeg_task = asyncio.create_task(broadcast())
 async def sender():
  try:
   while True: yield await q.get()
  finally: clients.discard(q)
 return StreamingResponse(sender(), media_type="audio/mpeg", headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"})
