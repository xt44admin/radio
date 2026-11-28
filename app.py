import asyncio
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
app = FastAPI()
STREAM_URL = "http://79.111.14:8000/beatdown"
clients = set()
ffmpeg_task = None
async def broadcast():
 global ffmpeg_task
 cmd = ["ffmpeg", "-user_agent", "VLC/3.0.18", "-reconnect", "1", "-reconnect_streamed", "1", "-reconnect_delay_max", "5", "-i", STREAM_URL, "-vn", "-c:a", "libmp3lame", "-b:a", "64k", "-q:a", "5", "-ar", "44100", "-ac", "2", "-f", "mp3", "pipe:1"]
 proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE)
 try:
  while clients:
   chunk = await proc.stdout.read(2048)
   if not chunk: break
   for q in list(clients):
    if q.full(): q.get_nowait()
    q.put_nowait(chunk)
 finally:
  try: proc.kill()
  except ProcessLookupError: pass
  await proc.wait()
  ffmpeg_task = None
@app.get("/")
def health(): return {"listeners": len(clients)}
@app.head("/{name}.mp3")
def head_stream(name: str):
 return Response(media_type="audio/mpeg", headers={"Cache-Control": "no-store", "icy-name": "Beatdown Radio", "icy-br": "64"})
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
 return StreamingResponse(sender(), media_type="audio/mpeg", headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no", "icy-name": "Beatdown Radio", "icy-br": "64"})
