/**
 * 필터/검색 - API 쿼리 연동
 */
const Filter = {
    currentFilters: { company: 'all', status: 'all', state: 'all' },

    init() {
        const companyEl = document.getElementById('filterCompany');
        const statusEl = document.getElementById('filterStatus');
        const stateEl = document.getElementById('filterState');
        const searchInput = document.getElementById('searchInput');
        const searchBtn = document.getElementById('searchBtn');
        const resetBtn = document.getElementById('resetFilter');
        if (companyEl) companyEl.addEventListener('change', () => this.apply());
        if (statusEl) statusEl.addEventListener('change', () => this.apply());
        if (stateEl) stateEl.addEventListener('change', () => this.apply());
        if (searchInput) {
            searchInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') this.search(); });
        }
        if (searchBtn) searchBtn.addEventListener('click', () => this.search());
        if (resetBtn) resetBtn.addEventListener('click', () => this.reset());
    },

    getFilterValues() {
        const companyEl = document.getElementById('filterCompany');
        const statusEl = document.getElementById('filterStatus');
        const stateEl = document.getElementById('filterState');
        return {
            company: companyEl ? companyEl.value : 'all',
            status: statusEl ? statusEl.value : 'all',
            state: stateEl ? stateEl.value : 'all',
        };
    },

    async apply() {
        this.currentFilters = this.getFilterValues();
        // 필터 변경 시 Dashboard 탭 상태 동기화
        this.syncDashboardTab();
        const apiCompany = DISPLAY_MAP.companyReverse[this.currentFilters.company] ?? '';
        const params = {};
        if (apiCompany) params.company = apiCompany;
        if (this.currentFilters.status && this.currentFilters.status !== 'all') params.status = this.currentFilters.status;
        if (this.currentFilters.state && this.currentFilters.state !== 'all') params.state = this.currentFilters.state;
        const result = await DataAPI.getSites(params);
        if (typeof App === 'undefined' || !App.renderSiteList) return;
        if (result) {
            if (typeof SiteMap !== 'undefined') SiteMap.updateMarkers(result.data);
            App.renderSiteList(result.data);
            const countEl = document.getElementById('siteCount');
            if (countEl) countEl.textContent = result.count;
        } else {
            App.renderSiteList(null, true);
            const countEl = document.getElementById('siteCount');
            if (countEl) countEl.textContent = '-';
        }
    },

    syncDashboardTab() {
        // 필터 상태에 따라 Dashboard 탭 활성화
        if (typeof Dashboard === 'undefined') return;
        const status = this.currentFilters.status;
        // 배정상태 필터가 설정되어 있고, 다른 필터가 없으면 해당 탭 활성화
        if (status === '미배정' && this.currentFilters.company === 'all' && this.currentFilters.state === 'all') {
            Dashboard.setActiveTab('statUnassigned');
        } else if (status === '배정완료' && this.currentFilters.company === 'all' && this.currentFilters.state === 'all') {
            Dashboard.setActiveTab('statAssigned');
        } else if (status === 'all' && this.currentFilters.company === 'all' && this.currentFilters.state === 'all') {
            Dashboard.setActiveTab('statTotalSites');
        } else {
            // 복합 필터가 적용되면 탭 비활성화
            Dashboard.clearActiveTab();
        }
    },

    async search() {
        const input = document.getElementById('searchInput');
        const query = input ? input.value.trim() : '';
        const result = await DataAPI.searchSites(query);
        if (typeof App === 'undefined' || !App.renderSiteList) return;
        if (result) {
            if (typeof SiteMap !== 'undefined') SiteMap.updateMarkers(result.data);
            App.renderSiteList(result.data);
            const countEl = document.getElementById('siteCount');
            if (countEl) countEl.textContent = result.count;
        } else {
            App.renderSiteList(null, true);
            const countEl = document.getElementById('siteCount');
            if (countEl) countEl.textContent = '-';
        }
    },

    reset() {
        const companyEl = document.getElementById('filterCompany');
        const statusEl = document.getElementById('filterStatus');
        const stateEl = document.getElementById('filterState');
        const searchInput = document.getElementById('searchInput');
        if (companyEl) companyEl.value = 'all';
        if (statusEl) statusEl.value = 'all';
        if (stateEl) stateEl.value = 'all';
        if (searchInput) searchInput.value = '';
        this.currentFilters = { company: 'all', status: 'all', state: 'all' };
        // Dashboard 탭 활성 상태 초기화
        if (typeof Dashboard !== 'undefined' && Dashboard.clearActiveTab) {
            Dashboard.clearActiveTab();
        }
        this.apply();
    },
};
