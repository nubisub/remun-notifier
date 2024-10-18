import os
import json
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def set_json(number):
    data = {
        "number": number
    }

    with open('number.json', 'w') as file:
        json.dump(data, file)
        
def get_data(number):
    url = f"https://jdih.setneg.go.id/front/Peraturan/ajaxview?id=P{number}"
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
        "Connection": "keep-alive",
        "Cookie": "ci_session=kv2hv8mdm6gs0mdchsmlcnd6ht0imjjt; CSRFCookie=4ffc891559efa0785ba36b8be670eec8; TS01e7ed0b=01f94ebe60b87597a0eea9571c292494bf84f5766b05ca5d46d6c14b4633805abfe98071f51e09f4e6dec3bdd8c8624ddf90cc2a5c55c90d978a85e4476a62d9f2cb8302cbbbc27fcecc5f0f053f6efa6f54b81f79; TSca2e059f027=086c094b6eab20009e0b3a333bfe010375d02efd919dc847ee953cdce7e72d7b6019f792e5a19ff40855ed9a3d11300068da1a6199230e5d01900fa6da46e1479adb9d6c309900bff0bee8cebc93d5b6e3052656e6fd19bdc9a05e6f418c62b0",
        "Host": "jdih.setneg.go.id",
        "Referer": "https://jdih.setneg.go.id/Terbaru",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"'
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch data for number {number}. Status code: {response.status_code}")
        return None

    try:
        data = response.json()
    except ValueError:
        print(f"Failed to parse JSON response for number {number}")
        return None

    if not isinstance(data, dict):
        print(f"Unexpected data format for number {number}: {data}")
        return None

    if data.get('data') is None:
        print(f"No data available for number {number}.")
        set_json(number)
        return None

    if 'tentang' not in data['data']:
        print(f"Missing 'tentang' key in 'data' for number {number}")
        return None

    title_data = data['data']['tentang']

    if title_data is None:
        print(f"Title data is None for number {number}. Stopping recursion.")
        return None

    title_data = title_data.title()
    date_data = data['data']['tgl_di']
    no_data = data['data']['no_peraturan']
    # add to last line of README.md

        
    
    if "Tunjangan Kinerja" in title_data:
        send_email(f"Tukin Naik", title_data)
        with open('README.md', 'a') as file:
            file.write(f"- `{date_data}` - `Perpres No {no_data}` - {title_data}\n")
    print(f"Title for number {number}: {title_data}")
    return get_data(number + 1)

def send_email(subject, body):
    sender_email = os.getenv('EMAIL_SENDER')
    receiver_email = os.getenv('EMAIL_RECEIVER')

    # If you are using Gmail, use "smtp.gmail.com" and port 587
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = os.getenv('EMAIL_SENDER')
    smtp_password = os.getenv('PASSWORD')
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))
    try:
        # Establish a secure session with the server using SMTP
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable security

        # Log in to your email account
        server.login(smtp_username, smtp_password)

        # Send the email
        server.send_message(msg)

        print("Email sent successfully")

    except Exception as e:
        print(f"Failed to send email: {e}")

    finally:
        server.quit()

def main():
    try:
        with open('number.json', 'r') as file:
            data = json.load(file)
            number = data.get('number', 1)
    except (FileNotFoundError, json.JSONDecodeError):
        number = 1

    get_data(number)

if __name__ == "__main__":
    main()
