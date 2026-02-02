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
        const apiCompany = DISPLAY_MAP.companyReverse[this.currentFilters.company] ?? '';
        const params = {};
        if (apiCompany) params.company = apiCompany;
        if (this.currentFilters.status && this.currentFilters.status !== 'all') params.status = this.currentFilters.status;
        if (this.currentFilters.state && this.currentFilters.state !== 'all') params.state = this.currentFilters.state;
        const result = await API.getSites(params);
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

    async search() {
        const input = document.getElementById('searchInput');
        const query = input ? input.value.trim() : '';
        const result = await API.searchSites(query);
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
        this.apply();
    },
};
