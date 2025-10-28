from openai import OpenAI

client = OpenAI()

async def chat_structured(system: str, messages: list, schema: dict, extra_context=None):
    """Send a chat completion request with a JSON schema tool and return the parsed arguments."""
    # Prepare messages with system and optional extra context
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    if extra_context:
        msgs.append({"role": "system", "content": f"\u88dc\u5145\u8cc7\u6599\uff1a{extra_context}"})
    msgs.extend(messages)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=msgs,
        tools=[{
            "type": "json_schema",
            "json_schema": {
                "name": "plan",
                "schema": {
                    "type": "object",
                    "properties": schema,
                    "required": ["steps"],
                },
            },
        }],
        tool_choice={"type": "tool", "name": "plan"},
    )
    # Extract the tool call arguments (parsed JSON) if present
    choice = response.choices[0]
    if choice.message.tool_calls:
        return choice.message.tool_calls[0].args
    return {}
