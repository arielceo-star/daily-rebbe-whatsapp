import requests
import os
import sys
import time
import re
import datetime

try:
    import brotli
except ImportError:
    brotli = None


REBBE_LETTER = """בעת רצון יזכירו אותך על הציון הקדוש של כ"ק מו"ח אדמו"ר זצוקללה"ה נבג"מ זי"ע, לבשר בשורות טובות באמור למעלה.

ובהכירי אותך ואת משפחתך בכלל, מיותר להדגיש, שאני מתפלא על קטנות הביטחון בהשם יתברך, אשר הוא משגיח בהשגחה פרטית על כל אחד עד לפרט הקטן ביותר, ובפרט במקרה שלך, שראית את חסדי השם יתברך מספר פעמים, מה שחייב הרי להביא באופן הגיוני להתחזקות בביטחון בהשם יתברך, ולפחות דאגה, ולקבוע עתים לתורה, ולקיים מצוות בשמחה וטוב לבב, ושלא לשים לב לכך שהיצר הרע מנסה לשכנע אחרת, ולא לחינם הרי נקרא היצר הרע – "זקן וכסיל".

אני מקווה שעד הזמן שתקבל את מכתבי זה, יהיה כבר שיפור, ותוכל לבשר בשורות טובות בכל זה.
ותרשום תזכורת מהרבי לא ליפול לעולם לעצת היצר"""


# "Hayom Yom" - compiled by the Rebbe. Text is fetched verbatim from the
# official Chabad-Lubavitch library (chabadlibrary.org) - no AI, no rewording.
CHABAD_LIBRARY_API = "https://chabadlibrary.org/books/api/main"
HAYOM_YOM_BOOK_ID = 3700000000
FALLBACK_LINK = "https://he.chabad.org/dailystudy/hayomyom.asp"

# hebcal English month name -> month heading in the sefer
HEBCAL_TO_BOOK_MONTH = {
    "Tishrei": ["תשרי"],
    "Cheshvan": ["חשון"],
    "Kislev": ["כסלו"],
    "Tevet": ["טבת"],
    "Sh'vat": ["שבט"],
    "Shvat": ["שבט"],
    "Adar": ["אדר א", "אדר ב"],  # regular year: learn both entries
    "Adar I": ["אדר א"],
    "Adar II": ["אדר ב"],
    "Nisan": ["ניסן"],
    "Iyyar": ["אייר"],
    "Sivan": ["סיון"],
    "Tamuz": ["תמוז"],
    "Av": ["מנחם אב"],
    "Elul": ["אלול"],
}


def heb_day_letters(n):
    ones = ["", "א", "ב", "ג", "ד", "ה", "ו", "ז", "ח", "ט"]
    if n == 15:
        return "טו"
    if n == 16:
        return "טז"
    tens = ["", "י", "כ", "ל"][n // 10]
    return tens + ones[n % 10]


def api_get(path):
    last_err = None
    for attempt in range(4):
        try:
            r = requests.get(CHABAD_LIBRARY_API, params={"path": path},
                             timeout=30, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            raw = r.content
            try:
                text = raw.decode("utf-8")
                if not text.strip().startswith(("{", "[")):
                    raise ValueError("not json")
            except (UnicodeDecodeError, ValueError):
                if brotli is None:
                    raise
                text = brotli.decompress(raw).decode("utf-8")
            import json
            return json.loads(text)
        except Exception as e:
            last_err = e
            time.sleep(3 * (attempt + 1))
    raise last_err


def clean_html(s):
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    return s.strip()


def get_hebrew_date():
    r = requests.get("https://www.hebcal.com/converter",
                     params={"cfg": "json", "g2h": 1,
                             "date": datetime.date.today().isoformat()},
                     timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_hayom_yom():
    hebdate = get_hebrew_date()
    hm, hd = hebdate["hm"], int(hebdate["hd"])
    display_date = hebdate.get("hebrew", f"{heb_day_letters(hd)} {hm}")
    display_date = re.sub(r"[֑-ׇ]", "", display_date)  # strip nikud
    book_months = HEBCAL_TO_BOOK_MONTH[hm]
    day_letters = heb_day_letters(hd)

    book = api_get(f"/{HAYOM_YOM_BOOK_ID}")
    sections = book["content"]["data"]

    entries = []
    for month_name in book_months:
        month_ids = [s["id"] for s in sections
                     if clean_html(s["heading"]) == month_name]
        day_id = None
        for mid in month_ids:
            month = api_get(f"/{mid}")
            for day in month["content"]["data"]:
                heading = clean_html(day["heading"])
                if heading.split()[0] == day_letters:
                    day_id = day["id"]
                    day_heading = heading
                    break
            if day_id:
                break
        if not day_id:
            raise LookupError(f"day {day_letters} not found in {month_name}")
        page = api_get(f"/{day_id}")
        text = clean_html(page["content"]["data"]["text"])
        entries.append((day_heading, text))

    body = "\n\n".join(
        (f"*{h}*\n{t}" if len(entries) > 1 else t) for h, t in entries)
    return display_date, body


def build_hayom_yom_message():
    is_motzaei_shabbat = (
        datetime.datetime.now(datetime.timezone.utc).weekday() == 5)
    prefix = "שבוע טוב ומבורך! ✨\n\n" if is_motzaei_shabbat else ""
    try:
        display_date, body = fetch_hayom_yom()
        return (f"{prefix}📖 *היום יום • {display_date}*\n\n"
                f"{body}\n\n"
                f'_(מתוך לוח "היום יום" שערך הרבי מליובאוויטש — '
                f"ספריית חב\"ד ליובאוויטש)_")
    except Exception as e:
        print(f"Hayom Yom fetch failed: {e}", file=sys.stderr)
        return (f"{prefix}📖 *היום יום*\n\n"
                f"הלימוד היומי באתר חב״ד:\n{FALLBACK_LINK}")


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
        # 08:00 IL slot triggered daily by cron-job.org — Hayom Yom, never on
        # Shabbat (Motzaei Shabbat comes via its own cron with explicit type).
        if datetime.datetime.now(datetime.timezone.utc).weekday() == 5:
            print("Shabbat - skipping send")
            sys.exit(0)
        message_type = "zugiyut"
    if message_type == "zugiyut":  # slot name kept for workflow compatibility
        msg = build_hayom_yom_message()
    else:
        msg = REBBE_LETTER
    print(f"Type: {message_type}")
    print(f"Message:\n{msg}\n".encode('utf-8', errors='replace').decode('utf-8'))
    send_whatsapp(msg)
