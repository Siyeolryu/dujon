/**
 * 대시보드 통계 카드 + 배정 현황 SVG 차트 - API /stats 연동
 * 스켈레톤 UI 지원
 */
const Dashboard = {
    async load() {
        this.showSkeleton();
        const data = await DataAPI.getStats();
        this.hideSkeleton();
        if (!data) return;
        const sites = data.sites || {};
        const personnel = data.personnel || {};
        const certs = data.certificates || {};
        this.updateCard('statTotalSites', sites.total ?? 0);
        this.updateCard('statUnassigned', sites.unassigned ?? 0);
        this.updateCard('statAssigned', sites.assigned ?? 0);
        this.updateCard('statAvailablePersonnel', personnel.available ?? 0);
        this.updateCard('statAvailableCerts', certs.available ?? 0);
        const unassigned = sites.unassigned ?? 0;
        const cardEl = document.getElementById('statUnassigned');
        if (cardEl) {
            if (unassigned >= 5) cardEl.classList.add('highlight-warning');
            else cardEl.classList.remove('highlight-warning');
        }
        this.renderChart(sites.assigned ?? 0, sites.unassigned ?? 0, sites.total ?? 0);
    },

    showSkeleton() {
        document.querySelectorAll('#statsGrid .stat-number').forEach((el) => {
            el.setAttribute('data-skeleton', '');
            el.classList.add('skeleton-number');
        });
        const wrap = document.getElementById('chartSvgWrap');
        if (wrap) wrap.innerHTML = '<div class="skeleton-block wide" style="height:120px;margin:0 auto"></div>';
    },

    hideSkeleton() {
        document.querySelectorAll('#statsGrid .stat-number').forEach((el) => {
            el.removeAttribute('data-skeleton');
            el.classList.remove('skeleton-number');
        });
    },

    updateCard(elementId, value) {
        const el = document.getElementById(elementId);
        if (!el) return;
        const numEl = el.querySelector('.stat-number');
        if (!numEl) return;
        const target = Number(value) ?? 0;
        numEl.textContent = target;
        numEl.removeAttribute('data-skeleton');
        numEl.classList.remove('skeleton-number');
    },

    /**
     * 배정 현황 도넛형 SVG (가벼운 시각화)
     * assigned / unassigned 비율
     */
    renderChart(assigned, unassigned, total) {
        const wrap = document.getElementById('chartSvgWrap');
        if (!wrap) return;
        if (total === 0) {
            wrap.innerHTML = '<p style="text-align:center;color:#6c757d;font-size:13px;">데이터 없음</p>';
            return;
        }
        const size = 120;
        const r = 48;
        const cx = size / 2;
        const cy = size / 2;
        const assignedRatio = assigned / total;
        const unassignedRatio = unassigned / total;
        const dashArray = [2 * Math.PI * r * assignedRatio, 2 * Math.PI * r * unassignedRatio];
        const dashOffset = -Math.PI * r; // 12시부터 시작
        const svg = `
            <svg viewBox="0 0 ${size} ${size}" width="100%" height="120" aria-hidden="true">
                <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#e9ecef" stroke-width="12"/>
                <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#c3e6cb" stroke-width="12"
                    stroke-dasharray="${dashArray[0]} ${dashArray[1]}" stroke-dashoffset="${dashOffset}"
                    stroke-linecap="round" transform="rotate(-90 ${cx} ${cy})"/>
                <text x="${cx}" y="${cy - 6}" text-anchor="middle" font-size="14" font-weight="600" fill="#1a1d21">${total}</text>
                <text x="${cx}" y="${cy + 12}" text-anchor="middle" font-size="11" fill="#6c757d">전체</text>
            </svg>
            <div style="display:flex;justify-content:center;gap:16px;margin-top:8px;font-size:12px;">
                <span style="color:#2e7d32"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#c3e6cb;vertical-align:middle;margin-right:4px"></span>배정완료 ${assigned}</span>
                <span style="color:#c62828"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#f5c6cb;vertical-align:middle;margin-right:4px"></span>미배정 ${unassigned}</span>
            </div>
        `;
        wrap.innerHTML = svg;
    },
};
