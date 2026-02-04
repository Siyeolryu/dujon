/**
 * API 통신 모듈 - 모든 API 호출 관리
 * CONFIG, UI 전역 객체 사용 (config.js, ui.js 로드 후)
 */
const API = {
    // #region agent log - 백엔드-프론트 연결 문제 확인용
    _logConnectionProblem(payload) {
        const { url, method, status, errorCode, message, request_id } = payload;
        const line = '[FE↔BE] url=' + url + ' method=' + method + ' status=' + status + ' code=' + (errorCode || '') + ' msg=' + (message || '') + ' request_id=' + (request_id || '');
        
        // 개발 환경에서만 콘솔 로그 출력
        const isDevelopment = typeof window !== 'undefined' && 
            (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
        
        if (isDevelopment && typeof console !== 'undefined' && console.warn) {
            console.warn(line);
        }
        
        // 보안: 프로덕션 환경에서는 외부 서버로 로그 전송하지 않음
        // 개발 환경에서만 디버깅 로그 전송 (선택적)
        if (isDevelopment) {
            try {
                fetch('http://127.0.0.1:7242/ingest/2aca0e8f-d16b-480b-8f72-96be3c2a5d6c', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        location: 'api.js:request',
                        message: 'API connection problem',
                        data: { url, method, status, errorCode, message, request_id },
                        timestamp: Date.now(),
                        sessionId: 'fe-be-connection',
                        hypothesisId: 'connection-fail',
                    }),
                }).catch(function() {});
            } catch (e) {
                // 무시 (디버깅 서버가 없어도 앱 동작에 영향 없음)
            }
        }
    },
    // #endregion

    async request(endpoint, options = {}) {
        const url = endpoint.startsWith('http') ? endpoint : `${CONFIG.API_BASE_URL}${endpoint}`;
        const method = (options.method || 'GET').toUpperCase();
        UI.showLoading();
        try {
            const res = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...(options.headers || {}),
                },
            });
            const json = await res.json().catch(() => ({}));
            UI.hideLoading();
            if (!res.ok) {
                const errorCode = json?.error?.code || '';
                const msg = json?.error?.message || res.statusText || '요청 실패';
                const request_id = json?.error?.request_id || '';
                this._logConnectionProblem({ url, method, status: res.status, errorCode, message: msg, request_id });
                if (res.status === 409) {
                    UI.showToast(msg, 'error');
                    if (typeof App !== 'undefined' && typeof App.loadAll === 'function') {
                        setTimeout(() => App.loadAll(), 800);
                    }
                } else {
                    UI.showToast(msg, 'error');
                }
                return null;
            }
            if (json.success === false) {
                const errorCode = json?.error?.code || '';
                const msg = json?.error?.message || '처리 실패';
                const request_id = json?.error?.request_id || '';
                this._logConnectionProblem({ url, method, status: 200, errorCode, message: msg, request_id });
                UI.showToast(msg, 'error');
                return null;
            }
            return json;
        } catch (err) {
            UI.hideLoading();
            const message = err.message || '네트워크 오류';
            this._logConnectionProblem({ url, method, status: 0, errorCode: 'NETWORK', message, request_id: '' });
            UI.showToast(message, 'error');
            return null;
        }
    },

    // === 현장 (Sites) ===
    async getSites(filters = {}) {
        const params = new URLSearchParams();
        if (filters.company) params.set('company', filters.company);
        if (filters.status) params.set('status', filters.status);
        if (filters.state) params.set('state', filters.state);
        const qs = params.toString();
        const res = await this.request(`/sites${qs ? '?' + qs : ''}`);
        return res ? { data: res.data || [], count: res.count ?? 0 } : null;
    },

    async searchSites(query) {
        if (!(query && String(query).trim())) {
            return this.getSites({});
        }
        const res = await this.request(`/sites/search?q=${encodeURIComponent(query.trim())}`);
        return res ? { data: res.data || [], count: res.count ?? 0 } : null;
    },

    async getSiteDetail(siteId) {
        const res = await this.request(`/sites/${encodeURIComponent(siteId)}`);
        return res?.data || null;
    },

    async createSite(siteData) {
        return await this.request('/sites', { method: 'POST', body: JSON.stringify(siteData) });
    },

    async updateSite(siteId, updateData) {
        const headers = {};
        if (updateData.version) {
            headers['If-Match'] = updateData.version;
        }
        return await this.request(`/sites/${encodeURIComponent(siteId)}`, {
            method: 'PUT',
            headers,
            body: JSON.stringify(updateData),
        });
    },

    async assignManager(siteId, assignData) {
        const body = {};
        if (assignData.담당소장ID) body.manager_id = assignData.담당소장ID;
        if (assignData.사용자격증ID) body.certificate_id = assignData.사용자격증ID;
        if (assignData.version) body.version = assignData.version;
        const headers = {};
        if (assignData.version) headers['If-Match'] = assignData.version;
        return await this.request(`/sites/${encodeURIComponent(siteId)}/assign`, {
            method: 'POST',
            headers,
            body: JSON.stringify(body),
        });
    },

    async unassignManager(siteId, version) {
        const body = version ? { version } : {};
        const headers = version ? { 'If-Match': version } : {};
        return await this.request(`/sites/${encodeURIComponent(siteId)}/unassign`, {
            method: 'POST',
            headers,
            body: JSON.stringify(body),
        });
    },

    // === 인력 (Personnel) ===
    async getPersonnel(filters = {}) {
        const params = new URLSearchParams();
        if (filters.status) params.set('status', filters.status);
        if (filters.role) params.set('role', filters.role);
        const qs = params.toString();
        const res = await this.request(`/personnel${qs ? '?' + qs : ''}`);
        return res ? { data: res.data || [], count: res.count ?? 0 } : null;
    },

    async getPersonnelDetail(personId) {
        const res = await this.request(`/personnel/${encodeURIComponent(personId)}`);
        return res?.data || null;
    },

    // === 자격증 (Certificates) ===
    async getCertificates(filters = {}) {
        const params = new URLSearchParams();
        if (filters.available === true || filters.available === 'true') params.set('available', 'true');
        if (filters.available === false || filters.available === 'false') params.set('available', 'false');
        const qs = params.toString();
        const res = await this.request(`/certificates${qs ? '?' + qs : ''}`);
        return res ? { data: res.data || [], count: res.count ?? 0 } : null;
    },

    async getCertificateDetail(certId) {
        const res = await this.request(`/certificates/${encodeURIComponent(certId)}`);
        return res?.data || null;
    },

    async createCertificate(certData) {
        return await this.request('/certificates', {
            method: 'POST',
            body: JSON.stringify(certData),
        });
    },

    async updateCertificate(certId, updateData) {
        return await this.request(`/certificates/${encodeURIComponent(certId)}`, {
            method: 'PUT',
            body: JSON.stringify(updateData),
        });
    },

    // === 통계 ===
    async getStats() {
        const res = await this.request('/stats');
        return res?.data || null;
    },

    // === 헬스 체크 ===
    async healthCheck() {
        try {
            const res = await fetch(`${CONFIG.API_BASE_URL}/health`);
            const json = await res.json().catch(() => ({}));
            return json.status === 'healthy' || json.status === 'ok';
        } catch {
            return false;
        }
    },
};

// API 라우터: CONFIG.API_MODE에 따라 Flask API 또는 Supabase 직접 연결 사용
// 사용법: DataAPI.getSites(), DataAPI.getPersonnel() 등
const DataAPI = new Proxy({}, {
    get(target, prop) {
        // API_MODE가 'supabase'이고 SupabaseAPI가 있으면 Supabase 사용
        if (CONFIG.API_MODE === 'supabase' && typeof SupabaseAPI !== 'undefined') {
            if (typeof SupabaseAPI[prop] === 'function') {
                return SupabaseAPI[prop].bind(SupabaseAPI);
            }
        }
        // 그 외에는 Flask API 사용
        if (typeof API[prop] === 'function') {
            return API[prop].bind(API);
        }
        return undefined;
    }
});
