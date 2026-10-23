from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/")
def index():
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Virtual Mouse & Keyboard</title>
<style>body{font-family:system-ui,sans-serif;max-width:820px;margin:48px auto;padding:0 20px;color:#18212f;background:#f5f7fb}main{background:white;border:1px solid #dce3ed;border-radius:16px;padding:28px}h1{margin-top:0}code{background:#eef2f8;padding:3px 6px;border-radius:5px}.ok{color:#137547;font-weight:700}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}.tile{background:#f5f7fb;padding:14px;border-radius:10px}</style></head>
<body><main><h1>Virtual Mouse &amp; Keyboard</h1>
<p>Hand-gesture control using computer vision — academic project deployment check.</p>
<p class="ok">● Web service is running</p><div class="grid">
<div class="tile"><b>Original application</b><p><code>hand.py</code> + <code>track.py</code></p></div>
<div class="tile"><b>Gesture features</b><p>Mouse movement, left/right/double click, screenshots and virtual keyboard.</p></div>
<div class="tile"><b>Deployment</b><p>Container health/status endpoint for Jenkins and Kubernetes verification.</p></div></div>
<p><b>Important:</b> The interactive gesture app requires a desktop webcam and GUI. Run <code>python hand.py</code> locally on a supported desktop to use it.</p>
<p>Health endpoint: <a href="/health">/health</a></p></main></body></html>"""

@app.get("/health")
def health():
    return jsonify(status="ok", application="virtual-mouse-keyboard"), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
