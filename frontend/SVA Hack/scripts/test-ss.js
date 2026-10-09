import fs from 'fs';
import { spawn } from 'child_process';
import os from 'os';
import path from 'path';

let html = `<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,700&display=swap" rel="stylesheet">
<style>body { font-family: 'Fraunces', serif; font-size: 28px; padding: 20px; }</style>
</head><body>
`;

for (let i = 1; i <= 6; i++) {
  const ss = 'ss0' + i;
  html += `<div style="font-feature-settings: '${ss}' 1;">${ss}: The Journey</div>`;
}

html += '</body></html>';
fs.writeFileSync('temp-ss.html', html);

async function check() {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'chrome-ss-'));
  const chrome = spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', [
    '--remote-debugging-port=9226',
    '--remote-allow-origins=*',
    '--headless=new',
    '--disable-gpu',
    `--user-data-dir=${tmp}`
  ]);
  await new Promise(r => setTimeout(r, 2000));
  const newTab = await (await fetch('http://127.0.0.1:9226/json/new', { method: 'PUT' })).json();
  const ws = new WebSocket(newTab.webSocketDebuggerUrl);
  let id = 1;
  const send = (method, params = {}) =>
    new Promise(res => {
      const curId = id++;
      const handler = ev => {
        const d = JSON.parse(ev.data);
        if (d.id === curId) { ws.removeEventListener('message', handler); res(d.result); }
      };
      ws.addEventListener('message', handler);
      ws.send(JSON.stringify({ id: curId, method, params }));
    });
  await new Promise(r => (ws.onopen = r));
  await send('Page.enable');
  await send('Page.navigate', { url: 'file:///' + path.resolve('temp-ss.html').replace(/\\/g, '/') });
  await new Promise(r => setTimeout(r, 2000));
  const shot = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync('screenshots/ss-test.png', Buffer.from(shot.data, 'base64'));
  ws.close();
  chrome.kill();
  try { fs.rmSync(tmp, { recursive: true, force: true }); } catch (e) {}
  try { fs.unlinkSync('temp-ss.html'); } catch (e) {}
  console.log('Saved screenshots/ss-test.png');
}
check();
