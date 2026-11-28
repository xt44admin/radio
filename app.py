import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
app = FastAPI()
STREAM_URL = "http://79.111.14.76:8000/beatdown"
clients = set()
ffmpeg_task = None
async def broadcast():
 global ffmpeg_task
 cmd = ["ffmpeg", "-reconnect", "1", "-reconnect_streamed", "1", "-reconnect_delay_max", "5", "-i", STREAM_URL, "-vn", "-c:a", "aac", "-profile:a", "aac_low", "-b:a", "48k", "-ar", "44100", "-ac", "2", "-f", "adts", "pipe:1"]
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
@app.get("/beatdown.aac")
async def stream():
 global ffmpeg_task
 q = asyncio.Queue(maxsize=16)
 clients.add(q)
 if ffmpeg_task is None: ffmpeg_task = asyncio.create_task(broadcast())
 async def sender():
  try:
   while True: yield await q.get()
  finally: clients.discard(q)
 return StreamingResponse(sender(), media_type="audio/aac", headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"})
