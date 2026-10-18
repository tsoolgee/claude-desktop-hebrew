Translate Claude Desktop native-shell strings (menus, dialogs, tray, notifications) from English to Hebrew.

Input: C:\Users\USER\Documents\CLAOD\claude-hebrew\_work\n\in_NNN.json (id -> English), NNN = your piece number.
Output: C:\Users\USER\Documents\CLAOD\claude-hebrew\_work\n\out_NNN.json — SAME ids, Hebrew values, UTF-8 JSON.

Translate yourself (no machine-translation API or script). Work in small steps: read the input, then write the output in 3-4 separate Python/Write calls (about 50 strings each, saved to part files out_NNN_a.json, out_NNN_b.json, ...), then merge them into out_NNN.json with ensure_ascii=False. Never emit one huge call.

Rules:
- Strings are ICU MessageFormat. Keep every {placeholder}, plural/select structure and keywords (plural, select, one, other, =0) and tags (<b>, <link>, <0>) EXACTLY; translate only the human text. Always keep the `other` branch.
- Keep Latin: Claude, Anthropic, Cowork, Claude Code, MCP, GitHub, Chrome, API, URL, code, extensions, key names, emoji, URLs.
- Style: natural modern Israeli Hebrew UI. Buttons/menus as nouns or short infinitives (שמירה, ביטול). Sentences gender-neutral/plural, avoid אתה/את.
- Glossary: chat=צ'אט, project=פרויקט, artifact=ארטיפקט, conversation=שיחה, Settings=הגדרות, connector=מחבר, extension=תוסף, skill=כישור.

Finally run: python C:\Users\USER\Documents\CLAOD\claude-hebrew\tools\validate.py <in> <out> and fix any reported ids; confirm all ids are present. Report only "done N, M failures".
