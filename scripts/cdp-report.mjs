/**
 * Auditoría y Generador de Reporte con Chrome Remote Debugging Protocol (CDP).
 *
 * Demuestra paso a paso cómo conectar con Chrome vía --remote-debugging-port=9222,
 * habilitar los dominios Page, Network, Runtime, Log y Performance, inspeccionar
 * el frontend conectado al backend local, ejecutar flujos interactivos, capturar
 * pantallas y generar reportes JSON + Markdown.
 *
 * Uso:
 *   node back/scripts/cdp-report.mjs
 *   TARGET_URL=http://127.0.0.1:3000 CDP_PORT=9222 OUTPUT_DIR=... node back/scripts/cdp-report.mjs
 */

import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createAppServer } from '../server.mjs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const CDP_PORT = Number(process.env.CDP_PORT || 9222);
const OUTPUT_DIR = path.resolve(
  process.env.OUTPUT_DIR || path.join(__dirname, '..', 'reports')
);
const HEADLESS = process.env.CDP_HEADLESS !== 'false';

function findChromeBinary() {
  const candidates = [
    process.env.CHROME_PATH,
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    path.join(process.env.LOCALAPPDATA || '', 'Google\\Chrome\\Application\\chrome.exe'),
    'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
  ].filter(Boolean);

  for (const p of candidates) {
    if (fs.existsSync(p)) return p;
  }
  throw new Error('No se encontró Chrome/Edge instalado en el sistema.');
}

async function waitForCdpEndpoint(port, timeoutMs = 15000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const res = await fetch(`http://127.0.0.1:${port}/json/version`);
      if (res.ok) return await res.json();
    } catch {
      // esperar a que Chrome abra el puerto CDP
    }
    await new Promise((r) => setTimeout(r, 250));
  }
  throw new Error(`Timeout esperando Chrome Remote Debugging en puerto ${port}`);
}

class CdpClient {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.nextId = 1;
    this.pending = new Map();
    this.listeners = new Map();
    this.commandLog = [];
  }

  async connect() {
    await new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.wsUrl);
      this.ws.addEventListener('open', resolve);
      this.ws.addEventListener('error', (err) => reject(err));
      this.ws.addEventListener('message', (evt) => {
        const msg = JSON.parse(String(evt.data));
        if (msg.id && this.pending.has(msg.id)) {
          const { resolve: res, reject: rej } = this.pending.get(msg.id);
          this.pending.delete(msg.id);
          if (msg.error) rej(new Error(`CDP ${msg.error.message}`));
          else res(msg.result);
        } else if (msg.method) {
          const handlers = this.listeners.get(msg.method) || [];
          for (const h of handlers) h(msg.params);
        }
      });
    });
  }

  on(eventName, handler) {
    if (!this.listeners.has(eventName)) this.listeners.set(eventName, []);
    this.listeners.get(eventName).push(handler);
  }

  async send(method, params = {}) {
    const id = this.nextId++;
    const startedAt = Date.now();
    const result = await new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
    this.commandLog.push({
      id,
      method,
      duration_ms: Date.now() - startedAt,
      params_preview: Object.keys(params),
    });
    return result;
  }

  async evalJs(expression) {
    const res = await this.send('Runtime.evaluate', {
      expression,
      awaitPromise: true,
      returnByValue: true,
    });
    if (res.exceptionDetails) {
      throw new Error(res.exceptionDetails.text || 'Error en Runtime.evaluate');
    }
    return res.result?.value;
  }

  close() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.close();
    }
  }
}

async function auditPage(cdp, pageLabel, url, screenshotPath, interactionFn) {
  const requests = new Map();
  const consoleEntries = [];
  const exceptions = [];

  const onReq = (p) => {
    requests.set(p.requestId, {
      url: p.request.url,
      method: p.request.method,
      resourceType: p.type || 'Other',
      startTs: p.timestamp,
      status: null,
      mimeType: null,
      encodedBytes: 0,
      durationMs: null,
      failed: false,
      errorText: null,
    });
  };
  const onRes = (p) => {
    const rec = requests.get(p.requestId);
    if (rec) {
      rec.status = p.response.status;
      rec.mimeType = p.response.mimeType;
    }
  };
  const onFin = (p) => {
    const rec = requests.get(p.requestId);
    if (rec) {
      rec.encodedBytes = p.encodedDataLength || 0;
      rec.durationMs = Number(((p.timestamp - rec.startTs) * 1000).toFixed(1));
    }
  };
  const onFail = (p) => {
    const rec = requests.get(p.requestId);
    if (rec) {
      rec.failed = true;
      rec.errorText = p.errorText;
    }
  };
  const onConsole = (p) => {
    const text = (p.args || [])
      .map((a) => (a.value !== undefined ? String(a.value) : a.description || a.type))
      .join(' ');
    consoleEntries.push({ type: p.type, text });
  };
  const onExc = (p) => {
    exceptions.push({
      text: p.exceptionDetails?.text || 'Uncaught exception',
      description: p.exceptionDetails?.exception?.description || '',
    });
  };

  cdp.on('Network.requestWillBeSent', onReq);
  cdp.on('Network.responseReceived', onRes);
  cdp.on('Network.loadingFinished', onFin);
  cdp.on('Network.loadingFailed', onFail);
  cdp.on('Runtime.consoleAPICalled', onConsole);
  cdp.on('Runtime.exceptionThrown', onExc);

  const navStart = Date.now();
  await cdp.send('Page.navigate', { url });
  // Esperar carga completa de DOM, Chart.js y llamadas /api/*
  await new Promise((r) => setTimeout(r, 2200));

  const domAudit = await cdp.evalJs(`(() => {
    const canvases = [...document.querySelectorAll('canvas')].map(c => ({
      id: c.id || '(sin id)',
      width: c.width,
      height: c.height,
      visible: c.getBoundingClientRect().width > 0 && c.getBoundingClientRect().height > 0
    }));
    const badge = document.getElementById('apiStatusBadge')?.textContent?.trim() || null;
    const h1 = document.querySelector('h1')?.textContent?.trim() || document.title;
    return {
      title: document.title,
      h1,
      apiBadge: badge,
      totalCanvases: canvases.length,
      renderedCanvases: canvases.filter(c => c.width > 0 && c.height > 0).length,
      canvases
    };
  })()`);

  const interactionResult = interactionFn ? await interactionFn(cdp) : null;

  const perfRaw = await cdp.send('Performance.getMetrics');
  const perfMap = Object.fromEntries(perfRaw.metrics.map((m) => [m.name, m.value]));

  const shot = await cdp.send('Page.captureScreenshot', {
    format: 'png',
    fromSurface: true,
  });
  fs.writeFileSync(screenshotPath, Buffer.from(shot.data, 'base64'));

  // Desregistrar listeners de esta página
  cdp.listeners.clear();

  const networkList = [...requests.values()];
  return {
    pageLabel,
    url,
    totalWallMs: Date.now() - navStart,
    domAudit,
    interactionResult,
    consoleEntries,
    exceptions,
    network: networkList,
    performance: {
      JSHeapUsedMB: Number(((perfMap.JSHeapUsedSize || 0) / 1048576).toFixed(2)),
      Nodes: perfMap.Nodes || 0,
      LayoutCount: perfMap.LayoutCount || 0,
      ScriptDurationMs: Number(((perfMap.ScriptDuration || 0) * 1000).toFixed(1)),
      TaskDurationMs: Number(((perfMap.TaskDuration || 0) * 1000).toFixed(1)),
    },
    screenshotFile: path.basename(screenshotPath),
  };
}

async function main() {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });

  // 1. Levantar servidor local si no se pasa TARGET_URL externo
  let localServer = null;
  let baseUrl = process.env.TARGET_URL || '';
  let dataSource = 'external';

  if (!baseUrl) {
    const created = await createAppServer();
    localServer = created.server;
    dataSource = created.adapter.source;
    await new Promise((resolve) => localServer.listen(0, '127.0.0.1', resolve));
    const { port } = localServer.address();
    baseUrl = `http://127.0.0.1:${port}`;
  }

  const chromeBin = findChromeBinary();
  const userDataDir = fs.mkdtempSync(path.join(os.tmpdir(), 'autogest-cdp-'));
  const chromeArgs = [
    `--remote-debugging-port=${CDP_PORT}`,
    `--user-data-dir=${userDataDir}`,
    '--no-first-run',
    '--no-default-browser-check',
    '--window-size=1440,960',
    ...(HEADLESS ? ['--headless=new'] : []),
    'about:blank',
  ];

  console.log(`[CDP] Lanzando Chrome: ${chromeBin}`);
  console.log(`[CDP] Puerto remoto: http://127.0.0.1:${CDP_PORT}`);
  const chromeProc = spawn(chromeBin, chromeArgs, { stdio: 'ignore' });

  let cdp = null;
  try {
    const versionInfo = await waitForCdpEndpoint(CDP_PORT);
    const targetsRes = await fetch(`http://127.0.0.1:${CDP_PORT}/json/list`);
    const targets = await targetsRes.json();
    const pageTarget = targets.find((t) => t.type === 'page') || targets[0];
    if (!pageTarget?.webSocketDebuggerUrl) {
      throw new Error('No se encontró un target de tipo page con webSocketDebuggerUrl.');
    }

    cdp = new CdpClient(pageTarget.webSocketDebuggerUrl);
    await cdp.connect();

    // Habilitar dominios CDP
    await cdp.send('Page.enable');
    await cdp.send('Network.enable');
    await cdp.send('Runtime.enable');
    await cdp.send('Log.enable');
    await cdp.send('Performance.enable');
    await cdp.send('Emulation.setDeviceMetricsOverride', {
      width: 1440,
      height: 960,
      deviceScaleFactor: 1,
      mobile: false,
    });

    // Auditar Vista 1: Dashboard Principal (/)
    const dashReport = await auditPage(
      cdp,
      'Dashboard Principal (/)',
      `${baseUrl}/`,
      path.join(OUTPUT_DIR, 'cdp_dashboard.png'),
      async (client) => {
        // Probar filtro interactivo por tipo de vehículo y calculadora con persistencia en API
        const filterCheck = await client.evalJs(`(async () => {
          const sel = document.getElementById('filtroTipoVehiculo');
          if (!sel || !window.AutoGestAPI) return { ok: false, reason: 'Sin controles de filtro' };
          sel.value = 'LIVIANO';
          await window.AutoGestAPI.applyDashboardFilters();
          const filteredText = document.getElementById('kpiValAccidentes')?.textContent?.trim();
          await window.AutoGestAPI.resetDashboardFilters();
          const resetText = document.getElementById('kpiValAccidentes')?.textContent?.trim();

          // Probar pestaña Métodos Numéricos y calculadora
          if (typeof filtrarVista === 'function') filtrarVista('todo');
          const inp = document.getElementById('inputRL');
          if (inp) inp.value = '2028';
          if (typeof calcDashRL === 'function') await calcDashRL();
          await new Promise(r => setTimeout(r, 500));
          const historyRows = document.querySelectorAll('#tbodyHistorialPredicciones tr').length;
          return {
            ok: true,
            kpiFiltradoLiviano: filteredText,
            kpiRestauradoTodos: resetText,
            filasHistorialPredicciones: historyRows
          };
        })()`);

        // Capturar también vista de la Calculadora + Historial de Predicciones conectado a la API
        await client.evalJs(`(() => {
          const el = document.getElementById('inputRL')?.closest('.chart-card');
          if (el) el.scrollIntoView({ behavior: 'instant', block: 'start' });
        })()`);
        await new Promise((r) => setTimeout(r, 400));
        const shotMn = await client.send('Page.captureScreenshot', {
          format: 'png',
          fromSurface: true,
        });
        fs.writeFileSync(
          path.join(OUTPUT_DIR, 'cdp_dashboard_mn.png'),
          Buffer.from(shotMn.data, 'base64')
        );
        await client.evalJs('window.scrollTo(0, 0)');
        return filterCheck;
      }
    );

    // Auditar Vista 2: Métodos Numéricos (/metodos.html)
    const metodosReport = await auditPage(
      cdp,
      'Métodos Numéricos (/metodos.html)',
      `${baseUrl}/metodos.html`,
      path.join(OUTPUT_DIR, 'cdp_metodos.png'),
      async (client) => {
        const res = await client.evalJs(`(async () => {
          const inpLag = document.getElementById('inputLag');
          if (inpLag) inpLag.value = '2019';
          if (typeof calcLag === 'function') await calcLag(true);
          await new Promise(r => setTimeout(r, 500));
          const resLag = document.getElementById('resultLag')?.textContent?.trim() || '';
          const historyRows = document.querySelectorAll('#tbodyHistorialPredicciones tr').length;
          return {
            ok: resLag.includes('430'),
            resultadoLagrange2019: resLag,
            filasHistorialPredicciones: historyRows
          };
        })()`);

        // Capturar también la gráfica semestral renderizada en /metodos.html
        await client.evalJs(`(() => {
          const el = document.getElementById('chartRLSem')?.closest('.chart-wrap');
          if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
        })()`);
        await new Promise((r) => setTimeout(r, 400));
        const shotMetChart = await client.send('Page.captureScreenshot', {
          format: 'png',
          fromSurface: true,
        });
        fs.writeFileSync(
          path.join(OUTPUT_DIR, 'cdp_metodos_chart.png'),
          Buffer.from(shotMetChart.data, 'base64')
        );
        await client.evalJs('window.scrollTo(0, 0)');
        return res;
      }
    );

    const report = {
      generatedAt: new Date().toISOString(),
      targetBaseUrl: baseUrl,
      dataSource,
      chrome: {
        binary: chromeBin,
        browserVersion: versionInfo.Browser,
        protocolVersion: versionInfo['Protocol-Version'],
        v8Version: versionInfo['V8-Version'],
        remoteDebuggingPort: CDP_PORT,
        webSocketUrl: pageTarget.webSocketDebuggerUrl,
      },
      cdpCommandTrace: cdp.commandLog,
      pages: [dashReport, metodosReport],
    };

    const jsonPath = path.join(OUTPUT_DIR, 'cdp-report.json');
    fs.writeFileSync(jsonPath, JSON.stringify(report, null, 2), 'utf8');

    console.log(`[CDP] Reporte JSON guardado en: ${jsonPath}`);
    console.log(
      `[CDP] Resumen: ${report.pages
        .map(
          (p) =>
            `${p.pageLabel} -> canvases=${p.domAudit.renderedCanvases}/${p.domAudit.totalCanvases}, red=${p.network.length}, erroresJS=${p.exceptions.length}`
        )
        .join(' | ')}`
    );
  } finally {
    if (cdp) cdp.close();
    chromeProc.kill();
    if (localServer) {
      await new Promise((resolve) => localServer.close(resolve));
    }
    try {
      fs.rmSync(userDataDir, { recursive: true, force: true });
    } catch {
      // en Windows Chrome puede tardar unos ms en liberar el perfil temporal
    }
  }
}

main().catch((err) => {
  console.error('[CDP] Error fatal:', err);
  process.exit(1);
});
