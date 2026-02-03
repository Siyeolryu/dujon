# 현장배정 관리 시스템 (dujon)

Google Sheets를 DB로 사용하는 현장·인력·자격증 관리 및 소장 배정 API + HTML 앱

- **저장소**: [Siyeolryu/dujon](https://github.com/Siyeolryu/dujon)
- **DB 스프레드시트**: [현장배정 DB (Google Sheets)](https://docs.google.com/spreadsheets/d/15fAEzkC9FCLA6sG1N--f69r-32WHoYLvmXcwED5xWzM/edit) — 현장등록·소장등록 등 모든 데이터가 해당 시트에 저장됩니다.

## 구성

- **Phase 2-1**: 데이터 조회 API (GET /api/sites, personnel, certificates, stats)
- **Phase 2-2**: 데이터 수정 API (POST/PUT, 소장 배정/해제)
- **Phase 2-3**: 실시간 동기화 (낙관적 잠금, 버전·충돌 감지)

## 실행

```bash
# API 서버
pip install -r requirements_api.txt
python run_api.py
# → http://localhost:5000
```

## GitHub 전체 업로드

- **한 번에 업로드**: `git_push_전체업로드.bat` 더블클릭 → 전체 파일 [Siyeolryu/dujon](https://github.com/Siyeolryu/dujon) 에 푸시  
- **연동만**: `github_연동_dujon.bat` → **푸시**: `git_push_dujon.bat` 또는 [GitHub_PUSH_가이드.md](GitHub_PUSH_가이드.md)
