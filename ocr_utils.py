# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : ocr_utils.py
   Author   : CoderPig
   date     : 2022-05-27 15:42 
   Desc     : 
-------------------------------------------------
"""
import socket
import requests as r
from collections import OrderedDict

local_ocr_base_url = "http://{}:8089".format(socket.gethostbyname(socket.gethostname()))
local_ocr_tr_run_url = local_ocr_base_url + "/api/tr-run/"


def picture_local_ocr(pic_path):
    upload_files = {'file': open(pic_path, 'rb'), 'compress': 960}
    resp = r.post(local_ocr_tr_run_url, files=upload_files)
    return extract_text(resp.json())


def extract_text(origin_data_dict):
    text_dict = OrderedDict()
    raw_out = origin_data_dict['data']['raw_out']
    if raw_out is not None:
        for raw in raw_out:
            text_dict[raw[1]] = (raw[0][0][0], raw[0][0][1], raw[0][1][0], raw[0][2][1])
        return text_dict
    else:
        print("Json数据解析异常")


if __name__ == '__main__':
    picture_local_ocr('test.jpg')
