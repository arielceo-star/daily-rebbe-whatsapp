import anthropic
import requests
import os
import datetime
import zoneinfo


TOPICS = [
    "ביטחון בהשם והשגחה פרטית",
    "שמחה כדרך חיים",
    "שלום בית ואהבה בין בני זוג",
    "פרנסה ומנוחת הנפש",
    "חינוך הילדים באהבה",
    "אמונה בזמנים של אתגר",
    "כוחה של תפילה",
    "אהבת ישראל",
    "קביעת עתים לתורה",
    "התגברות על עצת היצר",
    "הכרת תודה על חסדי השם",
    "שליחות ותכלית הנשמה",
    "בריאות הגוף והנפש",
    "מידת הביטחון מול הדאגה",
]


def generate_message():
    now = datetime.datetime.now(zoneinfo.ZoneInfo("Asia/Jerusalem"))
    is_evening = now.hour >= 15
    slot_name = "ערב" if is_evening else "בוקר"
    is_motzaei_shabbat = now.weekday() == 5 and is_evening
    opening_rule = (
        "פתח עם: 'שבוע טוב ומבורך! ✨'\n"
        if is_motzaei_shabbat
        else f"פתח עם: '📜 מכתב מהרבי — {slot_name} טוב!'\n"
    )

    slot_index = now.timetuple().tm_yday * 2 + (1 if is_evening else 0)
    topic = TOPICS[slot_index % len(TOPICS)]

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=700,
        messages=[{"role": "user", "content": f"""הבא קטע ממכתב אמיתי של הרבי מליובאוויטש מתוך אגרות קודש, בנושא: *{topic}*.

דרישות:
- צטט נאמנה את לשון המכתב (אם המקור באידיש — תרגם לעברית בהירה), אל תמציא מכתב שלא קיים
- ציין את המקור בסוף (למשל: אגרות קודש, כרך ומספר האיגרת, או תאריך המכתב)
- הוסף אחרי הציטוט שורה או שתיים של יישום מעשי להיום, בגובה עיניים
- אורך כולל: 6-9 שורות
- אמוג'ים במידה
{opening_rule}
החזר רק את טקסט ההודעה, ללא הסברים."""}]
    )
    return response.content[0].text


def get_phones():
    raw = os.environ.get("WHATSAPP_PHONES") or os.environ["WHATSAPP_PHONE"]
    phones = []
    for p in raw.split(","):
        p = p.strip()
        if not p:
            continue
        if "@" not in p:
            p = p + "@c.us"
        phones.append(p)
    return phones


def send_whatsapp(message):
    instance = os.environ["GREEN_API_INSTANCE"]
    token = os.environ["GREEN_API_TOKEN"]
    url_base = os.environ["GREEN_API_URL"]
    url = f"{url_base}/waInstance{instance}/sendMessage/{token}"
    for phone in get_phones():
        resp = requests.post(url, json={"chatId": phone, "message": message})
        resp.raise_for_status()
        print(f"Sent to {phone}! ID: {resp.json().get('idMessage')}")


if __name__ == "__main__":
    msg = generate_message()
    print(f"Message:\n{msg}\n".encode('utf-8', errors='replace').decode('utf-8'))
    send_whatsapp(msg)
