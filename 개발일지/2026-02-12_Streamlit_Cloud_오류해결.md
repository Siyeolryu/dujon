# Streamlit Cloud 배포 오류 해결 가이드

## 문제 상황
- **오류**: `ModuleNotFoundError: This app has encountered an error... openpyxl`
- **페이지**: 투입가능인원_상세 (8번 페이지)
- **원인**: Excel 내보내기 기능에 필요한 `openpyxl` 라이브러리가 Streamlit Cloud 환경에 설치되지 않음

## 해결 조치 (완료)

### 1. requirements.txt 업데이트 ✅
```
openpyxl>=3.1.2
```
- `requirements.txt`와 `requirements_streamlit.txt` 모두에 추가 완료
- GitHub에 푸시 완료 (커밋: 04c9ff8, d3c3c08)

### 2. Streamlit Cloud 재빌드 트리거 ✅
- `streamlit_app.py`에 주석 추가하여 변경 감지 유도
- 자동 재빌드가 시작되어야 함

## Streamlit Cloud에서 확인할 사항

### 방법 1: 앱 관리 페이지에서 확인
1. Streamlit Cloud 앱 페이지 접속: https://fmy69epaeds9hnwrakvwvb.streamlit.app/
2. 우측 하단의 **"Manage app"** 버튼 클릭
3. **"Logs"** 탭에서 재빌드 진행 상황 확인:
   - `Installing requirements from requirements.txt` 메시지 확인
   - `openpyxl` 설치 로그 확인
   - 빌드 완료 후 `App is live` 메시지 확인

### 방법 2: 수동 재부팅 (권장)
만약 자동 재빌드가 시작되지 않았다면:
1. **"Manage app"** → **"⋮" (메뉴)** → **"Reboot app"** 클릭
2. 앱이 재시작되면서 `requirements.txt`를 다시 읽고 패키지 설치

### 방법 3: 캐시 클리어 후 재배포
위 방법으로도 해결되지 않으면:
1. **"Manage app"** → **"Settings"** → **"Clear cache"**
2. 또는 **"⋮" (메뉴)** → **"Delete app"** 후 재배포

## 예상 재빌드 시간
- 일반적으로 **1~3분** 소요
- 패키지가 많거나 Streamlit Cloud 서버가 바쁜 경우 **최대 5~10분** 소요 가능

## 재빌드 완료 후 테스트
1. 앱 새로고침 (F5 또는 Ctrl+R)
2. **"투입가능인원_상세"** 페이지 접속
3. **"📊 Excel 다운로드"** 버튼 클릭
4. 오류 없이 Excel 파일이 다운로드되는지 확인

## 여전히 오류가 발생하는 경우

### 확인 사항
1. **GitHub에 최신 코드가 반영되었는지 확인**:
   - https://github.com/Siyeolryu/dujon/blob/main/requirements.txt
   - `openpyxl>=3.1.2`가 포함되어 있는지 확인

2. **Streamlit Cloud가 올바른 브랜치를 사용하는지 확인**:
   - "Manage app" → "Settings" → "Main file path": `streamlit_app.py`
   - "Branch": `main`

3. **로그에서 오류 메시지 확인**:
   - "Manage app" → "Logs"
   - `ERROR` 또는 `FAILED` 키워드 검색

### 대체 해결 방법
만약 `openpyxl`이 여전히 설치되지 않는다면, `export.py`를 수정하여 Excel 기능을 선택적으로 비활성화:

```python
# streamlit_utils/export.py 수정
try:
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

def render_quick_export_buttons(...):
    if not EXCEL_AVAILABLE:
        st.warning("Excel 내보내기는 현재 사용할 수 없습니다. CSV를 사용하세요.")
        # CSV만 제공
    else:
        # Excel과 CSV 모두 제공
```

## 참고 링크
- Streamlit Cloud 문서: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app
- openpyxl 문서: https://openpyxl.readthedocs.io/

---

**작성일**: 2026-02-12  
**최종 업데이트**: 2026-02-12 15:49
