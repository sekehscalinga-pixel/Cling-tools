
from flask import Flask, request, jsonify, Response, send_file
from yt_dlp import YoutubeDL
from urllib.parse import urlparse
from html import escape
import os, uuid

app = Flask(__name__)

BASE = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

HTML = r"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CLING TOOLS</title>
<style>
*{box-sizing:border-box}
body{
 margin:0;background:#080a0e;color:#e9fff5;
 font-family:Arial,sans-serif;
 background-image:radial-gradient(ellipse at top,#123328,#080a0e 65%);
 min-height:100vh
}
header{text-align:center;padding:28px 12px 20px}
.logo{
 font-size:30px;font-weight:900;color:#00ff9d;
 letter-spacing:2px;text-shadow:0 0 15px #00ff9d
}
.subtitle{font-size:11px;color:#879b92;letter-spacing:4px;margin-top:8px}
.wrap{max-width:760px;margin:auto;padding:14px}
.nav{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:18px}
.nav button{
 flex:1;min-width:100px;padding:12px 8px;border-radius:10px;
 color:#00ff9d;background:#111820;border:1px solid #00ff9d;
 font-weight:bold
}
.card{
 border:1px solid #263b33;background:#0e1418;
 border-radius:16px;padding:18px;margin-bottom:15px;
 box-shadow:0 0 18px #00ff9d08
}
h2{color:#00ff9d;font-size:18px;margin-top:0}
input,select{
 width:100%;padding:13px;margin:8px 0;
 background:#080c10;color:white;border:1px solid #31423c;
 border-radius:10px;font-size:14px
}
.btn{
 width:100%;padding:13px;margin-top:8px;
 background:#00ff9d;color:#07110b;border:0;
 border-radius:10px;font-weight:bold
}
.btn2{background:#bd78ff;color:#100819}
.note{font-size:12px;color:#8b9c95;line-height:1.6}
.output{margin-top:15px;word-break:break-word;color:#00ff9d}
a{color:#00ff9d}
.hidden{display:none}
footer{text-align:center;color:#5d7168;font-size:11px;padding:25px}
</style>
</head>
<body>
<header>
 <div class="logo">CLING TOOLS</div>
 <div class="subtitle">MULTI TOOL WEB</div>
</header>

<div class="wrap">
 <div class="nav">
  <button onclick="openTab('brat')">BRAT</button>
  <button onclick="openTab('video')">VIDEO</button>
  <button onclick="openTab('skip')">SKIP LINK</button>
 </div>

 <section class="card" id="brat">
  <h2>BRAT GENERATOR</h2>
  <input id="bratText" maxlength="80" placeholder="Masukkan teks...">
  <button class="btn" onclick="makeBrat()">GENERATE BRAT</button>
  <div id="bratOut" class="output"></div>
 </section>

 <section class="card hidden" id="video">
  <h2>VIDEO DOWNLOADER</h2>
  <input id="videoUrl" placeholder="Masukkan link TikTok">
  <select id="quality">
   <option value="480">480p</option>
   <option value="720">720p HD</option>
   <option value="1080">1080p Full HD</option>
   <option value="2160">2160p UHD / 4K</option>
  </select>
  <button class="btn" onclick="downloadVideo()">DOWNLOAD</button>
  <div class="output" id="videoOut"></div>
  <p class="note">Gunakan hanya video yang kamu miliki atau diizinkan untuk diunduh. Kualitas bergantung pada sumber.</p>
 </section>

 <section class="card hidden" id="skip">
  <h2>SKIP LINK / LINK OPENER</h2>
  <input id="skipUrl" placeholder="https://contoh.com">
  <button class="btn btn2" onclick="openDestination()">OPEN LINK</button>
  <div id="skipOut" class="output"></div>
  <p class="note">Membuka URL yang dimasukkan. Tidak menghapus verifikasi, iklan, atau proteksi safelink.</p>
 </section>
</div>
<footer>CLING TOOLS • PYTHON EDITION</footer>

<script>
function openTab(id){
 ['brat','video','skip'].forEach(x=>{
  document.getElementById(x).classList.add('hidden');
 });
 document.getElementById(id).classList.remove('hidden');
}

async function makeBrat(){
 const text=document.getElementById('bratText').value.trim();
 const out=document.getElementById('bratOut');
 if(!text){out.textContent='Isi teks terlebih dahulu';return;}
 out.textContent='Membuat gambar...';
 try{
  const res=await fetch('/brat?text='+encodeURIComponent(text));
  if(!res.ok)throw new Error('Gagal');
  const blob=await res.blob();
  const url=URL.createObjectURL(blob);
  out.replaceChildren();
  const img=document.createElement('img');
  img.src=url;img.style.cssText='width:100%;max-width:500px;border-radius:8px';
  const a=document.createElement('a');
  a.href=url;a.download='cling-brat.svg';
  a.textContent='DOWNLOAD IMAGE';
  a.style.display='block';a.style.marginTop='12px';
  out.append(img,a);
 }catch(e){out.textContent='Gagal membuat gambar';}
}

async function downloadVideo(){
 const url=document.getElementById('videoUrl').value.trim();
 const quality=document.getElementById('quality').value;
 const out=document.getElementById('videoOut');
 if(!url){out.textContent='Masukkan URL terlebih dahulu';return;}
 out.textContent='Sedang memproses video...';
 try{
  const res=await fetch('/download',{
   method:'POST',headers:{'Content-Type':'application/json'},
   body:JSON.stringify({url:url,quality:quality})
  });
  const data=await res.json();
  if(!res.ok)throw new Error(data.error||'Download gagal');
  out.replaceChildren();
  const a=document.createElement('a');
  a.href=data.file;a.textContent='DOWNLOAD FILE';
  out.appendChild(a);
 }catch(e){out.textContent=e.message;}
}

function openDestination(){
 const input=document.getElementById('skipUrl').value.trim();
 const out=document.getElementById('skipOut');
 out.replaceChildren();
 try{
  const u=new URL(input);
  if(!['http:','https:'].includes(u.protocol))throw new Error();
  const a=document.createElement('a');
  a.href=u.href;a.target='_blank';a.rel='noopener noreferrer';
  a.textContent='OPEN DESTINATION';
  const p=document.createElement('p');
  p.textContent='Link siap dibuka';
  out.append(p,a);
 }catch(e){
  out.textContent='URL tidak valid. Gunakan link http atau https.';
 }
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return Response(HTML, mimetype="text/html")

@app.route("/brat")
def brat():
    text = request.args.get("text", "")[:80]
    if not text:
        return "Teks kosong", 400

    safe = escape(text)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800">
    <rect width="100%" height="100%" fill="#8aff80"/>
    <foreignObject x="35" y="35" width="730" height="730">
    <div xmlns="http://www.w3.org/1999/xhtml"
      style="width:730px;height:730px;display:flex;align-items:center;
      justify-content:center;text-align:center;font-family:Arial,sans-serif;
      font-size:100px;font-weight:900;line-height:0.95;color:black;
      overflow-wrap:anywhere;">{safe}</div>
    </foreignObject></svg>"""

    return Response(svg, mimetype="image/svg+xml")

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "").strip()
    try:
        quality = int(data.get("quality", 720))
    except (ValueError, TypeError):
        quality = 720

    allowed = (480, 720, 1080, 2160)
    if quality not in allowed:
        quality = 720

    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        if parsed.scheme not in ("http", "https") or not (
            host == "tiktok.com" or host.endswith(".tiktok.com")
        ):
            return jsonify(error="Masukkan URL TikTok yang valid"), 400

        filename = uuid.uuid4().hex
        opts = {
            "format": f"best[height<={quality}]/best",
            "outtmpl": os.path.join(DOWNLOAD_DIR, filename + ".%(ext)s"),
            "noplaylist": True,
            "quiet": True,
        }
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)

        if not os.path.isfile(filepath):
            return jsonify(error="File hasil tidak ditemukan"), 500

        return jsonify(file="/files/" + os.path.basename(filepath))
    except Exception as e:
        return jsonify(error="Gagal mengunduh video. Periksa link dan coba lagi."), 500

@app.route("/files/<name>")
def serve_file(name):
    safe_name = os.path.basename(name)
    path = os.path.join(DOWNLOAD_DIR, safe_name)
    if not os.path.isfile(path):
        return "File tidak ditemukan", 404
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    print("CLING TOOLS berjalan di http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000)

