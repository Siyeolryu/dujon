// === API 설정 ===
// 배포 시: HTML에서 window.__API_BASE_URL__ 를 설정하면 해당 URL 사용 (4단계 배포 대응)
// 로컬: 같은 호스트에서 서빙 시 상대 경로 사용 (프론트·백 동일 포트)
const CONFIG = {
    // API 모드: 'supabase' (Supabase 직접 연결) 또는 'flask' (Flask 백엔드)
    API_MODE: 'supabase',

    // Flask 백엔드 URL (API_MODE='flask'일 때 사용)
    API_BASE_URL: (typeof window !== 'undefined' && window.__API_BASE_URL__)
        ? window.__API_BASE_URL__
        : (typeof window !== 'undefined' && window.location && window.location.origin
            ? window.location.origin + '/api'
            : 'http://localhost:5000/api'),

    // Supabase 설정 (API_MODE='supabase'일 때 사용)
    SUPABASE_URL: 'https://hhpofxpnztzibtpkpiar.supabase.co',
    SUPABASE_ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhocG9meHBuenR6aWJ0cGtwaWFyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc2MDc2NjgsImV4cCI6MjA4MzE4MzY2OH0.qYgw_6KlgPZrQPvLs0IJKb-HRZaWMJxiKv0H4izysAs',

    // 자동 새로고침 간격 (밀리초). 0이면 비활성
    AUTO_REFRESH_INTERVAL: 0,  // 60000 = 1분

    // Kakao Maps JavaScript 키 (카카오 개발자 콘솔에서 발급, 도메인 제한 권장)
    KAKAO_APP_KEY: '797d955e0a50c6f827d5bfe3ab6ee26e',

    // 지도 초기 설정
    MAP_CENTER: { lat: 37.0, lng: 127.0 },  // 경기도 중심
    MAP_ZOOM: 3  // 1~14, 작을수록 확대
};

// === 프론트 표시용 매핑 ===
const DISPLAY_MAP = {
    // 회사구분: API 값 → 화면 표시용
    company: {
        '더존종합건설': '종합건설',
        '더존하우징': '하우징'
    },
    // 역변환: 화면 값 → API 쿼리용
    companyReverse: {
        '종합건설': '더존종합건설',
        '하우징': '더존하우징',
        'all': ''
    },
    // 배정상태 색상 (파스텔/인디케이터)
    statusColor: {
        '배정완료': '#2e7d32',
        '미배정': '#c62828'
    },
    // 현장상태 색상 (세련된 파스텔)
    siteStatusColor: {
        '건축허가': '#1565c0',
        '착공예정': '#ef6c00',
        '착공중': '#d84315',
        '준공': '#2e7d32'
    },
    // 인력상태 색상
    personnelStatusColor: {
        '투입가능': '#27ae60',
        '투입중': '#f39c12',
        '휴가': '#95a5a6',
        '퇴사': '#e74c3c'
    }
};
