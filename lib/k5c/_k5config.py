#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
設定情報
"""

#
# K5ポータル
# https://s-portal.cloud.global.fujitsu.com/SK5PCOM001/
#

# 契約番号
DOMAIN_NAME = ""  # ここを書き換え

# グループdomainmanagerのドメインID
DOMAIN_ID = ""  # ここを書き換え

# プロジェクトID
PROJECT_ID = ""  # ここを書き換え

# ユーザ情報
USERNAME = ""  # ここを書き換え
PASSWORD = ""  # ここを書き換え

# 利用リージョン
REGION = "jp-east-1"  # ここを書き換え

#
# エンドポイント
#
EP_TOKEN = "https://identity." + REGION + ".cloud.global.fujitsu.com"
EP_IDENTITY = "https://identity." + REGION + ".cloud.global.fujitsu.com"
EP_NETWORK = "https://networking." + REGION + ".cloud.global.fujitsu.com"

#
# URLショートカット
#
URL_TOKEN = EP_TOKEN + "/v3/auth/tokens"
URL_USERS = EP_IDENTITY + "/v3/users?domain_id=" + DOMAIN_ID
URL_NETWORK = EP_NETWORK + "/v2.0/networks"

#
# プロキシ設定
#
USE_PROXY = False
# USE_PROXY = True

PROXIES = {
  'http': "http://username:password@proxyserver:8080",
  'https': "http://username:password@proxyserver:8080"
}

if not USE_PROXY:
  PROXIES = None

#
# 動作設定
#
TIMEOUT = 15
