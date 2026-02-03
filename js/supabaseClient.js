/**
 * Supabase 브라우저 클라이언트
 * 프로젝트: hhpofxpnztzibtpkpiar
 */

// Supabase 설정 - 브라우저에서 사용 가능한 anon key
const SUPABASE_URL = 'https://hhpofxpnztzibtpkpiar.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhocG9meHBuenR6aWJ0cGtwaWFyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc2MDc2NjgsImV4cCI6MjA4MzE4MzY2OH0.qYgw_6KlgPZrQPvLs0IJKb-HRZaWMJxiKv0H4izysAs';

// Supabase 클라이언트 생성 (CDN 또는 번들러 환경 둘 다 지원)
let supabase;

if (typeof window !== 'undefined' && window.supabase) {
    // CDN으로 로드된 경우 (supabase-js UMD)
    supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
} else if (typeof require !== 'undefined') {
    // CommonJS (Node 등)
    try {
        const { createClient } = require('@supabase/supabase-js');
        supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
    } catch (e) {
        console.warn('Supabase JS SDK를 찾을 수 없습니다. CDN 또는 npm install @supabase/supabase-js 필요.');
    }
}

// ES Module export (번들러용)
// export { supabase, SUPABASE_URL, SUPABASE_ANON_KEY };

// 전역 노출 (CDN/브라우저용)
if (typeof window !== 'undefined') {
    window.SUPABASE_URL = SUPABASE_URL;
    window.SUPABASE_ANON_KEY = SUPABASE_ANON_KEY;
    window.supabaseClient = supabase;
}
