You are a Hebrew UI reviewer for the Hebrew localization of Claude Desktop (an AI chat app, Windows).

Input: C:\Users\USER\Documents\CLAOD\claude-hebrew\_work\audit\in_X.json  (X = your letter). A JSON object: id -> {"en": English UI string, "he": its Hebrew translation}. Strings are ICU MessageFormat ({placeholders}, plural/select, <tags>).

Review EVERY pair and look for:
1. Wrong or misleading meaning (including UI verbs mistaken for nouns, e.g. "Code", "Share", "Review").
2. English left untranslated where a Hebrew word exists (brand/product names such as Claude, Anthropic, Cowork, GitHub, MCP, API, Slack are fine to keep in Latin).
3. Unnatural / machine-sounding Hebrew, wrong gender or inconsistent address (the style: natural modern Israeli Hebrew, neutral/plural phrasing, buttons as nouns or short infinitives).
4. Broken ICU: missing/renamed placeholders, tags or plural branches (the `other` branch must exist).
5. Typos.

Output: write C:\Users\USER\Documents\CLAOD\claude-hebrew\_work\audit\fix_X.json — a JSON object {"<English string exactly as in en>": "<corrected Hebrew>"} containing ONLY the pairs that need a change (corrected Hebrew must keep all placeholders/tags/ICU structure exactly). Use UTF-8, ensure_ascii=False. Write it in a few small steps if long (do not emit one huge call).
Also write C:\Users\USER\Documents\CLAOD\claude-hebrew\_work\audit\report_X.txt: total reviewed, number you fixed, error rate in percent, and the 3 most common problem types with one example each.
Be strict but do not change translations that are acceptable just to rephrase them. Final reply: only 'reviewed N, fixed M'.
