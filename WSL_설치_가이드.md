# WSL2 설치 가이드 (오류: HCS_E_HYPERV_NOT_INSTALLED 해결)

이미지에서 발생한 오류는 **가상 머신 플랫폼**이 꺼져 있거나 **BIOS 가상화**가 비활성화되어 있을 때 나타납니다.

---

## 1단계: Windows 기능 활성화

**관리자 PowerShell**을 열고 아래 중 하나를 실행하세요.

### 방법 A: 스크립트 실행 (권장)

1. 파일 탐색기에서 `enable_wsl_features.ps1` 찾기  
   경로: `c:\Users\user\.cursor\projects\배정관리 앱\`
2. **우클릭 → PowerShell에서 실행**  
   (또는 관리자 PowerShell에서 `cd "c:\Users\user\.cursor\projects\배정관리 앱"` 후 `.\enable_wsl_features.ps1`)

### 방법 B: 명령어 직접 입력

관리자 PowerShell에서 **한 줄씩** 실행 (공백 주의: `wsl` 과 `--install` 사이에 띄어쓰기):

```powershell
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
```

```powershell
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

---

## 2단계: 재시작

위 명령이 끝나면 **반드시 PC를 한 번 재시작**하세요.  
기능이 적용되려면 재부팅이 필요합니다.

---

## 3단계: BIOS에서 가상화 확인 (여전히 오류가 나는 경우)

오류 코드 `HCS_E_HYPERV_NOT_INSTALLED`가 **재시작 후에도** 나오면 BIOS 가상화가 꺼져 있을 가능성이 큽니다.

1. PC 재부팅
2. 부팅 시 **F2**, **F10**, **Del** 중 하나를 반복해서 눌러 BIOS/UEFI 진입  
   (제조사마다 키가 다름: Lenovo는 F1/F2, Dell은 F2, HP는 F10 등)
3. 메뉴에서 다음 중 하나를 찾습니다:
   - **Virtualization Technology**
   - **VT-x** (Intel)
   - **AMD-V** (AMD)
   - **SVM Mode**
4. 해당 항목을 **Enabled**로 변경
5. 저장 후 종료 (보통 F10)

---

## 4단계: WSL 설치 (재시작 후)

재시작이 끝난 뒤, **관리자 PowerShell**에서 아래 명령을 실행하세요.  
(`wsl`과 `--install` 사이에 **공백**이 있어야 합니다.)

```powershell
wsl --install
```

Ubuntu가 자동으로 설치됩니다. 완료 후 다시 한 번 재시작하라는 메시지가 나올 수 있습니다.

---

## 5단계: Claude Code 설치 (WSL 정상 동작 후)

WSL이 정상적으로 설치·실행되면, **WSL 터미널**(Ubuntu 등)을 열고:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

---

## 요약 체크리스트

| 순서 | 작업 | 완료 |
|------|------|------|
| 1 | `enable_wsl_features.ps1` 실행 또는 DISM 두 줄 실행 | ☐ |
| 2 | PC 재시작 | ☐ |
| 3 | (오류 계속 시) BIOS에서 가상화( VT-x / AMD-V ) Enabled | ☐ |
| 4 | `wsl --install` 실행 (공백 주의) | ☐ |
| 5 | WSL 터미널에서 Claude Code 설치 스크립트 실행 | ☐ |

---

**참고:**  
- 명령어는 `wsl--install`이 아니라 `wsl --install` (공백 필수)  
- 가이드: https://aka.ms/enablevirtualization
