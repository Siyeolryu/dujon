// 전역 변수
let map;
let markers = [];
let currentFilter = {
    company: 'all',
    status: 'all'
};
let selectedSite = null;

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    initMap();
    initFilters();
    initPanels();
    updateStats();
    populateTable();
});

// 지도 초기화 (카카오맵 없이 Google Maps API 사용)
function initMap() {
    // 대한민국 중심 좌표
    const centerLat = 37.5665;
    const centerLng = 126.9780;
    
    // 간단한 지도 대체 (실제로는 Google Maps API나 카카오맵 API 필요)
    const mapElement = document.getElementById('map');
    mapElement.innerHTML = '<div style="width:100%;height:100%;background:#e0e0e0;display:flex;align-items:center;justify-content:center;"><p style="color:#666;">지도 영역 (실제로는 카카오맵 또는 Google Maps API 연동 필요)</p></div>';
    
    // 지도 대신 마커 표시용 캔버스 생성
    createMapCanvas();
}

// 간단한 지도 캔버스 생성
function createMapCanvas() {
    const mapElement = document.getElementById('map');
    mapElement.innerHTML = '';
    
    const canvas = document.createElement('canvas');
    canvas.width = mapElement.offsetWidth;
    canvas.height = mapElement.offsetHeight;
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    mapElement.appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    
    // 배경
    ctx.fillStyle = '#f0f0f0';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // 격자
    ctx.strokeStyle = '#ddd';
    ctx.lineWidth = 1;
    for (let i = 0; i < canvas.width; i += 50) {
        ctx.beginPath();
        ctx.moveTo(i, 0);
        ctx.lineTo(i, canvas.height);
        ctx.stroke();
    }
    for (let i = 0; i < canvas.height; i += 50) {
        ctx.beginPath();
        ctx.moveTo(0, i);
        ctx.lineTo(canvas.width, i);
        ctx.stroke();
    }
    
    // 마커 표시
    drawMarkers(ctx, canvas);
    
    // 클릭 이벤트
    canvas.addEventListener('click', handleMapClick);
}

// 마커 그리기
function drawMarkers(ctx, canvas) {
    const filteredSites = getFilteredSites();
    
    // 좌표 범위 계산
    const lats = filteredSites.map(s => s.lat);
    const lngs = filteredSites.map(s => s.lng);
    const minLat = Math.min(...lats);
    const maxLat = Math.max(...lats);
    const minLng = Math.min(...lngs);
    const maxLng = Math.max(...lngs);
    
    markers = []; // 마커 정보 초기화
    
    filteredSites.forEach(site => {
        // 좌표를 캔버스 좌표로 변환
        const x = ((site.lng - minLng) / (maxLng - minLng)) * (canvas.width - 100) + 50;
        const y = canvas.height - (((site.lat - minLat) / (maxLat - minLat)) * (canvas.height - 100) + 50);
        
        // 마커 색상 결정
        let color;
        if (site.company === '종합') {
            color = '#2196F3'; // 파란색
        } else {
            color = '#FF5722'; // 주황색
        }
        
        // 마커 그리기
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(x, y, 8, 0, Math.PI * 2);
        ctx.fill();
        
        // 배정 상태 표시
        if (site.status === '미배정') {
            ctx.fillStyle = '#FFF';
            ctx.font = 'bold 10px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('!', x, y);
        } else {
            ctx.fillStyle = '#FFF';
            ctx.font = 'bold 8px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('✓', x, y);
        }
        
        // 마커 정보 저장
        markers.push({
            site: site,
            x: x,
            y: y,
            radius: 8
        });
    });
}

// 지도 클릭 처리
function handleMapClick(event) {
    const canvas = event.target;
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    // 클릭한 위치와 가까운 마커 찾기
    for (let marker of markers) {
        const distance = Math.sqrt(Math.pow(x - marker.x, 2) + Math.pow(y - marker.y, 2));
        if (distance <= marker.radius + 5) {
            showDetailPanel(marker.site);
            break;
        }
    }
}

// 필터 초기화
function initFilters() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const filterType = this.dataset.company ? 'company' : 'status';
            const filterValue = this.dataset.company || this.dataset.status;
            
            // 같은 그룹의 버튼 비활성화
            const group = this.parentElement;
            group.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // 필터 적용
            currentFilter[filterType] = filterValue;
            applyFilters();
        });
    });
}

// 필터 적용
function applyFilters() {
    createMapCanvas(); // 지도 다시 그리기
    updateStats();
    populateTable();
}

// 필터링된 현장 데이터 가져오기
function getFilteredSites() {
    return sitesData.filter(site => {
        const companyMatch = currentFilter.company === 'all' || site.company === currentFilter.company;
        const statusMatch = currentFilter.status === 'all' || site.status === currentFilter.status;
        return companyMatch && statusMatch;
    });
}

// 통계 업데이트
function updateStats() {
    const filteredSites = getFilteredSites();
    const assigned = filteredSites.filter(s => s.status === '배정완료').length;
    const unassigned = filteredSites.filter(s => s.status === '미배정').length;
    
    document.getElementById('totalSites').textContent = filteredSites.length;
    document.getElementById('assignedCount').textContent = assigned;
    document.getElementById('unassignedCount').textContent = unassigned;
}

// 패널 초기화
function initPanels() {
    // 상세정보 패널 닫기
    document.getElementById('closePanel').addEventListener('click', hideDetailPanel);
    
    // 리스트뷰 토글
    document.getElementById('toggleListView').addEventListener('click', function() {
        document.getElementById('listViewPanel').classList.add('active');
    });
    
    document.getElementById('closeListView').addEventListener('click', function() {
        document.getElementById('listViewPanel').classList.remove('active');
    });
}

// 상세정보 패널 표시
function showDetailPanel(site) {
    selectedSite = site;
    
    // 현장 정보
    document.getElementById('siteName').textContent = site.name;
    document.getElementById('siteCompany').textContent = site.company === '종합' ? '더존종합건설' : '더존하우징';
    document.getElementById('siteAddress').textContent = site.address;
    
    // 상태 표시
    const statusElement = document.getElementById('siteStatus');
    statusElement.textContent = site.siteStatus;
    statusElement.className = 'value status-tag';
    if (site.siteStatus === '건축허가') {
        statusElement.classList.add('permit');
    } else if (site.siteStatus === '착공예정' || site.siteStatus === '공사 중') {
        statusElement.classList.add('construction');
    } else if (site.siteStatus === '준공') {
        statusElement.classList.add('completed');
    }
    
    document.getElementById('buildingPermitDate').textContent = site.permitDate || '-';
    document.getElementById('siteStartDate').textContent = site.startDate || '-';
    document.getElementById('completionDate').textContent = site.completionDate || '-';
    document.getElementById('specialNotes').textContent = site.specialNotes || '-';
    
    // 준공필증 파일
    const certFileArea = document.getElementById('completionCert');
    if (site.completionCertFile) {
        certFileArea.innerHTML = `<img src="${site.completionCertFile}" alt="준공필증">`;
    } else {
        certFileArea.innerHTML = '<span class="no-file">미등록</span>';
    }
    
    // 담당 소장 정보
    const managerRow = document.getElementById('managerRow');
    const managerPhoneRow = document.getElementById('managerPhoneRow');
    const noManagerNotice = document.getElementById('noManagerNotice');
    
    if (site.manager) {
        managerRow.style.display = 'flex';
        managerPhoneRow.style.display = 'flex';
        noManagerNotice.style.display = 'none';
        
        document.getElementById('managerName').textContent = site.manager;
        document.getElementById('managerPhone').textContent = site.managerPhone || '-';
    } else {
        managerRow.style.display = 'none';
        managerPhoneRow.style.display = 'none';
        noManagerNotice.style.display = 'block';
    }
    
    // 사용 자격증 정보
    const certRow = document.getElementById('certRow');
    const certOwnerRow = document.getElementById('certOwnerRow');
    const certPhoneRow = document.getElementById('certPhoneRow');
    const noCertNotice = document.getElementById('noCertNotice');
    
    if (site.certName) {
        certRow.style.display = 'flex';
        certOwnerRow.style.display = 'flex';
        certPhoneRow.style.display = 'flex';
        noCertNotice.style.display = 'none';
        
        document.getElementById('certName').textContent = site.certName;
        document.getElementById('certOwner').textContent = site.certOwner || '-';
        document.getElementById('certPhone').textContent = site.certPhone || '-';
    } else {
        certRow.style.display = 'none';
        certOwnerRow.style.display = 'none';
        certPhoneRow.style.display = 'none';
        noCertNotice.style.display = 'block';
    }
    
    document.getElementById('detailPanel').classList.add('active');
}

// 상세정보 패널 숨기기
function hideDetailPanel() {
    document.getElementById('detailPanel').classList.remove('active');
    selectedSite = null;
}

// 테이블 채우기
function populateTable() {
    const tbody = document.getElementById('siteTableBody');
    tbody.innerHTML = '';
    
    const filteredSites = getFilteredSites();
    
    filteredSites.forEach(site => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${site.name}</td>
            <td>${site.company === '종합' ? '더존종합' : '더존하우징'}</td>
            <td>${site.startDate}</td>
            <td>${site.manager || '-'}</td>
            <td><span class="status-badge ${site.status === '배정완료' ? 'status-assigned' : 'status-unassigned'}">${site.status}</span></td>
        `;
        
        tr.addEventListener('click', function() {
            showDetailPanel(site);
            document.getElementById('listViewPanel').classList.remove('active');
        });
        
        tbody.appendChild(tr);
    });
}

// 윈도우 리사이즈 시 지도 다시 그리기
window.addEventListener('resize', function() {
    createMapCanvas();
});
