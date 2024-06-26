from env import *
import requests


def take_screensho_util():
    payload = {"session": "default", "format": "image"}
    response = requests.get(
        f"{url}/api/screenshot", params=payload,)
    data = response
    if data.status_code == 500 or data.status_code == 404:
        create_session()
        response = requests.get(
            f"{url}/api/default/auth/qr", params=payload,)
        data = response
    return data


def logout_util():
    payload = {"session": "default", "logout": "false"}
    response = requests.post(
        f"{url}/api/sessions/stop", data=payload,)
    data = response
    return data


def create_session():
    payload = {"name": "default"}
    response = requests.post(
        f"{url}/api/sessions/start", data=payload,)
    data = response
    return data


def send_text_util(phone, message):
    payload = {"session": "default", "text": message, "phone": phone}
    response = requests.get(
        f"{url}/api/sendText", params=payload)
    data = response
    return data
