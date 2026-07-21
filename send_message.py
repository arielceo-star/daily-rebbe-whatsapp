import requests
import os
import sys
import datetime


REBBE_LETTER = """בעת רצון יזכירו אותך על הציון הקדוש של כ"ק מו"ח אדמו"ר זצוקללה"ה נבג"מ זי"ע, לבשר בשורות טובות באמור למעלה.

ובהכירי אותך ואת משפחתך בכלל, מיותר להדגיש, שאני מתפלא על קטנות הביטחון בהשם יתברך, אשר הוא משגיח בהשגחה פרטית על כל אחד עד לפרט הקטן ביותר, ובפרט במקרה שלך, שראית את חסדי השם יתברך מספר פעמים, מה שחייב הרי להביא באופן הגיוני להתחזקות בביטחון בהשם יתברך, ולפחות דאגה, ולקבוע עתים לתורה, ולקיים מצוות בשמחה וטוב לבב, ושלא לשים לב לכך שהיצר הרע מנסה לשכנע אחרת, ולא לחינם הרי נקרא היצר הרע – "זקן וכסיל".

אני מקווה שעד הזמן שתקבל את מכתבי זה, יהיה כבר שיפור, ותוכל לבשר בשורות טובות בכל זה.
ותרשום תזכורת מהרבי לא ליפול לעולם לעצת היצר"""


def build_zugiyut_message():
    """Daily zugiyut message: a rotation of 20 letters of the Rebbe about
    shalom bayit / marriage. The quote is verbatim from Igrot Kodesh
    (chabadlibrary.org); each entry also carries a short plain-Hebrew
    explanation and a small daily action, written once and fixed in
    igrot_zugiyut.json - nothing is generated at send time."""
    import json
    is_motzaei_shabbat = (
        datetime.datetime.now(datetime.timezone.utc).weekday() == 5)
    prefix = "שבוע טוב ומבורך! ✨\n\n" if is_motzaei_shabbat else ""
    bank_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "igrot_zugiyut.json")
    with open(bank_path, encoding="utf-8") as f:
        bank = json.load(f)
    day_of_year = datetime.date.today().timetuple().tm_yday
    entry = bank[day_of_year % len(bank)]
    return (f"{prefix}💍 *מסר יומי לזוגיות — מאגרות הקודש של הרבי*\n\n"
            f"✍️ הרבי כותב:\n\"{entry['quote']}\"\n"
            f"_(אגרות קודש {entry['volume']}, אגרת {entry['letter']})_\n\n"
            f"💡 *בפשטות:* {entry['explain']}\n\n"
            f"✅ *משימה להיום:* {entry['task']}")


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
        # 08:00 IL slot triggered daily by cron-job.org — zugiyut, never on
        # Shabbat (Motzaei Shabbat comes via its own cron with explicit type).
        if datetime.datetime.now(datetime.timezone.utc).weekday() == 5:
            print("Shabbat - skipping send")
            sys.exit(0)
        message_type = "zugiyut"
    if message_type == "zugiyut":
        msg = build_zugiyut_message()
    else:
        msg = REBBE_LETTER
    print(f"Type: {message_type}")
    print(f"Message:\n{msg}\n".encode('utf-8', errors='replace').decode('utf-8'))
    send_whatsapp(msg)
