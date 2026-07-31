"""
Rebuild embed.html with current snapshot_data.json.
Run this after manually editing the JSON.

Usage: python rebuild_embed.py
"""
import json
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'snapshot_data.json')
EMBED_FILE = os.path.join(BASE_DIR, 'embed.html')

data = json.load(open(DATA_FILE, encoding='utf-8'))

mini = []
for e in data['entries']:
    files = e.get('sourceFiles', [])
    mini.append({
        'i': e['issue'],
        'd': e['date'],
        'n': e['name'],
        'r': e['role'],
        'c': e['client'],
        'rc': e.get('roleCategory', ''),
        'sp': e.get('specialism', ''),
        'a': e.get('academy'),
        's': e.get('sector', ''),
        'rl': e.get('relocated', False),
        'f': files[0] if files else '',
    })

mini_json = json.dumps(mini, separators=(',', ':'))

with open(EMBED_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(
    r'const D=\[.*?\];',
    f'const D={mini_json};',
    content,
    count=1,
    flags=re.DOTALL
)

with open(EMBED_FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Done - embed.html updated with {len(mini)} entries")
