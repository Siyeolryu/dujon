/**
 * 로컬 확인용 서버 (Node.js)
 * Python이 없을 때 프론트엔드 + API 목(mock) 서빙
 * 포트 5000, http://localhost:5000/
 */
import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PORT = 5000;
const ROOT = __dirname;

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.ico': 'image/x-icon',
};

function send(res, code, body, contentType) {
  const ct = contentType || 'application/json; charset=utf-8';
  res.writeHead(code, { 'Content-Type': ct, 'Access-Control-Allow-Origin': '*' });
  res.end(typeof body === 'string' ? body : JSON.stringify(body));
}

function apiHealth() {
  return { status: 'healthy', service: 'site-management-api', timestamp: new Date().toISOString() };
}
function apiStats() {
  return {
    success: true,
    data: {
      sites: { total: 0, assigned: 0, unassigned: 0, by_company: {}, by_state: {} },
      personnel: { total: 0, available: 0, deployed: 0, by_role: {} },
      certificates: { total: 0, available: 0, in_use: 0, expired: 0 },
    },
    timestamp: new Date().toISOString(),
  };
}
function apiEmptyList() {
  return { success: true, data: [], count: 0, timestamp: new Date().toISOString() };
}
function apiNotFound(code, message) {
  return { success: false, error: { code, message } };
}
function apiConfigRequired() {
  return { success: false, error: { code: 'CONFIG_REQUIRED', message: '실제 데이터/배정은 Python(Flask) 서버 + Google 시트 연동 후 사용하세요.' } };
}

function serveFile(filePath, res) {
  const ext = path.extname(filePath);
  const contentType = MIME[ext] || 'application/octet-stream';
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: { code: 'NOT_FOUND', message: 'Not Found' } }));
      return;
    }
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(data);
  });
}

function safePath(relative) {
  const normalized = path.normalize(relative).replace(/^(\.\.(\/|\\|$))+/, '');
  return path.resolve(ROOT, normalized);
}

const server = http.createServer((req, res) => {
  const pathname = (req.url || '/').split('?')[0];
  const pathLower = pathname.toLowerCase();

  if (pathLower.startsWith('/api/')) {
    if (pathLower === '/api/health') return send(res, 200, apiHealth());
    if (pathLower === '/api/stats') return send(res, 200, apiStats());
    if (pathLower === '/api/sites' && req.method === 'GET') return send(res, 200, apiEmptyList());
    if (pathLower === '/api/sites' && req.method === 'POST') return send(res, 503, apiConfigRequired());
    if (pathLower.startsWith('/api/sites/search') && req.method === 'GET') return send(res, 200, apiEmptyList());
    if (/^\/api\/sites\/[^/]+$/.test(pathLower) && req.method === 'GET') return send(res, 404, apiNotFound('NOT_FOUND', '현장을 찾을 수 없습니다'));
    if (/^\/api\/sites\/[^/]+\/assign$/.test(pathLower) && req.method === 'POST') return send(res, 400, apiConfigRequired());
    if (/^\/api\/sites\/[^/]+\/unassign$/.test(pathLower) && req.method === 'POST') return send(res, 400, apiConfigRequired());
    if (/^\/api\/sites\/[^/]+$/.test(pathLower) && req.method === 'PUT') return send(res, 400, apiConfigRequired());
    if (pathLower === '/api/personnel' && req.method === 'GET') return send(res, 200, apiEmptyList());
    if (/^\/api\/personnel\/[^/]+$/.test(pathLower) && req.method === 'GET') return send(res, 404, apiNotFound('PERSONNEL_NOT_FOUND', '인력을 찾을 수 없습니다'));
    if (pathLower === '/api/certificates' && req.method === 'GET') return send(res, 200, apiEmptyList());
    if (pathLower === '/api/certificates' && req.method === 'POST') return send(res, 503, apiConfigRequired());
    if (/^\/api\/certificates\/[^/]+$/.test(pathLower) && req.method === 'GET') return send(res, 404, apiNotFound('CERTIFICATE_NOT_FOUND', '자격증을 찾을 수 없습니다'));
    return send(res, 404, apiNotFound('NOT_FOUND', 'Not Found'));
  }

  if (pathname === '/' || pathname === '') {
    return serveFile(path.join(ROOT, 'site-management.html'), res);
  }
  const relative = pathname.replace(/^\//, '').replace(/\\/g, '/');
  const filePath = safePath(relative);
  const rootResolved = path.resolve(ROOT);
  if (filePath.indexOf(rootResolved) !== 0) {
    res.writeHead(403);
    res.end('Forbidden');
    return;
  }
  fs.stat(filePath, (err, stat) => {
    if (!err && stat.isFile()) return serveFile(filePath, res);
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ success: false, error: { code: 'NOT_FOUND', message: 'Not Found' } }));
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log('');
  console.log('====================================================');
  console.log('  현장배정 관리 시스템 (Node.js 로컬 서버)');
  console.log('====================================================');
  console.log('  프론트엔드: http://localhost:' + PORT + '/');
  console.log('  API 정보:   http://localhost:' + PORT + '/api-info');
  console.log('  헬스:       http://localhost:' + PORT + '/api/health');
  console.log('====================================================');
  console.log('  종료: Ctrl+C');
  console.log('');
});
