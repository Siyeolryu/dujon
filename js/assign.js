/**
 * 소장 배정 패널 - API assign/unassign 연동
 * API는 manager_id, certificate_id 둘 다 필수
 */
const Assign = {
    targetSiteId: null,
    selectedManagerId: null,
    selectedCertId: null,
    siteDetail: null,

    async open(siteId, siteName, siteAddress) {
        this.targetSiteId = siteId;
        this.selectedManagerId = null;
        this.selectedCertId = null;
        this.siteDetail = null;
        const nameEl = document.getElementById('assignTargetSite');
        const addrEl = document.getElementById('assignTargetAddress');
        if (nameEl) nameEl.textContent = siteName || '-';
        if (addrEl) addrEl.textContent = siteAddress || '';

        const detail = await API.getSiteDetail(siteId);
        if (detail) this.siteDetail = detail;

        const managerSelect = document.getElementById('managerSelect');
        const certSelect = document.getElementById('certificateSelect');
        if (managerSelect) managerSelect.innerHTML = '<option value="">-- 투입가능 소장 목록 --</option>';
        if (certSelect) certSelect.innerHTML = '<option value="">-- 사용가능 자격증 목록 --</option>';
        document.getElementById('managerPreview')?.classList.add('hidden');
        document.getElementById('certPreview')?.classList.add('hidden');
        this.updateConfirmButton();

        const personnelRes = await API.getPersonnel({ status: '투입가능', role: '소장' });
        const certRes = await API.getCertificates({ available: 'true' });
        if (managerSelect && personnelRes && personnelRes.data) {
            personnelRes.data.forEach((p) => {
                const opt = document.createElement('option');
                opt.value = p['인력ID'] || '';
                const companyDisplay = DISPLAY_MAP.company[p['소속']] || p['소속'] || '';
                const count = p['현재담당현장수'] ?? 0;
                opt.textContent = `${p['성명'] || ''} (${companyDisplay}, 현재 ${count}현장)`;
                managerSelect.appendChild(opt);
            });
        }
        if (certSelect && certRes && certRes.data) {
            certRes.data.forEach((c) => {
                const opt = document.createElement('option');
                opt.value = c['자격증ID'] || '';
                opt.textContent = `${c['자격증명'] || ''} — 소유자: ${c['소유자명'] || ''}`;
                certSelect.appendChild(opt);
            });
        }

        document.getElementById('assignPanel')?.classList.remove('hidden');
    },

    onManagerSelect(managerId) {
        this.selectedManagerId = managerId || null;
        const preview = document.getElementById('managerPreview');
        if (!preview) return;
        if (!managerId) {
            preview.classList.add('hidden');
            this.updateConfirmButton();
            return;
        }
        API.getPersonnelDetail(managerId).then((p) => {
            if (!p || p['인력ID'] !== managerId) return;
            preview.innerHTML = `
                <p><strong>${p['성명'] || '-'}</strong></p>
                <p>직책: ${p['직책'] || '-'} | 소속: ${DISPLAY_MAP.company[p['소속']] || p['소속'] || '-'}</p>
                <p>연락처: ${p['연락처'] || '-'}</p>
                <p>현재담당현장수: ${p['현재담당현장수'] ?? 0}</p>
            `;
            preview.classList.remove('hidden');
        });
        this.updateConfirmButton();
    },

    onCertSelect(certId) {
        this.selectedCertId = certId || null;
        const preview = document.getElementById('certPreview');
        if (!preview) return;
        if (!certId) {
            preview.classList.add('hidden');
            this.updateConfirmButton();
            return;
        }
        API.getCertificateDetail(certId).then((c) => {
            if (!c || c['자격증ID'] !== certId) return;
            preview.innerHTML = `
                <p><strong>${c['자격증명'] || '-'}</strong></p>
                <p>자격증번호: ${c['자격증번호'] || '-'}</p>
                <p>소유자: ${c['소유자명'] || '-'} (${c['소유자연락처'] || '-'})</p>
                <p>유효기간: ${c['유효기간'] || '-'}</p>
            `;
            preview.classList.remove('hidden');
        });
        this.updateConfirmButton();
    },

    updateConfirmButton() {
        const btn = document.getElementById('btnConfirmAssign');
        if (btn) btn.disabled = !(this.selectedManagerId && this.selectedCertId);
    },

    async confirm() {
        if (!this.targetSiteId || !this.selectedManagerId || !this.selectedCertId) {
            UI.showToast('소장과 자격증을 모두 선택해 주세요.', 'warning');
            return;
        }
        const siteName = document.getElementById('assignTargetSite')?.textContent || this.targetSiteId;
        const ok = await UI.confirm('배정 확인', `${siteName}에 선택한 소장·자격증을 배정하시겠습니까?`);
        if (!ok) return;
        this.setConfirmButtonLoading(true);
        const assignData = {
            담당소장ID: this.selectedManagerId,
            사용자격증ID: this.selectedCertId,
        };
        const version = (SiteDetail.currentSite && SiteDetail.currentSite['현장ID'] === this.targetSiteId) ? SiteDetail.currentSite.version : (this.siteDetail?.version || null);
        if (version) assignData.version = version;
        try {
            const res = await API.assignManager(this.targetSiteId, assignData);
            if (res) {
                UI.showToast('배정이 완료되었습니다.', 'success');
                this.close();
                if (typeof App !== 'undefined' && App.loadAll) await App.loadAll();
            }
        } finally {
            this.setConfirmButtonLoading(false);
        }
    },

    async unassign(siteId) {
        const ok = await UI.confirm('배정 해제', '이 현장의 배정을 해제하시겠습니까?');
        if (!ok) return;
        const btnUnassign = document.getElementById('btnUnassign');
        if (btnUnassign) {
            btnUnassign.disabled = true;
            btnUnassign.textContent = '처리 중...';
        }
        let version = (SiteDetail.currentSite && SiteDetail.currentSite['현장ID'] === siteId) ? SiteDetail.currentSite.version : null;
        if (!version && this.siteDetail && this.siteDetail['현장ID'] === siteId) version = this.siteDetail.version;
        try {
            const res = await API.unassignManager(siteId, version);
            if (res) {
                UI.showToast('배정이 해제되었습니다.', 'success');
                SiteDetail.close();
                if (typeof App !== 'undefined' && App.loadAll) await App.loadAll();
            }
        } finally {
            if (btnUnassign) {
                btnUnassign.disabled = false;
                btnUnassign.textContent = '배정 해제';
            }
        }
    },

    close() {
        this.targetSiteId = null;
        this.selectedManagerId = null;
        this.selectedCertId = null;
        this.siteDetail = null;
        document.getElementById('assignPanel')?.classList.add('hidden');
    },

    setConfirmButtonLoading(loading) {
        const btn = document.getElementById('btnConfirmAssign');
        if (!btn) return;
        btn.disabled = loading;
        btn.textContent = loading ? '처리 중...' : '배정 확인';
    },
};
