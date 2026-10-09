import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import os from 'os';

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const PORT = 9224;

async function run() {
  const tmpProfile = fs.mkdtempSync(path.join(os.tmpdir(), 'chrome-modes-'));
  const chrome = spawn(CHROME_PATH, [
    `--remote-debugging-port=${PORT}`,
    '--remote-allow-origins=*',
    '--headless=new',
    '--disable-gpu',
    '--no-first-run',
    '--no-default-browser-check',
    `--user-data-dir=${tmpProfile}`
  ]);

  await new Promise((r) => setTimeout(r, 2000));
  const newTab = await (await fetch(`http://127.0.0.1:${PORT}/json/new`, { method: 'PUT' })).json();
  const ws = new WebSocket(newTab.webSocketDebuggerUrl);

  let id = 1;
  const send = (method, params = {}) =>
    new Promise((resolve) => {
      const curId = id++;
      const handler = (ev) => {
        const d = JSON.parse(ev.data);
        if (d.id === curId) {
          ws.removeEventListener('message', handler);
          resolve(d.result);
        }
      };
      ws.addEventListener('message', handler);
      ws.send(JSON.stringify({ id: curId, method, params }));
    });

  await new Promise((r) => (ws.onopen = r));
  await send('Page.enable');

  // Mobile viewport 390x844
  await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });

  // 1. Capture Light mode (Kesari)
  await send('Page.navigate', { url: 'http://localhost:5173/?theme=kesari' });
  await new Promise((r) => setTimeout(r, 2000));
  let shot = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync('screenshots/home-light-kesari.png', Buffer.from(shot.data, 'base64'));
  console.log('Saved screenshots/home-light-kesari.png');

  // 2. Capture Dark mode (Chai & Clay)
  await send('Page.navigate', { url: 'http://localhost:5173/?theme=clay' });
  await new Promise((r) => setTimeout(r, 2000));
  shot = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync('screenshots/home-dark-clay.png', Buffer.from(shot.data, 'base64'));
  console.log('Saved screenshots/home-dark-clay.png');

  // 3. Capture Dark mode Journey
  await send('Page.navigate', { url: 'http://localhost:5173/journey?theme=clay' });
  await new Promise((r) => setTimeout(r, 2000));
  shot = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync('screenshots/journey-dark-clay.png', Buffer.from(shot.data, 'base64'));
  console.log('Saved screenshots/journey-dark-clay.png');

  ws.close();
  chrome.kill();
  try {
    fs.rmSync(tmpProfile, { recursive: true, force: true });
  } catch (e) {}
}

run();
