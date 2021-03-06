#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PUT /v2.0/routers/{router_id}
Update router
指定したルータの情報を更新する

NOTE:
　・external_gateway_infoのみを更新します
　・一度external_gateway_infoを空っぽにしたあと、指定したexternal_gateway_infoを設定します
"""

"""
実行例（external_gateway_infoを削除する場合）

bash-4.4$ ./bin/k5-update-router.py --router-id ffbd70be-24cf-4dff-a4f6-661bf892e313 --network-id ""
set external_gateway_info to null
PUT /v2.0/routers/{router_id}
==============  ====================================
name            iida-az1-router01
id              ffbd70be-24cf-4dff-a4f6-661bf892e313
az              jp-east-1a
tenant_id       a5001a8b9c4a4712985c11377bd6d4fe
status          ACTIVE
admin_state_up  True
==============  ====================================
bash-4.4$

実行例（external_gateway_infoを設定する場合）

bash-4.4$ ./bin/k5-update-router.py --router-id ffbd70be-24cf-4dff-a4f6-661bf892e313 --network-id af4198a9-b392-493d-80ec-a7c6e5a1c22a
PUT /v2.0/routers/{router_id}
==============  ====================================
name            iida-az1-router01
id              ffbd70be-24cf-4dff-a4f6-661bf892e313
az              jp-east-1a
tenant_id       a5001a8b9c4a4712985c11377bd6d4fe
status          ACTIVE
admin_state_up  True
==============  ====================================
PUT /v2.0/routers/{router_id}
==============  ====================================
name            iida-az1-router01
id              ffbd70be-24cf-4dff-a4f6-661bf892e313
az              jp-east-1a
tenant_id       a5001a8b9c4a4712985c11377bd6d4fe
status          ACTIVE
admin_state_up  True
==============  ====================================

実行例（external_gateway_infoを設定する場合）エラー

bash-4.4$ ./bin/k5-update-router.py --router-id ffbd70be-24cf-4dff-a4f6-661bf892e313 --network-id af4198a9-b392-493d-80ec-a7c6e5a1c22a
set external_gateway_info to null
PUT /v2.0/routers/{router_id}
==============  ====================================
name            iida-az1-router01
id              ffbd70be-24cf-4dff-a4f6-661bf892e313
az              jp-east-1a
tenant_id       a5001a8b9c4a4712985c11377bd6d4fe
status          ACTIVE
admin_state_up  True
==============  ====================================
set external_gateway_info to af4198a9-b392-493d-80ec-a7c6e5a1c22a
{
  "status_code": 409,
  "data": {
    "NeutronError": {
      "message": "No more IP addresses available on network af4198a9-b392-493d-80ec-a7c6e5a1c22a.",
      "type": "IpAddressGenerationFailure",
      "detail": ""
    }
  },
  "Content-Type": "application/json;charset=UTF-8"
}
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
# リクエストデータを作成する
#
def make_request_data(network_id=""):
  """リクエストデータを作成して返却します"""
  # pylint: disable=too-many-arguments

  router_object = {}

  if network_id:
    router_object['external_gateway_info'] = {
      'network_id': network_id
    }
  else:
    router_object['external_gateway_info'] = None

  return {'router': router_object}


#
# APIにアクセスする
#
def access_api(router_id="", data=None):
  """REST APIにアクセスします"""

  # 接続先URL
  url = k5c.EP_NETWORK +  "/v2.0/routers/" + router_id

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # PUTメソッド
  r = c.put(url=url, data=data)

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
    # ステータスコードが503の場合は2分後に実行を促す
    if status_code == 503:
      print("\nNOTE:")
      print("External gateway is being configured. Please try it again about 2 minutes later.")
    return

  # データは'data'キーに格納
  data = result.get('data', None)
  if not data:
    logging.error("no data found")
    return

  # 変更したルータの情報はデータオブジェクトの中の'network'キーにオブジェクトとして入っている
  #"data": {
  #  "router": {
  #    "admin_state_up": true,
  #    "id": "ad3ddc47-6303-48e8-87ad-cb0333c93112",
  #    "name": "iida-test-router-1",
  #    "external_gateway_info": null,
  #    "tenant_id": "a5001a8b9c4a4712985c11377bd6d4fe",
  #    "status": "ACTIVE",
  #    "availability_zone": "jp-east-1a"
  #  }
  #}
  rtr = data.get('router', {})

  # 表示用に配列にする
  rtrs = []
  rtrs.append(['name', rtr.get('name', '')])
  rtrs.append(['id', rtr.get('id', '')])
  rtrs.append(['az', rtr.get('availability_zone', '')])
  rtrs.append(['tenant_id', rtr.get('tenant_id', '')])
  rtrs.append(['status', rtr.get('status', '')])
  rtrs.append(['admin_state_up', rtr.get('admin_state_up', '')])

  # 表示
  print("PUT /v2.0/routers/{router_id}")
  print(tabulate(rtrs, tablefmt='rst'))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Updates a logical router.')
    parser.add_argument('--router-id', dest='router_id', metavar='id', required=True, help='The router id.')
    parser.add_argument('--network-id', dest='network_id', metavar='id', nargs='?', default='', required=True, help='The network_id, for the external gateway.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    router_id = args.router_id
    network_id = args.network_id
    dump = args.dump

    # DEBUG
    # router_id = "05dbac99-4058-4f60-a9cc-a7593a681d7b"
    # network_id = "6d9df982-7a89-462a-8b17-8a8e5befa63e"  # inf_az1_ext-net03
    # dump = False

    # まずはexternal_gateway_infoを空っぽにする

    print("set external_gateway_info to null")

    # 空っぽのリクエストデータを作成して
    data = make_request_data(network_id="")

    # 実行
    result = access_api(router_id=router_id, data=data)

    # 得たデータを処理する
    print_result(result)

    # 次にexternal_gateway_infoを設定する
    if network_id:
      print("set external_gateway_info to {}".format(network_id))
      data = make_request_data(network_id=network_id)
      result = access_api(router_id=router_id, data=data)
      # 中身を確認
      if dump:
        print(json.dumps(result, indent=2))
        return 0
      print_result(result)

    return 0


  # 実行
  sys.exit(main())
