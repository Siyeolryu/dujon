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

        const editTabSiteSelect = document.getElementById('editTabSiteSelect');
        if (editTabSiteSelect) {
            editTabSiteSelect.addEventListener('change', () => this.onEditTabSiteSelect());
        }
        const formSiteEdit = document.getElementById('formSiteEdit');
        if (formSiteEdit) {
            formSiteEdit.addEventListener('submit', (e) => { e.preventDefault(); this.submitSiteEdit(); });
        }
        document.getElementById('editTabSiteReset')?.addEventListener('click', () => this.resetSiteEditForm());

        const editTabCertSelect = document.getElementById('editTabCertSelect');
        if (editTabCertSelect) {
            editTabCertSelect.addEventListener('change', () => this.onEditTabCertSelect());
        }
        const formCertEdit = document.getElementById('formCertEdit');
        if (formCertEdit) {
            formCertEdit.addEventListener('submit', (e) => { e.preventDefault(); this.submitCertEdit(); });
        }
        document.getElementById('editTabCertReset')?.addEventListener('click', () => this.resetCertEditForm());
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
        if (tabId === 'tab-site-edit') this.loadEditTabSites();
        if (tabId === 'tab-cert-edit') this.loadEditTabCerts();
    },

    async loadEditTabSites() {
        const sel = document.getElementById('editTabSiteSelect');
        if (!sel || sel.options.length > 1) return;
        const res = await DataAPI.getSites({});
        const sites = res?.data || [];
        sel.innerHTML = '<option value="">-- 현장 선택 --</option>';
        sites.forEach((s) => {
            const opt = document.createElement('option');
            opt.value = s['현장ID'] || '';
            opt.textContent = (s['현장명'] || s['현장ID']) + ' (' + (s['현장ID'] || '') + ')';
            sel.appendChild(opt);
        });
    },

    async onEditTabSiteSelect() {
        const sel = document.getElementById('editTabSiteSelect');
        const form = document.getElementById('formSiteEdit');
        const siteId = sel?.value?.trim();
        if (!siteId) {
            if (form) form.style.display = 'none';
            return;
        }
        const detail = await DataAPI.getSiteDetail(siteId);
        if (!detail) {
            UI.showToast('현장 정보를 불러올 수 없습니다.', 'error');
            return;
        }
        document.getElementById('editTabSiteId').value = siteId;
        document.getElementById('editTabSiteName').value = detail['현장명'] || '';
        document.getElementById('editTabOwnerName').value = detail['건축주명'] || '';
        document.getElementById('editTabCompany').value = detail['회사구분'] || '';
        document.getElementById('editTabAddress').value = detail['주소'] || '';
        document.getElementById('editTabPermitDate').value = detail['건축허가일'] || '';
        document.getElementById('editTabStartDate').value = detail['착공예정일'] || '';
        document.getElementById('editTabCompletionDate').value = detail['준공일'] || '';
        document.getElementById('editTabState').value = detail['현장상태'] || '건축허가';
        document.getElementById('editTabNotes').value = detail['특이사항'] || '';
        this._editTabSiteVersion = detail.version || '';
        if (form) form.style.display = 'block';
    },

    resetSiteEditForm() {
        document.getElementById('editTabSiteSelect').value = '';
        document.getElementById('formSiteEdit').style.display = 'none';
        document.getElementById('formSiteEdit')?.reset();
        this._editTabSiteVersion = '';
    },

    async submitSiteEdit() {
        const siteId = document.getElementById('editTabSiteId')?.value?.trim();
        if (!siteId) return;
        const updateData = {
            현장명: document.getElementById('editTabSiteName')?.value?.trim() || '',
            건축주명: document.getElementById('editTabOwnerName')?.value?.trim() || '',
            회사구분: document.getElementById('editTabCompany')?.value || '',
            주소: document.getElementById('editTabAddress')?.value?.trim() || '',
            건축허가일: document.getElementById('editTabPermitDate')?.value?.trim() || '',
            착공예정일: document.getElementById('editTabStartDate')?.value?.trim() || '',
            준공일: document.getElementById('editTabCompletionDate')?.value?.trim() || '',
            현장상태: document.getElementById('editTabState')?.value || '건축허가',
            특이사항: document.getElementById('editTabNotes')?.value?.trim() || '',
        };
        if (this._editTabSiteVersion) updateData.version = this._editTabSiteVersion;
        const res = await DataAPI.updateSite(siteId, updateData);
        if (res) {
            UI.showToast('현장 정보가 수정되었습니다.', 'success');
            this._editTabSiteVersion = res.data?.version || this._editTabSiteVersion;
            if (typeof App !== 'undefined' && App.loadAll) await App.loadAll();
        }
    },

    async loadEditTabCerts() {
        const sel = document.getElementById('editTabCertSelect');
        if (!sel || sel.options.length > 1) return;
        const res = await DataAPI.getCertificates({});
        const certs = res?.data || [];
        sel.innerHTML = '<option value="">-- 자격증 선택 --</option>';
        certs.forEach((c) => {
            const opt = document.createElement('option');
            opt.value = c['자격증ID'] || '';
            opt.textContent = (c['자격증명'] || '') + ' / ' + (c['소유자명'] || '') + ' (' + (c['자격증ID'] || '') + ')';
            sel.appendChild(opt);
        });
    },

    async onEditTabCertSelect() {
        const sel = document.getElementById('editTabCertSelect');
        const form = document.getElementById('formCertEdit');
        const certId = sel?.value?.trim();
        if (!certId) {
            if (form) form.style.display = 'none';
            return;
        }
        const detail = await DataAPI.getCertificateDetail(certId);
        if (!detail) {
            UI.showToast('자격증 정보를 불러올 수 없습니다.', 'error');
            return;
        }
        document.getElementById('editTabCertId').value = certId;
        document.getElementById('editTabCertName').value = detail['자격증명'] || '';
        document.getElementById('editTabCertOwnerName').value = detail['소유자명'] || '';
        document.getElementById('editTabCertOwnerPhone').value = detail['소유자연락처'] || '';
        document.getElementById('editTabCertAvailable').value = detail['사용가능여부'] || '사용가능';
        document.getElementById('editTabCertNotes').value = detail['비고'] || '';
        if (form) form.style.display = 'block';
    },

    resetCertEditForm() {
        document.getElementById('editTabCertSelect').value = '';
        document.getElementById('formCertEdit').style.display = 'none';
        document.getElementById('formCertEdit')?.reset();
    },

    async submitCertEdit() {
        const certId = document.getElementById('editTabCertId')?.value?.trim();
        if (!certId) return;
        const updateData = {
            자격증명: document.getElementById('editTabCertName')?.value?.trim() || '',
            소유자명: document.getElementById('editTabCertOwnerName')?.value?.trim() || '',
            소유자연락처: document.getElementById('editTabCertOwnerPhone')?.value?.trim() || '',
            사용가능여부: document.getElementById('editTabCertAvailable')?.value || '사용가능',
            비고: document.getElementById('editTabCertNotes')?.value?.trim() || '',
        };
        const res = await DataAPI.updateCertificate(certId, updateData);
        if (res) {
            UI.showToast('자격증 정보가 수정되었습니다.', 'success');
            if (typeof App !== 'undefined' && App.loadAll) await App.loadAll();
        }
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
