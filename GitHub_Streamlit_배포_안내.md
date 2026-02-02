# GitHub / Streamlit Cloud 배포 시 설정

"Main file path를 찾을 수 없습니다" 오류 시 아래 값을 그대로 입력하세요.

---

## Main file path (필수)

저장소 **루트** 기준 경로입니다. 다음 중 하나를 사용하세요.

```
app_streamlit.py
```

또는

```
streamlit_app.py
```

- 루트에 `app_streamlit.py`와 `streamlit_app.py`가 모두 있으므로 둘 중 아무거나 지정하면 됩니다.

---

## Requirements file (의존성 파일)

```
requirements_streamlit.txt
```

또는 (플랫폼이 `requirements.txt`만 인식하는 경우)

```
requirements.txt
```

---

## Branch

```
main
```

---

## 요약

| 항목 | 입력값 |
|------|--------|
| **Main file path** | `app_streamlit.py` |
| **Requirements file** | `requirements_streamlit.txt` 또는 `requirements.txt` |
| **Branch** | `main` |

설정 후 배포하면 Streamlit이 루트에서 `streamlit run app_streamlit.py`(또는 지정한 파일)를 실행합니다.
