/**
 * 대시보드 통계 카드 + 배정 현황 SVG 차트 - API /stats 연동
 * 스켈레톤 UI 지원 + 탭 기능 (클릭 시 필터 적용)
 */
const Dashboard = {
    activeTabId: null,

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
        
        // 투입가능 인원 카드 통합
        const totalPersonnel = personnel.total ?? 0;
        const availablePersonnel = personnel.available ?? 0;
        const personnelCard = document.getElementById('statAvailablePersonnel');
        if (personnelCard) {
            const numEl = personnelCard.querySelector('.stat-number');
            const subEl = personnelCard.querySelector('.stat-sub-label');
            if (numEl) {
                numEl.textContent = `${availablePersonnel} / ${totalPersonnel}`;
                numEl.removeAttribute('data-skeleton');
                numEl.classList.remove('skeleton-number');
            }
            if (subEl) {
                subEl.textContent = `전체 ${totalPersonnel}명 · 투입가능 ${availablePersonnel}명`;
                subEl.removeAttribute('data-skeleton');
                subEl.classList.remove('skeleton-sub');
            }
        }
        const unassigned = sites.unassigned ?? 0;
        const cardEl = document.getElementById('statUnassigned');
        if (cardEl) {
            if (unassigned >= 5) cardEl.classList.add('highlight-warning');
            else cardEl.classList.remove('highlight-warning');
        }
        this.renderChart(sites.assigned ?? 0, sites.unassigned ?? 0, sites.total ?? 0);
        this.renderSummaryStrip(sites.by_company || {}, sites.by_state || {});
        this.initTabs();
    },

    /** 회사별·현장상태별 요약 스트립 (전체 현황 한눈에) */
    renderSummaryStrip(byCompany, byState) {
        const el = document.getElementById('summaryStrip');
        if (!el) return;
        const companyLabels = { '더존종합건설': '종합건설', '더존하우징': '하우징' };
        let companyHtml = '';
        for (const [k, v] of Object.entries(byCompany)) {
            if (v === 0) continue;
            companyHtml += `<span class="summary-item">${companyLabels[k] || k} <span>${v}건</span></span>`;
        }
        let stateHtml = '';
        const stateOrder = ['건축허가', '착공예정', '공사 중', '공사 중단', '준공'];
        for (const s of stateOrder) {
            const v = byState[s];
            if (!v) continue;
            stateHtml += `<span class="summary-item">${s} <span>${v}건</span></span>`;
        }
        for (const [k, v] of Object.entries(byState)) {
            if (stateOrder.includes(k) || v === 0) continue;
            stateHtml += `<span class="summary-item">${k} <span>${v}건</span></span>`;
        }
        el.innerHTML = '';
        if (companyHtml) {
            const g = document.createElement('div');
            g.className = 'summary-group';
            g.innerHTML = '<strong>회사별</strong>' + companyHtml;
            el.appendChild(g);
        }
        if (stateHtml) {
            const g = document.createElement('div');
            g.className = 'summary-group';
            g.innerHTML = '<strong>현장상태별</strong>' + stateHtml;
            el.appendChild(g);
        }
        if (!el.innerHTML) el.innerHTML = '<span class="summary-item">요약 데이터 없음</span>';
    },

    initTabs() {
        const tabs = document.querySelectorAll('.stat-card.stat-tab');
        tabs.forEach((tab) => {
            // 클릭 이벤트
            tab.addEventListener('click', () => this.handleTabClick(tab));
            // 키보드 접근성 (Enter/Space)
            tab.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.handleTabClick(tab);
                }
            });
        });
    },

    handleTabClick(tab) {
        const filterType = tab.getAttribute('data-filter-type');
        const filterValue = tab.getAttribute('data-filter-value');
        const tabId = tab.id;

        // 활성 탭 상태 업데이트
        this.setActiveTab(tabId);

        // 필터 타입에 따라 처리
        if (filterType === 'reset') {
            // 전체 현장: 모든 필터 초기화
            if (typeof Filter !== 'undefined') {
                Filter.reset();
            }
        } else if (filterType === 'status') {
            // 배정상태 필터 적용 (미배정/배정완료)
            if (typeof Filter !== 'undefined') {
                const statusEl = document.getElementById('filterStatus');
                if (statusEl) {
                    statusEl.value = filterValue;
                    Filter.apply();
                }
            }
        } else if (filterType === 'personnel') {
            // 투입가능 인원: 새 탭으로 상세 페이지 열기
            this.openPersonnelDetailPage();
        }

        // 스크롤을 현장 목록으로 이동 (부드러운 스크롤)
        const siteListSection = document.getElementById('siteList');
        if (siteListSection) {
            siteListSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    },

    setActiveTab(tabId) {
        // 모든 탭에서 active 클래스 제거
        document.querySelectorAll('.stat-card.stat-tab').forEach((tab) => {
            tab.classList.remove('active');
            tab.setAttribute('aria-selected', 'false');
        });
        // 선택된 탭에 active 클래스 추가
        const activeTab = document.getElementById(tabId);
        if (activeTab) {
            activeTab.classList.add('active');
            activeTab.setAttribute('aria-selected', 'true');
            this.activeTabId = tabId;
        }
    },

    clearActiveTab() {
        document.querySelectorAll('.stat-card.stat-tab').forEach((tab) => {
            tab.classList.remove('active');
            tab.setAttribute('aria-selected', 'false');
        });
        this.activeTabId = null;
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
        const assignedPct = ((assigned / total) * 100).toFixed(1);
        const dashArray = [2 * Math.PI * r * assignedRatio, 2 * Math.PI * r * unassignedRatio];
        const dashOffset = -Math.PI * r; // 12시부터 시작
        
        // 인터랙티브 SVG (클릭 가능)
        const svg = `
            <svg viewBox="0 0 ${size} ${size}" width="100%" height="120" aria-hidden="true">
                <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#e9ecef" stroke-width="12"/>
                <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#c3e6cb" stroke-width="12"
                    stroke-dasharray="${dashArray[0]} ${dashArray[1]}" stroke-dashoffset="${dashOffset}"
                    stroke-linecap="round" transform="rotate(-90 ${cx} ${cy})" 
                    class="chart-segment-assigned" style="cursor:pointer;" 
                    onclick="if(typeof Filter !== 'undefined') { document.getElementById('filterStatus').value='배정완료'; Filter.apply(); }"/>
                <text x="${cx}" y="${cy - 6}" text-anchor="middle" font-size="14" font-weight="600" fill="#1a1d21">${total}</text>
                <text x="${cx}" y="${cy + 12}" text-anchor="middle" font-size="11" fill="#6c757d">전체</text>
            </svg>
            <div style="display:flex;justify-content:center;gap:16px;margin-top:8px;font-size:12px;">
                <span style="color:#2e7d32;cursor:pointer;" onclick="if(typeof Filter !== 'undefined') { document.getElementById('filterStatus').value='배정완료'; Filter.apply(); }">
                    <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#c3e6cb;vertical-align:middle;margin-right:4px"></span>배정완료 ${assigned}
                </span>
                <span style="color:#c62828;cursor:pointer;" onclick="if(typeof Filter !== 'undefined') { document.getElementById('filterStatus').value='미배정'; Filter.apply(); }">
                    <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#f5c6cb;vertical-align:middle;margin-right:4px"></span>미배정 ${unassigned}
                </span>
            </div>
            <div style="text-align:center;margin-top:8px;font-size:13px;font-weight:500;color:#495057;">
                배정률: ${assignedPct}%
            </div>
        `;
        wrap.innerHTML = svg;
    },

    openPersonnelDetailPage() {
        // 새 탭으로 투입가능 인원 상세 페이지 열기 (Streamlit 또는 별도 HTML)
        // 현재는 필터만 적용하도록 유지 (추후 별도 페이지 구현 시 수정)
        window.open('/pages/8_personnel_detail', '_blank');
    },
};
