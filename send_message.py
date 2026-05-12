import anthropic
import requests
import os
import datetime

def generate_message():
      is_saturday = datetime.datetime.utcnow().weekday() == 5

    shabbat_prefix = "הוסף בתחילה: 'שבוע טוב ומבורך! ' " if is_saturday else ""

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(
              model="claude-sonnet-4-6",
              max_tokens=500,
              messages=[{
                            "role": "user",
                            "content": f"""כתוב מסר יומי קצר לקבוצת ווטסאפ על שלום בית וזוגיות, המבוסס על תורת הרבי מליובאוויטש.

                            דרישות:
                            - השתמש בציטוט מקורי של הרבי ממכתב, שיחה, או התוועדות (לא פסוקי תנך)
                            - כתוב בעברית פשוטה ובגובה עיניים
                            - קצר - 4-6 שורות בלבד
                            - הוסף אמוג'ים רלוונטיים
                            - סיים עם שאלה קצרה לעיון או פעולה קטנה להיום
                            {shabbat_prefix}
                            החזר רק את טקסט ההודעה, ללא הסברים."""
              }]
    )
    return response.content[0].text

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
      print(f"Message:\n{msg}\n")
      send_whatsapp(msg)
