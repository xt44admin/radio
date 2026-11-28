import subprocess
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
app = FastAPI()
@app.api_route("/", methods=["GET", "HEAD"])
def home(): return {"status": "ok"}
@app.head("/{name}.mp3")
def head(name: str): return Response(media_type="audio/mpeg")
@app.get("/{name}.mp3")
def stream(name: str):
 cmd = ["ffmpeg", "-i", "https://freeradio.wasmer.app/radcap.php", "-vn", "-c:a", "libmp3lame", "-b:a", "64k", "-q:a", "5", "-ar", "44100", "-ac", "2", "-f", "mp3", "pipe:1"]
 p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
 def gen():
  try:
   while chunk := p.stdout.read(4096): yield chunk
  finally: p.kill()
 return StreamingResponse(gen(), media_type="audio/mpeg", headers={"Cache-Control": "no-store"})
