/**
 * 메인 앱 - 초기화, 데이터 로드, 이벤트 바인딩
 * 테이블(AG-Grid 스타일) + 스켈레톤 UI + 행 클릭 → 슬라이드 인 상세 패널
 */
function renderSkeletonList() {
    const container = document.getElementById('skeletonList');
    if (!container) return;
    const rows = 6;
    let html = '';
    for (let i = 0; i < rows; i++) {
        html += `
            <div class="skeleton-row">
                <div class="skeleton-block wide"></div>
                <div class="skeleton-block medium"></div>
                <div class="skeleton-block narrow"></div>
                <div class="skeleton-block medium"></div>
            </div>
        `;
    }
    container.innerHTML = html;
    container.classList.remove('hidden');
    container.removeAttribute('aria-hidden');
}

function hideSkeletonShowContent() {
    const skeleton = document.getElementById('skeletonList');
    const tableWrap = document.getElementById('siteTableWrap');
    const emptyEl = document.getElementById('siteListEmpty');
    if (skeleton) {
        skeleton.classList.add('hidden');
        skeleton.setAttribute('aria-hidden', 'true');
    }
    if (tableWrap) tableWrap.classList.add('hidden');
    if (emptyEl) emptyEl.classList.add('hidden');
}

function showTable() {
    const tableWrap = document.getElementById('siteTableWrap');
    const emptyEl = document.getElementById('siteListEmpty');
    if (tableWrap) tableWrap.classList.remove('hidden');
    if (emptyEl) emptyEl.classList.add('hidden');
}

function showEmpty(message) {
    const tableWrap = document.getElementById('siteTableWrap');
    const emptyEl = document.getElementById('siteListEmpty');
    if (tableWrap) tableWrap.classList.add('hidden');
    if (emptyEl) {
        emptyEl.textContent = message;
        emptyEl.classList.remove('hidden');
    }
}

function renderSiteTableRow(site, selectedId) {
    const id = site['현장ID'] || site.id || '';
    const name = site['현장명'] || site.name || '-';
    const companyApi = site['회사구분'] || site.company || '';
    const companyDisplay = DISPLAY_MAP.company[companyApi] || companyApi || '-';
    const status = site['배정상태'] || site.status || '미배정';
    const state = site['현장상태'] || site.siteStatus || '';
    const address = (site['주소'] || site.address || '').slice(0, 30);
    const managerName = site['담당소장명'] || site.manager || '';
    const certName = site['자격증명'] || site.certName || '';
    const statusColor = DISPLAY_MAP.statusColor[status] || '#95a5a6';
    const stateColor = DISPLAY_MAP.siteStatusColor[state] || '#95a5a6';
    const isUnassigned = status === '미배정';
    const rowClass = isUnassigned ? 'unassigned-row' : '';
    const selectedClass = selectedId === id ? ' selected' : '';
    const assignBtn = isUnassigned
        ? `<button type="button" class="assign-inline-btn" data-site-id="${id}">배정하기</button>`
        : '';
    return `<tr class="${rowClass}${selectedClass}" data-site-id="${id}">
        <td class="cell-name">${escapeHtml(name)}</td>
        <td><span class="cell-badge" style="background:${stateColor}">${escapeHtml(companyDisplay)}</span></td>
        <td><span class="cell-badge" style="background:${statusColor}">${escapeHtml(status)}</span></td>
        <td><span class="cell-badge" style="background:${stateColor}">${escapeHtml(state)}</span></td>
        <td class="cell-manager">${managerName ? escapeHtml(managerName) + (certName ? ' · ' + escapeHtml(certName) : '') : '—'}</td>
        <td class="cell-action">${assignBtn}</td>
    </tr>`;
}

function escapeHtml(s) {
    if (s == null) return '';
    const div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
}

function getSortedSites(sites) {
    if (!sites || !sites.length) return sites || [];
    const sortBy = document.getElementById('sortBy')?.value || 'name';
    const copy = [...sites];
    if (sortBy === 'name') {
        copy.sort((a, b) => (a['현장명'] || a.name || '').localeCompare(b['현장명'] || b.name || '', 'ko'));
    } else if (sortBy === 'status') {
        copy.sort((a, b) => (a['배정상태'] || a.status || '').localeCompare(b['배정상태'] || b.status || '', 'ko'));
    } else if (sortBy === 'state') {
        copy.sort((a, b) => (a['현장상태'] || a.siteStatus || '').localeCompare(b['현장상태'] || b.siteStatus || '', 'ko'));
    }
    return copy;
}

const App = {
    currentSites: [],

    async init() {
        if (CONFIG.DEBUG) {
            console.log('🚀 현장배정 관리 시스템 시작...');
            console.log('📡 API 모드:', CONFIG.API_MODE);
        }
        const healthy = await DataAPI.healthCheck();
        const statusEl = document.getElementById('serverStatus');
        if (statusEl) {
            statusEl.textContent = '';
            statusEl.className = 'status-indicator';
            statusEl.style.background = healthy ? '#c3e6cb' : '#f5c6cb';
        }
        if (!healthy) {
            UI.showToast('API 서버에 연결할 수 없습니다. 서버를 확인하세요.', 'error');
        }
        Filter.init();
        if (typeof Tabs !== 'undefined') Tabs.init();
        this.bindEvents();
        renderSkeletonList();
        await this.loadAll();
        if (CONFIG.AUTO_REFRESH_INTERVAL > 0) {
            setInterval(() => this.loadAll(), CONFIG.AUTO_REFRESH_INTERVAL);
        }
        const lastEl = document.getElementById('lastUpdated');
        if (lastEl) lastEl.textContent = new Date().toLocaleTimeString('ko-KR');
        if (CONFIG.DEBUG) console.log('✅ 초기화 완료');
    },

    async loadAll() {
        await Promise.all([this.loadSites(), Dashboard.load()]);
        const lastEl = document.getElementById('lastUpdated');
        if (lastEl) lastEl.textContent = new Date().toLocaleTimeString('ko-KR');
    },

    async loadSites() {
        const filters = Filter.currentFilters;
        const apiCompany = DISPLAY_MAP.companyReverse[filters.company] || '';
        const params = {};
        if (apiCompany) params.company = apiCompany;
        if (filters.status && filters.status !== 'all') params.status = filters.status;
        if (filters.state && filters.state !== 'all') params.state = filters.state;
        const result = await DataAPI.getSites(params);
        if (result) {
            this.renderSiteList(result.data);
            const countEl = document.getElementById('siteCount');
            if (countEl) countEl.textContent = result.count;
        } else {
            this.renderSiteList(null, true);
            const countEl = document.getElementById('siteCount');
            if (countEl) countEl.textContent = '-';
        }
    },

    renderSiteList(sites, apiFailed = false) {
        hideSkeletonShowContent();
        const tbody = document.getElementById('siteTableBody');
        this.currentSites = sites || [];
        const selectedId = SiteDetail.currentSite ? (SiteDetail.currentSite['현장ID'] || SiteDetail.currentSite.id) : null;

        if (!sites || sites.length === 0) {
            const msg = apiFailed
                ? '서버에 연결할 수 없습니다. API 서버를 확인하세요.'
                : '조건에 맞는 현장이 없습니다.';
            showEmpty(msg);
            return;
        }
        showTable();
        const sorted = getSortedSites(sites);
        if (tbody) {
            tbody.innerHTML = sorted.map((site) => renderSiteTableRow(site, selectedId)).join('');
            tbody.querySelectorAll('tr[data-site-id]').forEach((tr) => {
                const id = tr.dataset.siteId;
                tr.addEventListener('click', (e) => {
                    if (e.target.classList.contains('assign-inline-btn')) {
                        e.stopPropagation();
                        const s = sorted.find((x) => (x['현장ID'] || x.id) === id);
                        if (s) Assign.open(id, s['현장명'] || s.name, s['주소'] || s.address);
                    } else if (id) {
                        SiteDetail.open(id);
                        this.updateSelectedRow(id);
                    }
                });
            });
        }
    },

    updateSelectedRow(siteId) {
        const tbody = document.getElementById('siteTableBody');
        if (!tbody) return;
        tbody.querySelectorAll('tr.selected').forEach((r) => r.classList.remove('selected'));
        const row = tbody.querySelector(`tr[data-site-id="${siteId}"]`);
        if (row) row.classList.add('selected');
    },

    bindEvents() {
        document.getElementById('sortBy')?.addEventListener('change', () => {
            if (this.currentSites && this.currentSites.length) this.renderSiteList(this.currentSites);
        });
        document.getElementById('closeDetail')?.addEventListener('click', () => SiteDetail.close());
        document.getElementById('closeAssign')?.addEventListener('click', () => Assign.close());
        document.getElementById('btnCancelAssign')?.addEventListener('click', () => Assign.close());
        document.getElementById('btnConfirmAssign')?.addEventListener('click', () => Assign.confirm());
        document.getElementById('btnAssign')?.addEventListener('click', () => {
            const site = SiteDetail.currentSite;
            if (site) Assign.open(site['현장ID'], site['현장명'], site['주소']);
        });
        document.getElementById('btnUnassign')?.addEventListener('click', () => {
            const site = SiteDetail.currentSite;
            if (site) Assign.unassign(site['현장ID']);
        });
        document.getElementById('managerSelect')?.addEventListener('change', (e) => Assign.onManagerSelect(e.target.value));
        document.getElementById('certificateSelect')?.addEventListener('change', (e) => Assign.onCertSelect(e.target.value));

        document.getElementById('btnEditSite')?.addEventListener('click', () => this.openEditSiteModal());
        document.getElementById('editSiteCancel')?.addEventListener('click', () => this.closeEditSiteModal());
        document.getElementById('editSiteForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveEditSite();
        });
    },

    openEditSiteModal() {
        const site = SiteDetail.currentSite;
        if (!site) return;
        const overlay = document.getElementById('editSiteOverlay');
        if (!overlay) return;
        document.getElementById('editSiteId').value = site['현장ID'] || '';
        document.getElementById('editSiteName').value = site['현장명'] || '';
        document.getElementById('editAddress').value = site['주소'] || '';
        document.getElementById('editLat').value = site['위도'] ?? '';
        document.getElementById('editLng').value = site['경도'] ?? '';
        document.getElementById('editPermitDate').value = site['건축허가일'] || '';
        document.getElementById('editStartDate').value = site['착공예정일'] || '';
        document.getElementById('editCompletionDate').value = site['준공일'] || '';
        document.getElementById('editState').value = site['현장상태'] || '건축허가';
        document.getElementById('editNotes').value = site['특이사항'] || '';
        overlay.classList.remove('hidden');
    },

    closeEditSiteModal() {
        document.getElementById('editSiteOverlay')?.classList.add('hidden');
    },

    async saveEditSite() {
        const siteId = document.getElementById('editSiteId')?.value;
        if (!siteId) return;
        const updateData = {
            현장명: document.getElementById('editSiteName')?.value?.trim() || '',
            주소: document.getElementById('editAddress')?.value?.trim() || '',
            위도: document.getElementById('editLat')?.value?.trim() || '',
            경도: document.getElementById('editLng')?.value?.trim() || '',
            건축허가일: document.getElementById('editPermitDate')?.value?.trim() || '',
            착공예정일: document.getElementById('editStartDate')?.value?.trim() || '',
            준공일: document.getElementById('editCompletionDate')?.value?.trim() || '',
            현장상태: document.getElementById('editState')?.value || '건축허가',
            특이사항: document.getElementById('editNotes')?.value?.trim() || '',
        };
        if (SiteDetail.currentSite && SiteDetail.currentSite.version) {
            updateData.version = SiteDetail.currentSite.version;
        }
        const res = await DataAPI.updateSite(siteId, updateData);
        if (res) {
            UI.showToast('현장 정보가 수정되었습니다.', 'success');
            this.closeEditSiteModal();
            await SiteDetail.open(siteId);
            await this.loadAll();
        }
    },
};

document.addEventListener('DOMContentLoaded', () => App.init());
