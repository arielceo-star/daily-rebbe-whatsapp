import requests
import os


DAILY_MESSAGE = """בעת רצון יזכירו אותך על הציון הקדוש של כ"ק מו"ח אדמו"ר זצוקללה"ה נבג"מ זי"ע, לבשר בשורות טובות באמור למעלה.

ובהכירי אותך ואת משפחתך בכלל, מיותר להדגיש, שאני מתפלא על קטנות הביטחון בהשם יתברך, אשר הוא משגיח בהשגחה פרטית על כל אחד עד לפרט הקטן ביותר, ובפרט במקרה שלך, שראית את חסדי השם יתברך מספר פעמים, מה שחייב הרי להביא באופן הגיוני להתחזקות בביטחון בהשם יתברך, ולפחות דאגה, ולקבוע עתים לתורה, ולקיים מצוות בשמחה וטוב לבב, ושלא לשים לב לכך שהיצר הרע מנסה לשכנע אחרת, ולא לחינם הרי נקרא היצר הרע – "זקן וכסיל".

אני מקווה שעד הזמן שתקבל את מכתבי זה, יהיה כבר שיפור, ותוכל לבשר בשורות טובות בכל זה.
ותרשום תזכורת מהרבי לא ליפול לעולם לעצת היצר"""


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
    send_whatsapp(DAILY_MESSAGE)
