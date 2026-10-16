# claude-desktop-hebrew

ממשק בעברית ל-Claude Desktop (Windows), כולל היפוך לכיוון RTL.

**סטטוס: בפיתוח.** מנגנון ההוספה של שפה עובד (נבדק על עותק של האפליקציה); התרגום המלא של ~34,500 המחרוזות בתהליך.

## איך זה עובד
- ממשק האפליקציה הוא אתר מקומי ב-`resources\ion-dist` (מחוץ ל-app.asar, לכן אין צורך לשנות את ה-EXE).
- `patcher/hebrew_patch.py` מוסיף `he-IL` לרשימות השפות, יוצר `i18n/he-IL.json` מתוך `translations/he.json` (אנגלית ← עברית, לפי טקסט ולא לפי מפתח, כדי לשרוד עדכוני גרסה), ומזריק `assets/he-rtl.js` שמהפך ל-RTL כשהשפה עברית.
- מחרוזת שלא תורגמה נשארת באנגלית.

## שימוש
```
python patcher/hebrew_patch.py            # מתקין (מבקש הרשאות מנהל)
python patcher/hebrew_patch.py --revert   # מחזיר את המקור
```
אחרי כל עדכון של Claude צריך להריץ שוב. בהגדרות ← שפה בוחרים עברית.

## פיתוח
`tools/validate.py` בודק שתרגום שומר על משתני ICU ותגיות; `tools/merge.py` ממזג תרגומים ל-`translations/he.json`.
