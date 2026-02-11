"""
데이터 내보내기 데모 페이지
Excel, CSV 내보내기 기능 테스트
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_utils.theme import apply_localhost_theme
from streamlit_utils.export import (
    render_export_button, render_export_section, render_quick_export_buttons,
    prepare_sites_export, prepare_personnel_export, prepare_certificates_export
)
from streamlit_utils.api_client import get_sites, get_personnel, get_certificates

apply_localhost_theme()

st.title("📥 데이터 내보내기 데모")
st.markdown("**Excel 및 CSV 내보내기 기능 테스트**")

# ========== 샘플 데이터 생성 ==========
st.markdown("---")
st.markdown("### 샘플 데이터")

# 현장 샘플 데이터
sample_sites = [
    {
        "현장ID": "S001",
        "현장명": "평택 푸르지오",
        "회사구분": "더존종합건설",
        "주소": "경기도 평택시 비전동 123",
        "현장상태": "착공중",
        "배정상태": "배정완료",
        "담당소장명": "김현장",
        "담당소장연락처": "010-1234-5678",
        "사용자격증명": "건축기사",
        "자격증소유자명": "김현장",
        "건축허가일": "2025-12-10",
        "착공예정일": "2026-03-15",
        "준공일": "2027-12-30",
        "특이사항": "대단지 아파트",
        "등록일": "2025-11-01",
        "수정일": "2026-01-05"
    },
    {
        "현장ID": "S002",
        "현장명": "수원 힐스테이트",
        "회사구분": "더존종합건설",
        "주소": "경기도 수원시 영통구 456",
        "현장상태": "착공예정",
        "배정상태": "배정완료",
        "담당소장명": "이소장",
        "담당소장연락처": "010-2345-6789",
        "사용자격증명": "건축산업기사",
        "자격증소유자명": "이소장",
        "건축허가일": "2026-01-05",
        "착공예정일": "2026-04-01",
        "준공일": "2027-10-15",
        "특이사항": "역세권 개발",
        "등록일": "2025-11-15",
        "수정일": "2026-01-10"
    },
    {
        "현장ID": "S003",
        "현장명": "용인 동백 자이",
        "회사구분": "더존종합건설",
        "주소": "경기도 용인시 기흥구 789",
        "현장상태": "건축허가",
        "배정상태": "미배정",
        "담당소장명": "",
        "담당소장연락처": "",
        "사용자격증명": "건축기사",
        "자격증소유자명": "박사무실장",
        "건축허가일": "2026-02-20",
        "착공예정일": "2026-05-10",
        "준공일": "2028-03-20",
        "특이사항": "학군지 인기단지",
        "등록일": "2025-12-01",
        "수정일": "2026-01-15"
    },
]

# 인력 샘플 데이터
sample_personnel = [
    {
        "인력ID": "P001",
        "성명": "김현장",
        "직책": "소장",
        "소속": "더존종합건설",
        "연락처": "010-1234-5678",
        "이메일": "kim@example.com",
        "보유자격증": "건축기사, 안전관리자",
        "현재상태": "투입중",
        "현재담당현장수": 3,
        "입사일": "2010-03-02",
        "비고": "15년차 베테랑",
        "등록일": "2025-11-01"
    },
    {
        "인력ID": "P002",
        "성명": "이소장",
        "직책": "소장",
        "소속": "더존종합건설",
        "연락처": "010-2345-6789",
        "이메일": "lee@example.com",
        "보유자격증": "건축산업기사",
        "현재상태": "투입중",
        "현재담당현장수": 2,
        "입사일": "2012-05-15",
        "비고": "아파트 전문",
        "등록일": "2025-11-01"
    },
]

# DataFrame 변환
sites_df = pd.DataFrame(sample_sites)
personnel_df = pd.DataFrame(sample_personnel)

st.caption(f"현장 데이터: {len(sample_sites)}건 | 인력 데이터: {len(sample_personnel)}건")

# ========== 방법 1: 빠른 내보내기 버튼 ==========
st.markdown("---")
st.markdown("### 방법 1: 빠른 내보내기 버튼")
st.markdown("Excel과 CSV 버튼을 나란히 배치")

tab1, tab2 = st.tabs(["현장 데이터", "인력 데이터"])

with tab1:
    st.markdown("#### 현장 데이터 내보내기")
    render_quick_export_buttons(
        data=sites_df,
        filename_prefix="현장목록",
        key_suffix="sites_quick"
    )

with tab2:
    st.markdown("#### 인력 데이터 내보내기")
    render_quick_export_buttons(
        data=personnel_df,
        filename_prefix="인력목록",
        key_suffix="personnel_quick"
    )

# ========== 방법 2: 내보내기 섹션 (미리보기 포함) ==========
st.markdown("---")
st.markdown("### 방법 2: 내보내기 섹션 (미리보기 포함)")
st.markdown("Expander로 접을 수 있으며, 데이터 미리보기 제공")

render_export_section(
    data=sites_df,
    title="현장 데이터 내보내기",
    filename_prefix="현장목록",
    show_preview=True,
    preview_rows=3,
    key_suffix="sites_section"
)

render_export_section(
    data=personnel_df,
    title="인력 데이터 내보내기",
    filename_prefix="인력목록",
    show_preview=True,
    preview_rows=2,
    key_suffix="personnel_section"
)

# ========== 방법 3: 단일 내보내기 버튼 ==========
st.markdown("---")
st.markdown("### 방법 3: 단일 내보내기 버튼")
st.markdown("형식 선택 후 다운로드")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 현장 데이터")
    render_export_button(
        data=sites_df,
        filename_prefix="현장목록",
        button_text="📥 현장 데이터 다운로드",
        key_suffix="sites_single"
    )

with col2:
    st.markdown("#### 인력 데이터")
    render_export_button(
        data=personnel_df,
        filename_prefix="인력목록",
        button_text="📥 인력 데이터 다운로드",
        key_suffix="personnel_single"
    )

# ========== 실제 API 데이터 테스트 ==========
st.markdown("---")
st.markdown("### 실제 API 데이터 내보내기")
st.markdown("API에서 실제 데이터를 가져와 내보내기")

if st.button("🔄 API 데이터 불러오기", use_container_width=True):
    with st.spinner("데이터 로딩 중..."):
        # 실제 API 호출
        sites_data, sites_err = get_sites()
        personnel_data, personnel_err = get_personnel()
        
        if sites_data:
            st.success(f"✅ 현장 데이터 {len(sites_data)}건 로드 완료")
            sites_export_df = prepare_sites_export(sites_data)
            
            st.markdown("#### 현장 데이터 내보내기")
            render_quick_export_buttons(
                data=sites_export_df,
                filename_prefix="현장목록_실제데이터",
                key_suffix="sites_api"
            )
        else:
            st.warning(f"현장 데이터 로드 실패: {sites_err}")
        
        if personnel_data:
            st.success(f"✅ 인력 데이터 {len(personnel_data)}건 로드 완료")
            personnel_export_df = prepare_personnel_export(personnel_data)
            
            st.markdown("#### 인력 데이터 내보내기")
            render_quick_export_buttons(
                data=personnel_export_df,
                filename_prefix="인력목록_실제데이터",
                key_suffix="personnel_api"
            )
        else:
            st.warning(f"인력 데이터 로드 실패: {personnel_err}")

# ========== 사용 가이드 ==========
st.markdown("---")
st.markdown("### 📝 사용 가이드")

st.markdown("""
#### 내보내기 기능 특징

1. **Excel 내보내기** (`.xlsx`)
   - 컬럼 너비 자동 조정
   - 한글 완벽 지원
   - Excel에서 바로 열기 가능

2. **CSV 내보내기** (`.csv`)
   - UTF-8 BOM 인코딩 (Excel 한글 깨짐 방지)
   - 가벼운 파일 크기
   - 다양한 프로그램에서 호환

3. **파일명 자동 생성**
   - 형식: `{접두사}_{YYYYMMDD_HHMMSS}.{확장자}`
   - 예: `현장목록_20260211_232900.xlsx`

#### 통합 방법

```python
# 페이지에 통합하기
from streamlit_utils.export import render_quick_export_buttons, prepare_sites_export

# 데이터 준비
sites_data, _ = get_sites()
export_df = prepare_sites_export(sites_data)

# 내보내기 버튼 렌더링
render_quick_export_buttons(
    data=export_df,
    filename_prefix="현장목록",
    key_suffix="unique_key"
)
```

#### 다음 단계

- ✅ 현장 목록 페이지에 통합
- ✅ 투입가능인원 페이지에 통합
- ✅ 필터링된 데이터만 내보내기
- ✅ 자격증 목록 페이지에 통합
""")
