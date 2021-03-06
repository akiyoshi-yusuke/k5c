#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GET /v2.0/vpn/ikepolicies/{ikepolicy-id}
Show IKE policy details
指定したIKEポリシーの詳細を表示する
"""

"""
実行例

bash-4.4$ ./bin/k5-list-ikepolicy.py | ./bin/k5-show-ikepolicy.py -
ikepolicy_id: 4334b806-824c-4419-b0cb-b79fa8be9c72
GET /v2.0/vpn/ikepolicies/{ikepolicy-id}
=======================  ====================================
name                     iida-az1-ikepolicy
id                       4334b806-824c-4419-b0cb-b79fa8be9c72
auth_algorithm           sha1
pfs                      group14
ike_version              v1
encryption_algorithm     aes-256
phase1_negotiation_mode  main
tenant_id                a5001a8b9c4a4712985c11377bd6d4fe
availability_zone        jp-east-1a
=======================  ====================================

lifetime
=====  =======
value  86400
units  seconds
=====  =======

bash-4.4$
"""

import json
import logging
import os
import sys

def here(path=''):
  """相対パスを絶対パスに変換して返却します"""
  if getattr(sys, 'frozen', False):
    # cx_Freezeで固めた場合は実行ファイルからの相対パス
    return os.path.abspath(os.path.join(os.path.dirname(sys.executable), path))
  else:
    # 通常はこのファイルの場所からの相対パス
    return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

# libフォルダにおいたpythonスクリプトを読みこませるための処理
if not here("../lib") in sys.path:
  sys.path.append(here("../lib"))

if not here("../lib/site-packages") in sys.path:
  sys.path.append(here("../lib/site-packages"))

try:
  from k5c import k5c
except ImportError as e:
  logging.exception("k5cモジュールのインポートに失敗しました: %s", e)
  sys.exit(1)

try:
  from tabulate import tabulate
except ImportError as e:
  logging.exception("tabulateモジュールのインポートに失敗しました: %s", e)
  sys.exit(1)

#
# APIにアクセスする
#
def access_api(ikepolicy_id=""):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/vpn/ikepolicies/" + ikepolicy_id

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # GETメソッドで取得して、結果のオブジェクトを得る
  r = c.get(url=url)

  return r


#
# 結果を表示する
#
def print_result(result):
  """結果を表示します"""

  # ステータスコードは'status_code'キーに格納
  status_code = result.get('status_code', -1)

  # ステータスコードが異常な場合
  if status_code < 0 or status_code >= 400:
    print(json.dumps(result, indent=2))
    return

  # データは'data'キーに格納
  data = result.get('data', None)
  if not data:
    logging.error("no data found")
    return

  #{
  #  "Content-Type": "application/json;charset=UTF-8",
  #  "status_code": 200,
  #  "data": {
  #    "ikepolicy": {
  #      "auth_algorithm": "sha1",
  #      "pfs": "group14",
  #      "description": "",
  #      "lifetime": {
  #        "value": 86400,
  #        "units": "seconds"
  #      },
  #      "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #      "ike_version": "v1",
  #      "name": "iida-az1-ikepolicy",
  #      "encryption_algorithm": "aes-256",
  #      "availability_zone": "jp-east-1a",
  #      "phase1_negotiation_mode": "main",
  #      "id": "ace696b0-b937-4ee7-8444-20acbb2400e0"
  #    }
  #  }
  #}

  item = data.get('ikepolicy', {})

  disp_keys = [
    'name', 'id', 'auth_algorithm', 'pfs', 'ike_version', 'encryption_algorithm', 'phase1_negotiation_mode',
    'tenant_id', 'availability_zone'
  ]

  disp_list = []

  for key in disp_keys:
    row = []
    row.append(key)
    row.append(item.get(key, ''))
    disp_list.append(row)

  print("GET /v2.0/vpn/ikepolicies/{ikepolicy-id}")
  print(tabulate(disp_list, tablefmt='rst'))

  lifetime = item.get('lifetime', {})
  lifetime_list = []
  lifetime_keys = ['value', 'units']
  for key in lifetime_keys:
    row = []
    row.append(key)
    row.append(lifetime.get(key, ''))
    lifetime_list.append(row)

  print("")
  print("lifetime")
  print(tabulate(lifetime_list, tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Shows details for a specified IKE policy.')
    parser.add_argument('ikepolicy_id', metavar='id', help='The ikepolicy id.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    ikepolicy_id = args.ikepolicy_id
    dump = args.dump

    if ikepolicy_id == '-':
      import re
      regex = re.compile('^([a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}).*', re.I)
      for line in sys.stdin:
        match = regex.match(line)
        if match:
          uuid = match.group(1)
          result = access_api(ikepolicy_id=uuid)
          print("ikepolicy_id: {}".format(uuid))
          print_result(result)
          print("")
          sys.stdout.flush()
      return 0


    # 実行
    result = access_api(ikepolicy_id=ikepolicy_id)

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result)

    return 0


  # 実行
  sys.exit(main())
