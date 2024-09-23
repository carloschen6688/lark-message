#!/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import json
import argparse
import hashlib
import base64
import hmac
import time


def gen_sign(timestamp, secret):
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    hmac_code = hmac.new(string_to_sign.encode("utf-8"),
                         digestmod=hashlib.sha256).digest()
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return sign


def build_card_message(args):
    elements = [
        {
            "tag": "column_set",
            "flex_mode": "none",
            "background_style": "default",
            "columns": [
                {
                    "tag": "column",
                    "width": "weighted",
                    "weight": 1,
                    "vertical_aign": "top",
                    "elements": [
                        {
                            "tag": "div",
                            "text": {
                                "content": args.content,
                                "tag": "lark_md"
                            }
                        }
                    ]
                }
            ]
        }
    ]

    message_card = {
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": False
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": args.title
                },
                "template": args.header_color
            },
            "elements": elements
        }
    }

    if args.lark_signature_verification:
        # The timestamp used is more than 1 hour from the time the request was sent, and the signature has expired
        timestamp = str(int(time.time()))
        sign = gen_sign(timestamp, args.lark_signature_verification)
        message_card["timestamp"] = timestamp
        message_card["sign"] = sign

    message_card_json = json.dumps(message_card, indent=4, ensure_ascii=False)
    return message_card_json


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Notify Lark')
    parser.add_argument('--title', type=str, help='Title', required=True)
    parser.add_argument('--content', type=str, help='Content', required=True)
    parser.add_argument('--header-color', type=str,
                        help='Header color', default="green")
    parser.add_argument('--lark-bot-notify-webhook', type=str,
                        help='Lark webhook', required=True)
    parser.add_argument('--lark-signature-verification', type=str,
                        help='Lark signature verification', required=False)
    args = parser.parse_args()

    message = build_card_message(args)
    print("Notify message: ", message)
    subprocess.run(["curl", "-X", "POST", "-H", "Content-Type: application/json",
                   "-d", message, args.lark_bot_notify_webhook], check=True)
    # if args.lark_signature_verification:
    #     timestamp = str(int(time.time() * 1000))
    #     sign = gen_sign(timestamp, args.lark_signature_verification)
    #     subprocess.run(["curl", "-X", "POST", "-H", "Content-Type: application/json", "-H", "X-Lark-Request-Timestamp:" + timestamp, "-H", "token: " + sign, "-d", message, args.lark_bot_notify_webhook], check=True)
    # else:
    #     subprocess.run(["curl", "-X", "POST", "-H", "Content-Type: application/json", "-d", message, args.lark_bot_notify_webhook], check=True)
    print("Notify message sent succeed")
