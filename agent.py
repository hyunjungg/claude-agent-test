"""Claude Agent SDK 최소 예제 (CLAUDE_CODE_OAUTH_TOKEN 사용)

  python agent.py alloc <함수소스파일>                # 1. 도구 없이, 보낸 코드만 보고 답변
  python agent.py find  <프로젝트디렉토리> <함수명>    # 2. 에이전트가 스스로 코드를 탐색해서 답변
"""
import asyncio, os, sys
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

# .env 의 CLAUDE_CODE_OAUTH_TOKEN 을 환경변수로 올림 (SDK 가 띄우는 CLI 가 이걸로 인증)
for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")):
    if "=" in line and not line.startswith("#"):
        k, v = line.strip().split("=", 1)
        os.environ.setdefault(k, v)


def ask(prompt: str, options: ClaudeAgentOptions) -> str:
    async def _run():
        result = None
        async for msg in query(prompt=prompt, options=options):   # 스트림은 끝까지 소비해야 함 (중간 return 금지)
            if isinstance(msg, ResultMessage):
                result = msg.result
        return result
    return asyncio.run(_run())


def check_alloc(func_src: str) -> str:
    prompt = ("다음 C 함수에서 memory allocation(malloc/calloc/realloc/xmalloc/strdup 등)이 "
              "발생하는지 확인해줘. 주어진 코드만 보고 답하고, 발생한다면 어느 줄인지 알려줘.\n\n"
              f"```c\n{func_src}\n```")
    return ask(prompt, ClaudeAgentOptions(tools=[]))


def find_definition(project_dir: str, func_name: str) -> str:
    prompt = (f"이 프로젝트에서 `{func_name}` 함수가 **정의**된 파일 경로와 라인 번호를 찾아줘. "
              "헤더의 선언(프로토타입)이 아니라 본문이 있는 정의여야 해.")
    return ask(prompt, ClaudeAgentOptions(cwd=project_dir, tools=["Glob", "Grep", "Read"]))


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "alloc":
        print(check_alloc(open(sys.argv[2]).read()))
    elif len(sys.argv) >= 4 and sys.argv[1] == "find":
        print(find_definition(sys.argv[2], sys.argv[3]))
    else:
        sys.exit(__doc__)
