import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
workspace = Path(__file__).resolve().parent / 'agent-workspace'
allowed_files = {'checker.py', 'description.txt'}

client = OpenAI(
    api_key=os.environ['LITELLM_TOKEN'],
    base_url=os.environ['DUKE_API_BASE'],
    timeout=30,
    max_retries=0,
)
model = os.environ['DUKE_MODEL']

tools = [{
    'type': 'function',
    'function': {
        'name': 'read_file',
        'description': 'Read one permitted contestant file from the isolated challenge workspace.',
        'parameters': {
            'type': 'object',
            'properties': {'filename': {'type': 'string', 'enum': sorted(allowed_files)}},
            'required': ['filename'],
            'additionalProperties': False,
        },
    },
}]

messages = [
    {'role': 'system', 'content': 'You are a CTF agent testing tool access. Call read_file to inspect checker.py. Never guess file contents.'},
    {'role': 'user', 'content': 'Inspect checker.py using the available tool, then briefly describe what you saw.'},
]

first = client.chat.completions.create(
    model=model, messages=messages, tools=tools, tool_choice='auto', max_tokens=250
)
message = first.choices[0].message
print('Model:', model)
print('Tool calls:', len(message.tool_calls or []))
if not message.tool_calls:
    print('Model response:', message.content)
    raise SystemExit('Model did not call a tool; check model tool support.')

messages.append(message.model_dump(exclude_none=True))
for call in message.tool_calls:
    if call.function.name != 'read_file':
        result = {'error': 'Tool not permitted'}
    else:
        try:
            args = json.loads(call.function.arguments)
            filename = args.get('filename')
            if filename not in allowed_files:
                raise ValueError('File not permitted')
            path = workspace / filename
            if path.is_symlink() or not path.is_file():
                raise ValueError('File missing or symlink not permitted')
            result = {'content': path.read_text(encoding='utf-8')[:6000]}
            print('Read file:', filename)
        except (ValueError, OSError, UnicodeError) as exc:
            result = {'error': str(exc)}
    messages.append({'role': 'tool', 'tool_call_id': call.id, 'content': json.dumps(result)})

second = client.chat.completions.create(
    model=model, messages=messages, max_tokens=180
)
print('Final response:', second.choices[0].message.content)
print('Total tokens:', sum((r.usage.total_tokens if r.usage else 0) for r in (first, second)))
