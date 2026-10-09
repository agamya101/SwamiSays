import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import os from 'os';

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const PORT = 9222;
const OUT_DIR = path.resolve('screenshots');

if (!fs.existsSync(OUT_DIR)) {
  fs.mkdirSync(OUT_DIR, { recursive: true });
}

function delay(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function waitForChrome(port, maxTries = 20) {
  for (let i = 0; i < maxTries; i++) {
    try {
      const res = await fetch(`http://127.0.0.1:${port}/json/version`);
      if (res.ok) {
        const data = await res.json();
        return data.webSocketDebuggerUrl;
      }
    } catch (e) {}
    await delay(300);
  }
  throw new Error('Chrome remote debugging did not respond in time.');
}

async function run() {
  const tmpProfile = fs.mkdtempSync(path.join(os.tmpdir(), 'chrome-shot-'));
  console.log(`Using temp profile: ${tmpProfile}`);

  const chrome = spawn(CHROME_PATH, [
    `--remote-debugging-port=${PORT}`,
    '--remote-allow-origins=*',
    '--headless=new',
    '--disable-gpu',
    '--no-first-run',
    '--no-default-browser-check',
    `--user-data-dir=${tmpProfile}`
  ]);

  try {
    await waitForChrome(PORT);

    // Create target page via PUT
    const targetRes = await fetch(`http://127.0.0.1:${PORT}/json/new`, { method: 'PUT' });
    const target = await targetRes.json();
    const wsUrl = target.webSocketDebuggerUrl;

    const ws = new WebSocket(wsUrl);
    let msgId = 1;
    const pending = new Map();

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.id && pending.has(data.id)) {
        const { resolve, reject } = pending.get(data.id);
        pending.delete(data.id);
        if (data.error) reject(data.error);
        else resolve(data.result);
      }
    };

    await new Promise((r) => (ws.onopen = r));

    function send(method, params = {}) {
      const id = msgId++;
      return new Promise((resolve, reject) => {
        pending.set(id, { resolve, reject });
        ws.send(JSON.stringify({ id, method, params }));
      });
    }

    await send('Page.enable');

    // Warmup
    await send('Page.navigate', { url: 'http://localhost:5173/compare' });
    await delay(2000);

    const tasks = [
      { name: 'compare-1280', url: 'http://localhost:5173/compare', width: 1280, height: 950, waitMs: 4000 },
      { name: 'compare-390', url: 'http://localhost:5173/compare', width: 390, height: 844, waitMs: 2500 },
      { name: 'home-kesari-390', url: 'http://localhost:5173/?theme=kesari&embed=1', width: 390, height: 844, waitMs: 1500 },
      { name: 'home-clay-390', url: 'http://localhost:5173/?theme=clay&embed=1', width: 390, height: 844, waitMs: 1500 },
      { name: 'home-indigo-390', url: 'http://localhost:5173/?theme=indigo&embed=1', width: 390, height: 844, waitMs: 1500 },
      { name: 'journey-wheel-390', url: 'http://localhost:5173/journey?theme=kesari&embed=1', width: 390, height: 844, waitMs: 1500 },
      { name: 'journey-wheel-1280', url: 'http://localhost:5173/journey?theme=kesari&embed=1', width: 1280, height: 850, waitMs: 1500 },
      { name: 'lesson-390', url: 'http://localhost:5173/journey/3?theme=kesari&embed=1', width: 390, height: 844, waitMs: 1500 },
      { name: 'episode-390', url: 'http://localhost:5173/journey/3/1?theme=kesari&embed=1', width: 390, height: 844, waitMs: 1500 },
      { name: 'sos-input-390', url: 'http://localhost:5173/sos?theme=kesari&embed=1', width: 390, height: 844, waitMs: 1500 },
      { name: 'sos-result-390', url: 'http://localhost:5173/sos/result?theme=kesari&embed=1', width: 390, height: 844, waitMs: 4500 }
    ];

    for (const task of tasks) {
      console.log(`Capturing ${task.name}...`);
      await send('Emulation.setDeviceMetricsOverride', {
        width: task.width,
        height: task.height,
        deviceScaleFactor: 1,
        mobile: task.width < 500
      });

      await send('Page.navigate', { url: task.url });
      await delay(task.waitMs || 1500);

      const shot = await send('Page.captureScreenshot', { format: 'png' });
      const buffer = Buffer.from(shot.data, 'base64');
      const filePath = path.join(OUT_DIR, `${task.name}.png`);
      fs.writeFileSync(filePath, buffer);
      console.log(`Saved: ${filePath}`);
    }

    ws.close();
  } catch (err) {
    console.error('Error during capture:', err);
  } finally {
    chrome.kill();
    try {
      fs.rmSync(tmpProfile, { recursive: true, force: true });
    } catch (e) {}
  }
}

run();
