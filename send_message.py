import anthropic
import requests
import os
import sys
import datetime


REBBE_LETTER = """בעת רצון יזכירו אותך על הציון הקדוש של כ"ק מו"ח אדמו"ר זצוקללה"ה נבג"מ זי"ע, לבשר בשורות טובות באמור למעלה.

ובהכירי אותך ואת משפחתך בכלל, מיותר להדגיש, שאני מתפלא על קטנות הביטחון בהשם יתברך, אשר הוא משגיח בהשגחה פרטית על כל אחד עד לפרט הקטן ביותר, ובפרט במקרה שלך, שראית את חסדי השם יתברך מספר פעמים, מה שחייב הרי להביא באופן הגיוני להתחזקות בביטחון בהשם יתברך, ולפחות דאגה, ולקבוע עתים לתורה, ולקיים מצוות בשמחה וטוב לבב, ושלא לשים לב לכך שהיצר הרע מנסה לשכנע אחרת, ולא לחינם הרי נקרא היצר הרע – "זקן וכסיל".

אני מקווה שעד הזמן שתקבל את מכתבי זה, יהיה כבר שיפור, ותוכל לבשר בשורות טובות בכל זה.
ותרשום תזכורת מהרבי לא ליפול לעולם לעצת היצר"""


TOPICS = [
    ("כוח ההקשבה", "הרבי לימד שהבעל שיודע לשתוק ולשמוע את אשתו — בלי לצאת להגן על עצמו — הוא הבעל שאשתו תאהב מעומק ליבה. תן דוגמה מעשית: איך קשב עמוק משנה את האווירה בבית."),
    ("שמחה בבית", "הרבי הדגיש שוב ושוב שהשמחה היא עמוד השדרה של הבית היהודי — לא שמחה מזויפת, אלא שמחה שנבנית במודע. תן טיפ מעשי קטן להכניס שמחה לבית היום."),
    ("כבוד האשה", "הרבי כתב שהאשה היא עקרת הבית — לא כי היא 'עקורה' מהעולם, אלא כי היא ה*עיקר* שלו. תסביר מה זה אומר בפועל ואיך הבעל יכול לבטא זאת היום."),
    ("ויתור וסליחה", "הרבי לימד ששלום בית לא נבנה כשכל אחד 'צודק' — אלא כשכל אחד בוחר בשלום על פני ניצחון. תן דוגמה מעשית של ויתור שמחזק ולא מחליש."),
    ("דיבור ותקשורת", "הרבי כתב שמילה אחת שנאמרת בנחת שווה יותר ממאה מילים שנאמרות בכעס. תן כלי מעשי לשיחה שמקרבת ולא מרחיקה."),
    ("הבית כמקדש", "הרבי לימד שהבית היהודי הוא 'מקדש מעט' — המקום שבו שכינה שורה. תסביר איך כל מעשה קטן בבית — ארוחה, מגע, שיחה — יכול להיות קדוש."),
    ("צמיחה משותפת", "הרבי לימד שבני זוג לא רק חיים ביחד — הם גדלים ביחד. כשאחד עולה, הוא מרים את השני. תן דוגמה לאיך לתמוך בחלומות של בן/בת הזוג."),
    ("נוכחות מלאה", "הרבי דיבר על כך שהמתנה הגדולה ביותר שאפשר לתת לבן/בת הזוג היא נוכחות אמיתית — לא גוף שיושב ליד עם מחשבות אחרות. תן פעולה קטנה שמגלמת נוכחות מלאה."),
    ("הכרת תודה", "הרבי לימד שהכרת תודה היא יסוד העבודה עם ה' — וגם יסוד הזוגיות. בני זוג שמתרגלים להודות זה לזה מדי יום יוצרים קשר שמתחזק עם הזמן."),
    ("אחדות הנשמות", "הרבי לימד שנשמות בני הזוג היו אחת לפני הירידה לעולם, ונישואין הם לא 'פגישה של שניים' אלא 'חזרה לשלמות'. תסביר איך ראייה זו משנה את כל הקשר."),
]


def generate_zugiyut_message():
    now = datetime.datetime.utcnow()
    is_saturday = now.weekday() == 5
    shabbat_prefix = "פתח עם: 'שבוע טוב ומבורך! ✨'\n" if is_saturday else ""

    day_of_year = now.timetuple().tm_yday
    topic_name, topic_guidance = TOPICS[day_of_year % len(TOPICS)]

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": f"""כתוב מסר יומי לקבוצת ווטסאפ על זוגיות מתורת הרבי מליובאוויטש.

נושא היום: *{topic_name}*
כיוון: {topic_guidance}

דרישות:
- התמקד אך ורק בנושא שצוין — אל תפזר לנושאים אחרים
- השתמש בלפחות ציטוט אחד ספציפי של הרבי (ממכתב, שיחה, או התוועדות — לא פסוקי תנך)
- כתוב בעברית חיה ובגובה עיניים
- 4-6 שורות בלבד
- אמוג'ים רלוונטיים
- סיים עם שאלה לעיון או פעולה קטנה אחת להיום
{shabbat_prefix}
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
    message_type = os.environ.get("MESSAGE_TYPE", "letter")
    if message_type == "auto":
        # 08:00 IL slot triggered daily by cron-job.org — zugiyut, never on Shabbat
        # (the Motzaei Shabbat zugiyut comes via its own cron with an explicit type).
        if datetime.datetime.now(datetime.timezone.utc).weekday() == 5:
            print("Shabbat - skipping send")
            sys.exit(0)
        message_type = "zugiyut"
    if message_type == "zugiyut":
        msg = generate_zugiyut_message()
    else:
        msg = REBBE_LETTER
    print(f"Type: {message_type}")
    print(f"Message:\n{msg}\n".encode('utf-8', errors='replace').decode('utf-8'))
    send_whatsapp(msg)
