import requests
import os


DAILY_MESSAGE = """בעת רצון יזכירו אותך על הציון הקדוש של כ"ק מו"ח אדמו"ר זצוקללה"ה נבג"מ זי"ע, לבשר בשורות טובות באמור למעלה.

ובהכירי אותך ואת משפחתך בכלל, מיותר להדגיש, שאני מתפלא על קטנות הביטחון בהשם יתברך, אשר הוא משגיח בהשגחה פרטית על כל אחד עד לפרט הקטן ביותר, ובפרט במקרה שלך, שראית את חסדי השם יתברך מספר פעמים, מה שחייב הרי להביא באופן הגיוני להתחזקות בביטחון בהשם יתברך, ולפחות דאגה, ולקבוע עתים לתורה, ולקיים מצוות בשמחה וטוב לבב, ושלא לשים לב לכך שהיצר הרע מנסה לשכנע אחרת, ולא לחינם הרי נקרא היצר הרע – "זקן וכסיל".

אני מקווה שעד הזמן שתקבל את מכתבי זה, יהיה כבר שיפור, ותוכל לבשר בשורות טובות בכל זה.
ותרשום תזכורת מהרבי לא ליפול לעולם לעצת היצר"""


def generate_message():
    return DAILY_MESSAGE


def send_whatsapp(message):
    instance = os.environ["GREEN_API_INSTANCE"]
    token = os.environ["GREEN_API_TOKEN"]
    url_base = os.environ["GREEN_API_URL"]
    phone = os.environ["WHATSAPP_PHONE"]
    url = f"{url_base}/waInstance{instance}/sendMessage/{token}"
    resp = requests.post(url, json={"chatId": phone, "message": message})
    resp.raise_for_status()
    print(f"Sent! ID: {resp.json().get('idMessage')}")


if __name__ == "__main__":
    msg = generate_message()
    print(f"Message:\n{msg}\n".encode('utf-8', errors='replace').decode('utf-8'))
    send_whatsapp(msg)
