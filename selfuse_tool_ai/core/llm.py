from openai import OpenAI
import os

_client = None

def reset_client():
    """Reset the OpenAI client (force re-initialization)."""
    global _client
    _client = None

def get_client():
    """Get or create OpenAI client."""
    global _client
    if _client is None:
        # 明確從環境變數讀取 API key
        api_key = os.environ.get("OPENAI_API_KEY")

        # 如果環境變數中沒有，嘗試從 secure_config 載入
        if not api_key:
            try:
                # 動態導入避免循環依賴
                import sys
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                if project_root not in sys.path:
                    sys.path.insert(0, project_root)

                from src.core.secure_config import get_openai_api_key
                api_key = get_openai_api_key()
                if api_key:
                    os.environ["OPENAI_API_KEY"] = api_key
            except Exception as e:
                pass

        if not api_key:
            raise ValueError(
                "OpenAI API key not found. Please set OPENAI_API_KEY environment variable "
                "or configure it in the settings."
            )

        _client = OpenAI(api_key=api_key)
    return _client

async def chat_structured(system: str, messages: list, schema: dict, extra_context=None):
    """Send a chat completion request with a JSON schema tool and return the parsed arguments."""
    # Prepare messages with system and optional extra context
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    if extra_context:
        msgs.append({"role": "system", "content": f"\u88dc\u5145\u8cc7\u6599\uff1a{extra_context}"})
    msgs.extend(messages)

    client = get_client()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=msgs,
        tools=[{
            "type": "function",
            "function": {
                "name": "plan",
                "description": "Generate a plan with steps to accomplish the user's goal",
                "parameters": {
                    "type": "object",
                    "properties": schema,
                    "required": ["steps"],
                },
            },
        }],
        tool_choice={"type": "function", "function": {"name": "plan"}},
    )
    # Extract the tool call arguments (parsed JSON) if present
    choice = response.choices[0]
    if choice.message.tool_calls:
        import json
        return json.loads(choice.message.tool_calls[0].function.arguments)
    return {}
