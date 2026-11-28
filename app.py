import asyncio
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
app = FastAPI()
clients = set()
task = None
async def broadcast():
 global task
 cmd = ["ffmpeg", "-fflags", "nobuffer", "-flags", "low_delay", "-probesize", "32768", "-analyzeduration", "0", "-i", "https://freeradio.wasmer.app/radcap.php", "-vn", "-c:a", "libmp3lame", "-b:a", "64k", "-q:a", "5", "-ar", "44100", "-ac", "2", "-f", "mp3", "pipe:1"]
 p = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE)
 try:
  while clients:
   chunk = await p.stdout.read(1024)
   if not chunk: break
   for q in list(clients):
    if q.full(): q.get_nowait()
    q.put_nowait(chunk)
 finally:
  try: p.kill()
  except ProcessLookupError: pass
  await p.wait()
  task = None
@app.api_route("/", methods=["GET", "HEAD"])
def home(): return {"listeners": len(clients)}
@app.head("/{name}.mp3")
def head(name: str): return Response(media_type="audio/mpeg")
@app.get("/{name}.mp3")
async def stream(name: str):
 global task
 q = asyncio.Queue(maxsize=16)
 clients.add(q)
 if task is None: task = asyncio.create_task(broadcast())
 async def gen():
  try:
   while True: yield await q.get()
  finally: clients.discard(q)
 return StreamingResponse(gen(), media_type="audio/mpeg", headers={"Cache-Control": "no-store"})
