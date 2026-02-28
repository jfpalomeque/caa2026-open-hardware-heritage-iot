#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>

// =============================
// AI Thinker ESP32-CAM pin map
// =============================
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// Flash LED on AI Thinker ESP32-CAM
#define FLASH_GPIO_NUM     4

// =============================
// WiFi Access Point
// =============================
const char* ssid = "ESP32_CAM_DEMO";
const char* password = "12345678";

WebServer server(80);

// =============================
// HTML GUI
// =============================
static const char PROGMEM INDEX_HTML[] = R"HTML(
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ESP32-CAM Demo</title>
  <style>
    :root { color-scheme: light; }
    body {
      margin: 0; padding: 0;
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
      background: #0b1020; color: #e9eefc;
    }
    .wrap { max-width: 980px; margin: 0 auto; padding: 16px; }
    .card {
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.10);
      border-radius: 16px;
      padding: 14px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.25);
    }
    h1 { font-size: 18px; margin: 0 0 12px 0; font-weight: 650; letter-spacing: 0.2px; }
    .grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 12px;
    }
    @media (min-width: 860px) {
      .grid { grid-template-columns: 2fr 1fr; }
    }
    .video {
      width: 100%;
      aspect-ratio: 4 / 3;
      border-radius: 14px;
      border: 1px solid rgba(255,255,255,0.10);
      background: #050814;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
    }
    .video img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      display: block;
    }
    .badge {
      position: absolute;
      left: 12px; top: 12px;
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(0,0,0,0.45);
      border: 1px solid rgba(255,255,255,0.10);
      font-size: 12px;
    }
    .controls { display: grid; gap: 10px; }
    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .btn {
      padding: 10px 12px;
      border-radius: 12px;
      border: 1px solid rgba(255,255,255,0.12);
      background: rgba(255,255,255,0.10);
      color: #e9eefc;
      font-weight: 600;
      cursor: pointer;
      user-select: none;
      transition: transform 0.04s ease, background 0.15s ease;
    }
    .btn:active { transform: scale(0.98); }
    .btn.primary { background: rgba(93,165,255,0.28); border-color: rgba(93,165,255,0.45); }
    .btn.danger  { background: rgba(255,93,93,0.22); border-color: rgba(255,93,93,0.40); }
    .btn.good    { background: rgba(110,255,170,0.18); border-color: rgba(110,255,170,0.35); }

    label { font-size: 12px; opacity: 0.9; margin-bottom: 6px; display: block; }
    select, input[type="range"] {
      width: 100%;
      padding: 10px 10px;
      border-radius: 12px;
      border: 1px solid rgba(255,255,255,0.12);
      background: rgba(255,255,255,0.08);
      color: #e9eefc;
      outline: none;
    }
    .kv { display: flex; justify-content: space-between; font-size: 12px; opacity: 0.9; margin-top: 6px; }
    .foot {
      margin-top: 10px;
      font-size: 12px;
      opacity: 0.75;
      line-height: 1.3;
    }
    a { color: #9cc7ff; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>ESP32-CAM Live Demo (no router needed)</h1>

      <div class="grid">
        <div class="video">
          <div class="badge" id="status">Stopped</div>
          <img id="stream" alt="stream preview" src="">
        </div>

        <div class="controls">
          <div class="row">
            <button class="btn primary" id="btnStart">Start</button>
            <button class="btn danger" id="btnStop">Stop</button>
          </div>

          <div class="row">
            <button class="btn good" id="btnSnap">Snapshot</button>
            <button class="btn" id="btnFlash">Flash: Off</button>
          </div>

          <div>
            <label for="res">Resolution</label>
            <select id="res">
              <option value="10">UXGA (1600x1200)</option>
              <option value="8">SVGA (800x600)</option>
              <option value="6" selected>VGA (640x480)</option>
              <option value="5">QVGA (320x240)</option>
            </select>
          </div>

          <div>
            <label for="q">JPEG Quality (lower is better quality, bigger files)</label>
            <input id="q" type="range" min="10" max="63" value="12">
            <div class="kv"><span>Quality</span><span id="qv">12</span></div>
          </div>

          <button class="btn" id="btnApply">Apply settings</button>

          <div class="foot">
            Tips: If the stream is slow, use QVGA and raise quality number.
            Snapshot downloads a JPEG. Flash helps indoors.
          </div>
        </div>
      </div>
    </div>
  </div>

<script>
  const streamImg = document.getElementById("stream");
  const statusEl = document.getElementById("status");
  const q = document.getElementById("q");
  const qv = document.getElementById("qv");
  const res = document.getElementById("res");
  const btnFlash = document.getElementById("btnFlash");

  let running = false;
  let flashOn = false;

  function setStatus(txt) { statusEl.textContent = txt; }

  function startStream() {
    if (running) return;
    running = true;
    setStatus("Streaming");
    streamImg.src = "/stream?ts=" + Date.now();
  }

  function stopStream() {
    running = false;
    streamImg.src = "";
    setStatus("Stopped");
  }

  async function applySettings() {
    const r = res.value;
    const quality = q.value;
    setStatus("Applying...");
    try {
      await fetch(`/set?framesize=${encodeURIComponent(r)}&quality=${encodeURIComponent(quality)}`, { cache: "no-store" });
      setStatus(running ? "Streaming" : "Stopped");
      if (running) {
        // force refresh stream connection
        streamImg.src = "";
        setTimeout(() => streamImg.src = "/stream?ts=" + Date.now(), 200);
      }
    } catch (e) {
      setStatus("Error");
    }
  }

  async function snapshot() {
    setStatus("Snapshot...");
    const url = "/capture?ts=" + Date.now();
    // Use an <a> download to save on phones and laptops
    const a = document.createElement("a");
    a.href = url;
    a.download = "esp32cam.jpg";
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => setStatus(running ? "Streaming" : "Stopped"), 600);
  }

  async function toggleFlash() {
    flashOn = !flashOn;
    btnFlash.textContent = "Flash: " + (flashOn ? "On" : "Off");
    try {
      await fetch(`/flash?on=${flashOn ? 1 : 0}`, { cache: "no-store" });
    } catch (e) {}
  }

  q.addEventListener("input", () => qv.textContent = q.value);

  document.getElementById("btnStart").onclick = startStream;
  document.getElementById("btnStop").onclick = stopStream;
  document.getElementById("btnApply").onclick = applySettings;
  document.getElementById("btnSnap").onclick = snapshot;
  btnFlash.onclick = toggleFlash;

  // nice default
  qv.textContent = q.value;
</script>
</body>
</html>
)HTML";

// =============================
// Helpers
// =============================
bool setFramesize(int fs) {
  sensor_t* s = esp_camera_sensor_get();
  if (!s) return false;
  // framesize_t enum values: QVGA=5, VGA=6, SVGA=8, UXGA=10 etc
  return (s->set_framesize(s, (framesize_t)fs) == 0);
}

bool setQuality(int q) {
  sensor_t* s = esp_camera_sensor_get();
  if (!s) return false;
  // quality: 10..63 (lower is better)
  return (s->set_quality(s, q) == 0);
}

// =============================
// Routes
// =============================
void handleRoot() {
  server.send_P(200, "text/html", INDEX_HTML);
}

void handleFlash() {
  if (!server.hasArg("on")) {
    server.send(400, "text/plain", "missing on");
    return;
  }
  int on = server.arg("on").toInt();
  digitalWrite(FLASH_GPIO_NUM, on ? HIGH : LOW);
  server.send(200, "text/plain", on ? "on" : "off");
}

void handleSet() {
  bool ok = true;

  if (server.hasArg("framesize")) {
    int fs = server.arg("framesize").toInt();
    ok = ok && setFramesize(fs);
  }
  if (server.hasArg("quality")) {
    int q = server.arg("quality").toInt();
    if (q < 10) q = 10;
    if (q > 63) q = 63;
    ok = ok && setQuality(q);
  }

  server.send(ok ? 200 : 500, "text/plain", ok ? "ok" : "fail");
}

void handleCapture() {
  camera_fb_t* fb = esp_camera_fb_get();
  if (!fb) {
    server.send(500, "text/plain", "capture failed");
    return;
  }
  server.sendHeader("Content-Disposition", "inline; filename=capture.jpg");
  server.send_P(200, "image/jpeg", (const char*)fb->buf, fb->len);
  esp_camera_fb_return(fb);
}

void handleStream() {
  WiFiClient client = server.client();

  server.sendContent(
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: multipart/x-mixed-replace; boundary=frame\r\n\r\n"
  );

  while (client.connected()) {
    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) {
      break;
    }

    server.sendContent("--frame\r\n");
    server.sendContent("Content-Type: image/jpeg\r\n\r\n");
    client.write(fb->buf, fb->len);
    server.sendContent("\r\n");

    esp_camera_fb_return(fb);

    delay(80); // smoother vs bandwidth, tweak if needed
  }
}

// =============================
// Setup / Loop
// =============================
void setup() {
  Serial.begin(115200);
  Serial.println();

  pinMode(FLASH_GPIO_NUM, OUTPUT);
  digitalWrite(FLASH_GPIO_NUM, LOW);

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;

  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  if (psramFound()) {
    config.frame_size = FRAMESIZE_VGA;
    config.jpeg_quality = 12;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_QVGA;
    config.jpeg_quality = 14;
    config.fb_count = 1;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed, error 0x%x\n", err);
    return;
  }

  WiFi.softAP(ssid, password);
  IPAddress ip = WiFi.softAPIP();

  Serial.println("AP started");
  Serial.print("SSID: "); Serial.println(ssid);
  Serial.print("PASS: "); Serial.println(password);
  Serial.print("Open: http://"); Serial.println(ip);

  server.on("/", handleRoot);
  server.on("/stream", HTTP_GET, handleStream);
  server.on("/capture", HTTP_GET, handleCapture);
  server.on("/flash", HTTP_GET, handleFlash);
  server.on("/set", HTTP_GET, handleSet);

  server.begin();
}

void loop() {
  server.handleClient();
}