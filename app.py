"""
The flask application package.
"""
import os
from os import environ
from flask import Flask

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('application.cfg', silent=True)

# アプリケーションコンテキストが終了したときに
# 毎回DBを切断する
from db import close_db
app.teardown_appcontext(close_db)

# インデックスページの読み込み
import views

# ログイン機能の追加
from auth import auth_bp
app.register_blueprint(auth_bp)

# 書籍管理機能の追加
from item import item_bp
app.register_blueprint(item_bp)

# if __name__ == '__main__':
#    app.run()