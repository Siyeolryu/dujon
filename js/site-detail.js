/**
 * 현장 상세 패널 - API getSiteDetail 연동
 */
const SiteDetail = {
    currentSite: null,

    async open(siteId) {
        const data = await DataAPI.getSiteDetail(siteId);
        if (!data) return;
        this.currentSite = data;
        const panel = document.getElementById('siteDetailPanel');
        if (!panel) return;
        const companyDisplay = DISPLAY_MAP.company[data['회사구분']] || data['회사구분'] || '-';
        setText('detailSiteName', data['현장명'] || '-');
        setText('detailSiteId', data['현장ID'] || '-');
        setText('detailCompany', companyDisplay);
        setText('detailAddress', data['주소'] || '-');
        setText('detailState', data['현장상태'] || '-');
        setText('detailPermitDate', data['건축허가일'] || '-');
        setText('detailStartDate', data['착공예정일'] || '-');
        setText('detailCompletionDate', data['준공일'] || '-');
        setText('detailNotes', data['특이사항'] || '-');
        this.renderAssignInfo(data);
        const btnAssign = document.getElementById('btnAssign');
        const btnUnassign = document.getElementById('btnUnassign');
        if (btnAssign && btnUnassign) {
            const isAssigned = data['배정상태'] === '배정완료';
            btnAssign.classList.toggle('hidden', isAssigned);
            btnUnassign.classList.toggle('hidden', !isAssigned);
        }
        panel.classList.remove('hidden');
        if (typeof App !== 'undefined' && App.updateSelectedRow) App.updateSelectedRow(siteId);
    },

    close() {
        this.currentSite = null;
        const panel = document.getElementById('siteDetailPanel');
        if (panel) panel.classList.add('hidden');
    },

    renderAssignInfo(site) {
        const container = document.getElementById('detailAssignInfo');
        if (!container) return;
        if (site['배정상태'] === '배정완료' && (site['담당소장명'] || site.manager)) {
            const manager = site.manager || {};
            const name = site['담당소장명'] || manager.name || '-';
            const phone = site['담당소장연락처'] || manager.phone || '-';
            const certName = site['자격증명'] || (site.certificate && site.certificate.name) || '-';
            const owner = site['자격증소유자명'] || (site.certificate && site.certificate.owner) || '-';
            container.innerHTML = `
                <p><strong>담당소장:</strong> ${name} ${phone ? `(${phone})` : ''}</p>
                <p><strong>사용자격증:</strong> ${certName} — 소유자: ${owner}</p>
            `;
        } else {
            container.innerHTML = `
                <p class="empty-state">소장이 배정되지 않았습니다</p>
                <button type="button" id="btnAssignInline" class="action-btn primary">배정하기</button>
            `;
            const btn = document.getElementById('btnAssignInline');
            if (btn) btn.addEventListener('click', () => {
                if (this.currentSite) Assign.open(this.currentSite['현장ID'], this.currentSite['현장명'] || '', this.currentSite['주소'] || '');
            });
        }
    },
};

function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
}
