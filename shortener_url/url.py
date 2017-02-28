# -*- coding: utf-8 -*-

import base64
import hashlib

def encode_url(url, **settings):
    """convert canonical url to short url"""
    cut = settings.get("URL_CUT", 4)
    return str(base64.b64encode(hashlib.md5(url.encode()).digest()[-cut:])).replace('=','').replace('/','_').decode()

