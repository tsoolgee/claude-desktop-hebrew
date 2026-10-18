Coverage check for the Hebrew localization of Claude Desktop.

Input: C:\Users\USER\Documents\CLAOD\claude-hebrew\_work\coverage_gaps.json with two lists:
- "no_he": id -> English string that is used in the app UI but currently has NO Hebrew translation (299 items). Most are brand/technical names that should stay in Latin (Claude, GitHub, OAuth, font names, social networks...). Some are real UI words that must be translated.
- "not_in_catalog": id -> English default string used in code but missing from the translation catalog (91 items). These cannot be translated through the catalog; just classify them.

Tasks:
1. For every item in "no_he": decide KEEP (brand / code / proper noun / technical term that Israeli users see in English) or TRANSLATE. For TRANSLATE items write natural modern Israeli Hebrew (ICU MessageFormat: keep {placeholders}, tags and plural/select structure exactly).
   Write C:\Users\USER\Documents\CLAOD\claude-hebrew\_work\gaps_he.json: {"<English string>": "<Hebrew>"} for the TRANSLATE items only (UTF-8, ensure_ascii=False; small steps, not one huge call).
2. Write C:\Users\USER\Documents\CLAOD\claude-hebrew\_work\gaps_report.txt with: how many KEEP vs TRANSLATE in "no_he"; for "not_in_catalog": how many look like user-visible text vs internal/debug strings, plus the 15 most user-visible examples.
Final reply: only 'translate N, keep M, not_in_catalog visible K'.
