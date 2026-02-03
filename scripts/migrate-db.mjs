/**
 * Node로 Supabase에 마이그레이션 SQL 적용
 * 사용: node scripts/migrate-db.mjs
 */
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import pg from 'pg';

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, '..');

// .env 간단 파싱 (DATABASE_URL만)
function loadEnv() {
  const path = join(root, '.env');
  try {
    const text = readFileSync(path, 'utf8');
    for (const line of text.split('\n')) {
      const m = line.match(/^\s*DATABASE_URL\s*=\s*(.+)\s*$/);
      if (m) return m[1].trim().replace(/^["']|["']$/g, '');
    }
  } catch (_) {}
  return process.env.DATABASE_URL;
}

const databaseUrl = loadEnv();
if (!databaseUrl) {
  console.error('오류: .env에 DATABASE_URL이 없습니다.');
  process.exit(1);
}

const sqlPath = join(root, 'supabase', 'migrations', '001_initial_tables.sql');
const sql = readFileSync(sqlPath, 'utf8');

const client = new pg.Client({ connectionString: databaseUrl });

async function main() {
  try {
    await client.connect();
    await client.query(sql);
    console.log('마이그레이션 적용 완료: sites, personnel, certificates 테이블 및 RLS 정책 생성됨.');
  } catch (e) {
    if (/already exists/.test(e.message)) {
      console.log('테이블 또는 정책이 이미 존재합니다. 스키마는 적용된 상태일 수 있습니다.');
      console.log('상세:', e.message);
    } else {
      console.error('마이그레이션 실패:', e.message);
      process.exit(1);
    }
  } finally {
    await client.end();
  }
}

main();
