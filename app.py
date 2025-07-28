import requests 
import re
from email.message import EmailMessage
import aiosmtplib
import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

HOST = "smtp.gmail.com"

def monitor(url):
    monitor_endpoint = url + ".js"

    try:
        response = requests.get(monitor_endpoint)

        if response.status_code == 200:
            data = response.json()
            in_stock = data.get("available")

            if bool(in_stock):
                print(f"Alert: {url} is in stock!")
                subj = "Grand Seiko Alert"
                title = data.get("title", "Grand Seiko Watch")
                msg = f"{title} is in stock: {url}"
                asyncio.run(send_txt(msg, subj))
                return True

            else:
                print(f"Info: {url} is not in stock.")

        else:
            print(f"Warning: {url} returned status code {response.status_code}.")
        
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not reach {url}. Exception: {e}")
        return False


async def send_txt(msg, subj):
    to_email = "vtext.com" # verizon sms gateway
    email, pword, num = fetch_env_vars()

    message = EmailMessage()
    message["From"] = email
    message["To"] = f"{num}@{to_email}"
    message["Subject"] = subj
    message.set_content(msg)

    res = await aiosmtplib.send(message, hostname=HOST, port=587, username=email, password=pword) 
    msg = "text failed" if not re.search(r"\sOK\s", res[1]) else "text succeeded"
    print(msg)

def fetch_env_vars():
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    phone_number = os.getenv("PHONE_NUMBER")
    if not email or not password or not phone_number:
        raise ValueError("Missing required environment variables.")
    return email, password, phone_number

if __name__ == "__main__":
    # This script monitors a Grand Seiko watch availability and sends a text alert when it is in stock.
    url =  "https://grandseikoboutique.us/products/watch-spring-drive-boutique-limited-indigo-sbga469"

    # run the monitor function every hour until product is in stock
    flag = False
    while not flag:
        flag = monitor(url)
        asyncio.run(asyncio.sleep(3600))
