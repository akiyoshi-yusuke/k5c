#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""K5 REST APIに必要なトークンをスレッドセーフに管理するためのモジュールです."""

import datetime
import logging
import os
import pickle
from threading import RLock


class K5TokenManager(object):
  """接続状態を管理します"""
  #
  # 想定しているトークンオブジェクトの形式
  # getToken()の戻り値
  # {
  #    'X-Subject-Token': 'ed0456b9f91041e88db9163e7cf88043',
  #    'expires_at': '2017-05-02T09:11:58.198526Z',
  #    'issued_at': '2017-05-02T06:11:58.198552Z'
  # }
  #

  # トークンを保存するファイル名(中身はjsonではなくpickle形式)
  TOKEN_FILENAME = ".k5-token.pickle"

  # 時刻表示のフォーマット
  DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

  def __init__(self):
    """コンストラクタ"""
    # オンメモリのトークン
    self._token_json = None

    # 排他制御用のロック
    self._lock = RLock()

  def saveToken(self, token):
    """トークンをpickleでファイルに保存します"""
    if not token:
      return

    try:
      with open(self.TOKEN_FILENAME, 'wb') as f:
        pickle.dump(token, f)
    except IOError as e:
      logging.error(e)

  def loadToken(self):
    """pickleでファイルに保存されているトークンを復元します"""
    if not os.path.isfile(self.TOKEN_FILENAME):
      return None

    try:
      with open(self.TOKEN_FILENAME, 'rb') as f:
        token = pickle.load(f)
        return token
    except IOError as e:
      logging.error(e)
    except ValueError as e:
      logging.error(e)
    return None

  def isNotExpired(self, token):
    """有効期限が切れていないことを確認します"""
    now = datetime.datetime.now()

    # 有効期限を取り出す
    # 'expires_at': '2017-05-02T09:11:58.198526Z',
    expires_at_str = token.get('expires_at', None)

    # expires_atが存在しない場合はあらためて取得し直す
    if expires_at_str is None:
      return False

    # 時刻に戻す
    expires_at = datetime.datetime.strptime(expires_at_str, self.DATE_FORMAT)

    # dirty hack
    # JSTにいるものと仮定して+9時間を加算する
    expires_at += datetime.timedelta(hours=9)

    # dirty hack
    # 誤差を考えて3分を減算する
    expires_at -= datetime.timedelta(minutes=3)

    if now < expires_at:
      return True
    #
    return False

  def getCachedToken(self):
    """メモリもしくはディスクからトークンのキャッシュを取得して返します"""
    # まずはメモリキャッシュの有無を確認して、あればそれを返却
    token = self._token_json
    if token and self.isNotExpired(token):
      logging.info("found token on memory cache")
      return token
    logging.info("there is no token on memory cache")

    # メモリキャッシュにない場合は、ディスクから探す
    token = self.loadToken()

    # トークンがディスクに保存されていない
    if not token:
      logging.info("there is no token on disk cache")
      return None

    # トークンの有効期間が切れてないか確認する
    if self.isNotExpired(token):
      logging.info("found token on disk cache")
      self._token_json = token
      return token
    logging.info("there is no available token on disk cache")
    return None

  def lock(self):
    """ロックを獲得します"""
    self._lock.acquire()

  def release(self):
    """ロックを開放します."""
    self._lock.release()

  def token(self, *_):
    """トークンを取得、設定します."""
    if not _:
      return self.getCachedToken()
    else:
      self._token_json = _[0]
      self.saveToken(_[0])
      return self

###############################################################################

#
# K5TokenManagerクラスのインスタンスをグローバル名前空間に一つ生成して共有する
#
k5tokenmanager = K5TokenManager()
