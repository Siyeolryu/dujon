/**
 * 탭 전환 (현장 목록 / 현장등록 / 자격증등록) + 등록 폼 API 연동
 */
const Tabs = {
    init() {
        const nav = document.querySelector('.tab-nav');
        const panels = document.querySelectorAll('.tab-panel');
        if (!nav || !panels.length) return;

        nav.querySelectorAll('.tab-btn').forEach((btn) => {
            btn.addEventListener('click', () => this.switchTab(btn.dataset.tab));
        });

        const formSite = document.getElementById('formSiteRegister');
        if (formSite) {
            formSite.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitSiteRegister();
            });
        }

        const formCert = document.getElementById('formCertRegister');
        if (formCert) {
            formCert.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitCertRegister();
            });
        }
        document.querySelectorAll('.cert-type-btn').forEach((btn) => {
            btn.addEventListener('click', () => this.switchCertType(btn.dataset.certType));
        });
        const customWrap = document.getElementById('certCustomNameWrap');
        if (customWrap) customWrap.classList.add('hidden');
    },

    selectedCertType: '건설초급',

    switchCertType(type) {
        this.selectedCertType = type || '건설초급';
        document.querySelectorAll('.cert-type-btn').forEach((btn) => {
            const isActive = btn.dataset.certType === this.selectedCertType;
            btn.classList.toggle('active', isActive);
            btn.setAttribute('aria-selected', isActive ? 'true' : 'false');
        });
        const customWrap = document.getElementById('certCustomNameWrap');
        if (customWrap) {
            customWrap.classList.toggle('hidden', this.selectedCertType !== '추가등록');
            const input = document.getElementById('newCertCustomName');
            if (input) input.value = '';
        }
    },

    getCertNameForSubmit() {
        if (this.selectedCertType === '추가등록') {
            const v = document.getElementById('newCertCustomName')?.value?.trim();
            return v || '추가등록';
        }
        return this.selectedCertType;
    },

    switchTab(tabId) {
        const panels = document.querySelectorAll('.tab-panel');
        const buttons = document.querySelectorAll('.tab-btn');
        panels.forEach((panel) => {
            const isActive = panel.id === tabId;
            panel.classList.toggle('active', isActive);
            panel.hidden = !isActive;
        });
        buttons.forEach((btn) => {
            btn.classList.toggle('active', btn.dataset.tab === tabId);
            btn.setAttribute('aria-selected', btn.dataset.tab === tabId ? 'true' : 'false');
        });
    },

    async submitSiteRegister() {
        const siteName = document.getElementById('newSiteName')?.value?.trim();
        const company = document.getElementById('newCompany')?.value;
        const address = document.getElementById('newAddress')?.value?.trim();
        if (!siteName || !company || !address) {
            UI.showToast('현장명, 회사구분, 주소는 필수입니다.', 'warning');
            return;
        }
        const payload = {
            현장명: siteName,
            건축주명: document.getElementById('newOwnerName')?.value?.trim() || '',
            회사구분: company,
            주소: address,
            건축허가일: document.getElementById('newPermitDate')?.value?.trim() || '',
            착공예정일: document.getElementById('newStartDate')?.value?.trim() || '',
            준공일: document.getElementById('newCompletionDate')?.value?.trim() || '',
            현장상태: document.getElementById('newState')?.value || '건축허가',
            특이사항: document.getElementById('newNotes')?.value?.trim() || '',
            배정상태: '미배정',
        };
        const res = await DataAPI.createSite(payload);
        if (res) {
            UI.showToast('현장이 등록되었습니다.', 'success');
            document.getElementById('formSiteRegister')?.reset();
            if (typeof App !== 'undefined' && App.loadAll) await App.loadAll();
            this.switchTab('tab-site-list');
        }
    },

    async submitCertRegister() {
        const ownerName = document.getElementById('newCertOwnerName')?.value?.trim();
        if (!ownerName) {
            UI.showToast('소유자 명은 필수입니다.', 'warning');
            return;
        }
        if (this.selectedCertType === '추가등록' && !document.getElementById('newCertCustomName')?.value?.trim()) {
            UI.showToast('+추가등록 선택 시 자격증명을 입력하세요.', 'warning');
            return;
        }
        const certName = this.getCertNameForSubmit();
        const payload = {
            자격증명: certName,
            소유자명: ownerName,
            소유자연락처: document.getElementById('newCertOwnerPhone')?.value?.trim() || '',
            사용가능여부: document.getElementById('newCertAvailable')?.value || '사용가능',
            비고: document.getElementById('newCertNotes')?.value?.trim() || '',
        };
        const res = await DataAPI.createCertificate(payload);
        if (res) {
            UI.showToast('자격증이 등록되었습니다.', 'success');
            document.getElementById('formCertRegister')?.reset();
            this.switchCertType('건설초급');
            if (typeof App !== 'undefined' && App.loadAll) await App.loadAll();
            this.switchTab('tab-site-list');
        }
    },
};
