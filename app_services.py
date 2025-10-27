# -*- coding: utf-8 -*-
import os
import json
import shutil
import platform
import subprocess
from datetime import datetime

import requests

from line_config import LINE_CHANNEL_ACCESS_TOKEN, LINE_USER_ID


def send_line_message(message):
    """Send a text message to LINE using push API. Returns True on success."""
    try:
        url = "https://api.line.me/v2/bot/message/broadcast"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(LINE_CHANNEL_ACCESS_TOKEN)
        }

        payload = {
            "to": LINE_USER_ID,
            "messages": [
                {
                    "type": "text",
                    "text": message
                }
            ]
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            return True
        else:
            print("ส่งข้อความไม่สำเร็จ: {}".format(response.status_code))
            print(response.text)
            return False
    except Exception as e:
        print("เกิดข้อผิดพลาดในการส่งข้อความ: {}".format(str(e)))
        return False


def open_pdf_external(pdf_path):
    """Open a PDF file with the default system viewer (best-effort)."""
    try:
        if platform.system() == "Windows":
            os_startfile = getattr(__import__("os"), "startfile", None)
            if os_startfile:
                os_startfile(pdf_path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", pdf_path])
        else:
            subprocess.Popen(["xdg-open", pdf_path])
    except Exception:
        pass


def copy_product_image(source_path, base_dir=None):
    """Copy a product image into the application's product_images directory.

    Returns the new path, or the original source_path on error.
    """
    if not source_path or not os.path.exists(source_path):
        return ""

    try:
        # Determine destination directory
        if base_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        images_dir = os.path.join(base_dir, "product_images")
        os.makedirs(images_dir, exist_ok=True)

        file_ext = os.path.splitext(source_path)[1]
        new_filename = "product_{}{}".format(datetime.now().strftime('%Y%m%d_%H%M%S'), file_ext)
        new_path = os.path.join(images_dir, new_filename)

        shutil.copy2(source_path, new_path)
        return new_path
    except Exception as e:
        print("Error copying image: {}".format(e))
        return source_path


