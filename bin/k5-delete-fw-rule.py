#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DELETE /v2.0/fw/firewall_rules/{firewall_rule_id}
Delete firewall rule
ファイアーウォールのルールを削除する

NOTE:
　・ポリシーに割り当てたものは削除できません（エラーが戻ります）
"""

"""
実行例（成功した場合は特にデータは戻りません）

bash-4.4$ ./k5-delete-fw-rule.py 856e5fa9-f114-403f-aae0-f9ef3ffd3f0c
status_code: 204

bash-4.4$
実行例（失敗した場合はエラーメッセージが戻ります）
bash-4.4$ ./k5-delete-fw-rule.py 856e5fa9-f114-403f-aae0-f9ef3ffd3f0c
{
  "status_code": 404,
  "Content-Type": "application/json;charset=UTF-8",
  "data": {
    "NeutronError": {
      "detail": "",
      "type": "FirewallRuleNotFound",
      "message": "Firewall Rule 856e5fa9-f114-403f-aae0-f9ef3ffd3f0c could not be found."
    }
  }
}
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


#
# APIにアクセスする
#
def access_api(rule_id=""):
  """REST APIにアクセスします"""

  # 接続先
  url = k5c.EP_NETWORK + "/v2.0/fw/firewall_rules/" + rule_id

  # Clientクラスをインスタンス化
  c = k5c.Client()

  # DELETEメソッドで削除して、結果のオブジェクトを得る
  r = c.delete(url=url)

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

  # 結果表示
  print("status_code: {0}".format(result.get('status_code', "")))
  print(result.get('data', ""))


if __name__ == '__main__':

  import argparse

  def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Deletes a firewall rule.')
    parser.add_argument('rule_id', metavar='id', help='The firewall rule id.')
    parser.add_argument('--dump', action='store_true', default=False, help='Dump json result and exit.')
    args = parser.parse_args()
    rule_id = args.rule_id
    dump = args.dump

    if rule_id == '-':
      import re
      regex = re.compile('^([a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}).*', re.I)
      for line in sys.stdin:
        match = regex.match(line)
        if match:
          uuid = match.group(1)
          # 実行
          result = access_api(rule_id=uuid)
          # 表示
          print(uuid)
          print_result(result)
          print("")
          sys.stdout.flush()
      return 0

    # 実行
    result = access_api(rule_id=rule_id)

    # 中身を確認
    if dump:
      print(json.dumps(result, indent=2))
      return 0

    # 表示
    print_result(result)

    return 0


  # 実行
  sys.exit(main())
