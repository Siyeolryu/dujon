"""
더존건설 현장배정 관리 CLI Agent.
Anthropic Python SDK의 tool-use 기능을 활용한 대화형 터미널 에이전트.

실행: python -m agent.cli_agent
"""
import asyncio
import os
import sys

from anthropic import Anthropic
from dotenv import load_dotenv

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from agent.system_prompt import SYSTEM_PROMPT
from agent.tools import TOOLS, handle_tool
from agent.api_helpers import api


MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
MAX_TOKENS = 4096

BANNER = """
╔══════════════════════════════════════════════╗
║   더존건설 현장배정 관리 AI 어시스턴트       ║
║                                              ║
║   명령어 예시:                               ║
║   • 전체 통계 보여줘                         ║
║   • 미배정 현장 목록                         ║
║   • 투입가능한 인력 조회                     ║
║   • 종료 / quit / exit                       ║
╚══════════════════════════════════════════════╝
"""


def print_assistant(text: str):
    """어시스턴트 응답 출력."""
    print(f"\n🤖 어시스턴트> {text}\n")


async def run_agent():
    """메인 대화 루프."""
    client = Anthropic()
    messages = []

    print(BANNER)

    # API 서버 연결 확인
    health, err = await api.health_check()
    if err:
        print(f"⚠️  Flask API 서버 연결 실패: {err}")
        print("   'python run_api.py'로 API 서버를 먼저 실행하세요.\n")
    else:
        print("✅ Flask API 서버 연결 확인 완료\n")

    try:
        while True:
            # 사용자 입력
            try:
                user_input = input("사용자> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n👋 종료합니다.")
                break

            if not user_input:
                continue
            if user_input.lower() in ("종료", "quit", "exit", "q"):
                print("👋 종료합니다.")
                break

            # 대화 이력에 추가
            messages.append({"role": "user", "content": user_input})

            # Claude API 호출 → tool_use 루프
            while True:
                response = client.messages.create(
                    model=MODEL,
                    max_tokens=MAX_TOKENS,
                    system=SYSTEM_PROMPT,
                    tools=TOOLS,
                    messages=messages,
                )

                # 응답 처리
                assistant_content = response.content
                messages.append({"role": "assistant", "content": assistant_content})

                # stop_reason 확인
                if response.stop_reason == "end_turn":
                    # 텍스트 블록만 출력
                    for block in assistant_content:
                        if hasattr(block, "text"):
                            print_assistant(block.text)
                    break

                if response.stop_reason == "tool_use":
                    # 도구 호출 처리
                    tool_results = []
                    for block in assistant_content:
                        if block.type == "tool_use":
                            tool_name = block.name
                            tool_input = block.input
                            print(f"  🔧 [{tool_name}] 호출 중...")

                            result_text = await handle_tool(tool_name, dict(tool_input))

                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result_text,
                            })
                        elif hasattr(block, "text") and block.text:
                            # 도구 호출 전 텍스트가 있으면 출력
                            print_assistant(block.text)

                    # 도구 결과를 대화에 추가하고 다시 호출
                    messages.append({"role": "user", "content": tool_results})
                    continue

                # 그 외 (max_tokens 등)
                for block in assistant_content:
                    if hasattr(block, "text"):
                        print_assistant(block.text)
                break

    finally:
        await api.close()


def main():
    """진입점."""
    # ANTHROPIC_API_KEY 확인
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
        print("   .env 파일에 ANTHROPIC_API_KEY=sk-... 를 추가하세요.")
        sys.exit(1)

    asyncio.run(run_agent())


if __name__ == "__main__":
    main()
