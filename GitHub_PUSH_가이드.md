# GitHub 연동·푸시 가이드 (Siyeolryu/dujon)

저장소: **https://github.com/Siyeolryu/dujon**

## 0. 전체 파일 한 번에 업로드 (가장 간단)

프로젝트 폴더에서 **`git_push_전체업로드.bat`** 더블클릭  
→ Git 초기화(필요 시) + `git add .` + 커밋 + **`git push`** [Siyeolryu/dujon](https://github.com/Siyeolryu/dujon) 까지 한 번에 실행

## 0-1. 연동만 하기

**`github_연동_dujon.bat`** 더블클릭  
→ Git 초기화 + `origin` = https://github.com/Siyeolryu/dujon.git 설정

## 1. 수동 연동 (최초 1회)

명령 프롬프트(cmd)에서 프로젝트 폴더로 이동한 뒤 실행하세요.

```cmd
cd /d "c:\Users\user\.cursor\projects\on-site allocation"
```

### Git이 없을 때

```cmd
git init
git remote add origin https://github.com/Siyeolryu/dujon.git
git branch -M main
```

### 이미 다른 remote가 있을 때

```cmd
git remote set-url origin https://github.com/Siyeolryu/dujon.git
```

## 2. 푸시

```cmd
git add .
git status
git commit -m "Phase 2: 1단계 Google Sheets 고급화, 2-1/2-2 API, 2-3 실시간 동기화"
git branch -M main
git push -u origin main
```

- **인증**: 푸시 시 GitHub 로그인 또는 Personal Access Token 입력이 필요할 수 있습니다.
- **빈 저장소**: Siyeolryu/dujon이 비어 있으면 위 `git push -u origin main`으로 첫 푸시가 됩니다.

## 3. 제외 파일 (.gitignore)

다음은 푸시되지 않습니다.

- `.env`, `token.pickle`, `client_secret*.json` (비밀/인증)
- `__pycache__/`, `venv/` (실행/가상환경)

필요 시 `.env.example`만 커밋하고 실제 `.env`는 로컬에서만 사용하세요.
