import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import os from 'os';

const HTML = `
<!DOCTYPE html>
<html>
<head>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=DM+Serif+Display&family=Fraunces:ital,opsz,wght,SOFT,WONK@0,9..144,100..900,0..100,0..1&display=swap" rel="stylesheet">
<style>
body { background: #FBF6EC; color: #3B2A1A; padding: 40px; font-size: 32px; }
.box { margin-bottom: 30px; border-bottom: 1px solid #ccc; padding-bottom: 10px; }
.f-default { font-family: 'Fraunces', serif; font-weight: 700; }
.f-wonk0 { font-family: 'Fraunces', serif; font-weight: 700; font-variation-settings: 'WONK' 0, 'opsz' 36; }
.f-cormorant { font-family: 'Cormorant Garamond', serif; font-weight: 700; }
.f-dm { font-family: 'DM Serif Display', serif; }
</style>
</head>
<body>
<div class="box"><div class="label" style="font-size:16px;">1. Fraunces Default:</div><div class="f-default">The Journey</div></div>
<div class="box"><div class="label" style="font-size:16px;">2. Fraunces WONK 0 opsz 36:</div><div class="f-wonk0">The Journey</div></div>
<div class="box"><div class="label" style="font-size:16px;">3. Cormorant Garamond:</div><div class="f-cormorant">The Journey</div></div>
<div class="box"><div class="label" style="font-size:16px;">4. DM Serif Display:</div><div class="f-dm">The Journey</div></div>
</body>
</html>
`;

async function test() {
  fs.writeFileSync('temp-font-test.html', HTML);
  const tmpProfile = fs.mkdtempSync(path.join(os.tmpdir(), 'chrome-font-'));
  const chrome = spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', [
    '--remote-debugging-port=9225',
    '--remote-allow-origins=*',
    '--headless=new',
    '--disable-gpu',
    `--user-data-dir=${tmpProfile}`
  ]);
  await new Promise(r => setTimeout(r, 2000));
  const newTab = await (await fetch('http://127.0.0.1:9225/json/new', { method: 'PUT' })).json();
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
  await send('Page.navigate', { url: 'file:///' + path.resolve('temp-font-test.html').replace(/\\/g, '/') });
  await new Promise(r => setTimeout(r, 2000));
  const shot = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync('screenshots/font-test.png', Buffer.from(shot.data, 'base64'));
  ws.close();
  chrome.kill();
  try { fs.rmSync(tmpProfile, { recursive: true, force: true }); } catch (e) {}
  try { fs.unlinkSync('temp-font-test.html'); } catch (e) {}
  console.log('Saved screenshots/font-test.png');
}
test();
