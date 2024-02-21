"""
DB接続と切断を行う
"""

import sqlite3
from flask import current_app, g

# def get_db():
#     """DBへの接続"""
#     if 'db' not in g:
#         g.db = sqlite3.connect(
#             current_app.config['DATABASE'],
#             detect_types=sqlite3.PARSE_DECLTYPES
#         )

#         # 列に名前でアクセスできるようにする
#         g.db.row_factory = sqlite3.Row

#     return g.db


# def close_db(e=None):
#     """DBの切断"""
#     db = g.pop('db', None)

#     if db is not None:
#         db.close()

import pyodbc
from flask import current_app, g

def get_db():
    """DBへの接続"""
    if 'db' not in g:
        conn_str = current_app.config['AZURE_SQL_CONNECTION_STRING']
        g.db = pyodbc.connect(conn_str)

    return g.db

def close_db(e=None):
    """DBの切断"""
    db = g.pop('db', None)
    if db is not None:
        db.close()