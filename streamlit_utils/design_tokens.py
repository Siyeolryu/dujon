"""
디자인 토큰 중앙 저장소.
theme.py · css/style.css · .streamlit/config.toml에 분산된 값을 한곳에 모아
바이브코딩 시 복붙 없이 참조할 수 있도록 합니다.

사용법:
    from streamlit_utils.design_tokens import T
    color = T.COLOR_PRIMARY
"""


class _Tokens:
    """더존건설 Modern Minimal Premium 디자인 토큰."""

    # ── 색상: 브랜드 ──
    COLOR_PRIMARY = "#0d6efd"
    COLOR_PRIMARY_HOVER = "#0b5ed7"
    COLOR_PRIMARY_DARK = "#0a58ca"
    COLOR_PRIMARY_SHADOW = "rgba(13,110,253,0.3)"

    # ── 색상: 배경 ──
    BG_APP = "#F8F9FA"        # Streamlit config: backgroundColor
    BG_CARD = "#FFFFFF"       # secondaryBackgroundColor
    BG_HOVER = "#f8f9fa"
    BG_MUTED = "#f1f3f5"

    # ── 색상: 텍스트 ──
    TEXT_HEADING = "#1a1d21"
    TEXT_BODY = "#2c3e50"      # Streamlit config: textColor
    TEXT_SECONDARY = "#495057"
    TEXT_MUTED = "#6c757d"
    TEXT_PLACEHOLDER = "#adb5bd"

    # ── 색상: 보더 ──
    BORDER_DEFAULT = "#dee2e6"  # Streamlit config: widgetBorderColor
    BORDER_LIGHT = "#e9ecef"
    BORDER_LIGHTEST = "#f1f3f5"

    # ── 색상: 상태(파스텔) ──
    STATUS_SUCCESS = "#10b981"
    STATUS_SUCCESS_BG = "#d1fae5"
    STATUS_SUCCESS_TEXT = "#065f46"

    STATUS_DANGER = "#ef4444"
    STATUS_DANGER_BG = "#fee2e2"
    STATUS_DANGER_TEXT = "#991b1b"

    STATUS_WARNING = "#f59e0b"
    STATUS_WARNING_BG = "#fef3c7"
    STATUS_WARNING_TEXT = "#92400e"

    STATUS_INFO = "#3b82f6"
    STATUS_INFO_BG = "#dbeafe"
    STATUS_INFO_TEXT = "#1e40af"

    STATUS_NEUTRAL = "#6b7280"
    STATUS_NEUTRAL_BG = "#f3f4f6"
    STATUS_NEUTRAL_TEXT = "#6b7280"

    # ── 타이포그래피 ──
    FONT_FAMILY = "'Segoe UI', 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif"
    FONT_SIZE_XS = "12px"
    FONT_SIZE_SM = "13px"
    FONT_SIZE_BASE = "14px"
    FONT_SIZE_MD = "16px"
    FONT_SIZE_LG = "18px"
    FONT_SIZE_XL = "20px"
    FONT_SIZE_KPI = "36px"
    FONT_SIZE_METRIC = "28px"
    FONT_WEIGHT_NORMAL = "400"
    FONT_WEIGHT_MEDIUM = "500"
    FONT_WEIGHT_SEMIBOLD = "600"
    FONT_WEIGHT_BOLD = "700"
    LETTER_SPACING_TIGHT = "-0.02em"

    # ── 공간 ──
    SPACE_XS = "4px"
    SPACE_SM = "8px"
    SPACE_MD = "12px"
    SPACE_BASE = "16px"
    SPACE_LG = "20px"
    SPACE_XL = "24px"
    SPACE_2XL = "32px"

    # ── 모서리 ──
    RADIUS_SM = "4px"
    RADIUS_MD = "8px"
    RADIUS_LG = "12px"
    RADIUS_PILL = "9999px"

    # ── 그림자 ──
    SHADOW_SM = "0 1px 3px rgba(0,0,0,0.06)"
    SHADOW_MD = "0 2px 8px rgba(0,0,0,0.06)"
    SHADOW_LG = "0 8px 24px rgba(0,0,0,0.12)"
    SHADOW_PRIMARY = "0 2px 4px rgba(13,110,253,0.3)"
    SHADOW_PRIMARY_HOVER = "0 4px 8px rgba(13,110,253,0.4)"

    # ── 트랜지션 ──
    TRANSITION_DEFAULT = "all 0.2s ease"
    TRANSITION_SLIDE = "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"

    # ── 브레이크포인트 ──
    BP_MOBILE = "480px"
    BP_TABLET = "768px"
    BP_DESKTOP = "1024px"

    # ── 레이아웃 ──
    CONTENT_PADDING = "20px 24px 32px 24px"
    KPI_CARD_MIN_WIDTH = "180px"
    FORM_MAX_WIDTH = "800px"

    # ── 상태 매핑: 배정상태 → 색상 클래스 ──
    ASSIGNMENT_STATUS_MAP = {
        "배정완료": "success",
        "미배정": "danger",
    }

    # ── 상태 매핑: 현장상태 → 색상 클래스 ──
    SITE_STATE_MAP = {
        "건축허가": "neutral",
        "착공예정": "info",
        "공사 중": "warning",
        "공사 중단": "danger",
        "준공": "success",
    }

    # ── 상태 매핑: 인력상태 → 색상 클래스 ──
    PERSONNEL_STATUS_MAP = {
        "투입가능": "success",
        "투입중": "warning",
        "휴가": "neutral",
        "퇴사": "danger",
    }

    # ── 상태 매핑: 자격증 → 색상 클래스 ──
    CERTIFICATE_STATUS_MAP = {
        "사용가능": "success",
        "사용중": "warning",
        "만료": "danger",
    }

    # ── 차트 기본 팔레트 ──
    CHART_PALETTE = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"]

    def status_color(self, status: str, domain: str = "assignment") -> dict:
        """상태값에 대응하는 {bg, border, text} 색상 dict 반환.

        Args:
            status: 상태 문자열 (예: '배정완료', '투입가능')
            domain: 'assignment' | 'site_state' | 'personnel' | 'certificate'
        """
        maps = {
            "assignment": self.ASSIGNMENT_STATUS_MAP,
            "site_state": self.SITE_STATE_MAP,
            "personnel": self.PERSONNEL_STATUS_MAP,
            "certificate": self.CERTIFICATE_STATUS_MAP,
        }
        cls = maps.get(domain, {}).get(status, "neutral")
        return {
            "success": {"bg": self.STATUS_SUCCESS_BG, "border": self.STATUS_SUCCESS, "text": self.STATUS_SUCCESS_TEXT},
            "danger":  {"bg": self.STATUS_DANGER_BG,  "border": self.STATUS_DANGER,  "text": self.STATUS_DANGER_TEXT},
            "warning": {"bg": self.STATUS_WARNING_BG, "border": self.STATUS_WARNING, "text": self.STATUS_WARNING_TEXT},
            "info":    {"bg": self.STATUS_INFO_BG,    "border": self.STATUS_INFO,    "text": self.STATUS_INFO_TEXT},
            "neutral": {"bg": self.STATUS_NEUTRAL_BG, "border": self.STATUS_NEUTRAL, "text": self.STATUS_NEUTRAL_TEXT},
        }[cls]


# 모듈-레벨 싱글턴
T = _Tokens()
