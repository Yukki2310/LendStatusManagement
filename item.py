"""
物品一覧の取得・新規追加・編集・削除を行う
"""

from datetime import datetime
from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from auth import login_required
from db import get_db

item_bp = Blueprint('item', __name__, url_prefix='/item')

@item_bp.route('/')
@login_required
def index_item():
    # 物品の一覧を取得する

    # DBと接続
    db = get_db()

    # 物品データを取得
    user_id = session.get('user_id')
    all_item = db.execute(
        'SELECT * FROM item ORDER BY id DESC'
    ).fetchall()

    # 一覧画面へ遷移
    return render_template('item/index_item.html',
                           items=all_item,
                           title='ログイン',
                           year=datetime.now().year)


@item_bp.route('/my_status')
@login_required
def my_status():
    # 自分の借りている物品の一覧を取得する

    # DBと接続
    db = get_db()

    # 物品データを取得
    user_id = session.get('user_id')
    all_item = db.execute(
        'SELECT * FROM item WHERE user_id = ? ORDER BY id DESC', (user_id,)
    ).fetchall()

    # 一覧画面へ遷移
    return render_template('item/my_status.html',
                           items=all_item,
                           title='ログイン',
                           year=datetime.now().year)


@item_bp.route('/<int:item_id>/detail_item')
@login_required
def detail_item(item_id):
    # データの取得と存在チェック
    item = get_item_and_check(item_id)

    return render_template('item/detail_item.html',
                            item=item,
                            title='物品詳細',
                            year=datetime.now().year)


@item_bp.route('/create_item', methods=('GET', 'POST'))
@login_required
def create_item():
    """
    GET ：登録画面に遷移
    POST：登録処理を実施
    """
    # 登録画面の表示 ----------------------------------
    if request.method == 'GET':
        # 登録画面に遷移
        return render_template('item/create_item.html',
                               title='新規追加',
                               year=datetime.now().year)


    # 登録処理 ---------------------------------------
    # ユーザーIDを取得
    # user_id = session.get('user_id')

    # 登録フォームから送られてきた値を取得
    name = request.form['name']
    detail = request.form['detail']

    # デフォルトで設定する値
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # DBと接続
    db = get_db()

    # エラーチェック
    error_message = None

    if not name:
        error_message = '品名の入力は必須です'

    if error_message is not None:
        # エラーがあれば、それを画面に表示させる
        flash(error_message, category='alert alert-danger')
        return redirect(url_for('item.create_item'))

    # エラーがなければテーブルに登録する
    db.execute(
        'INSERT INTO item (name, user_id, last_update, detail) VALUES (?, NULL, ?, ?)',
        (name, current_date, detail)
    )
    db.commit()

    # 物品一覧画面へ遷移
    flash('追加されました', category='alert alert-info')
    return redirect(url_for('item.index_item'))


@item_bp.route('/<int:item_id>/update_item', methods=('GET', 'POST'))
@login_required
def update_item(item_id):
    """
    GET ：更新画面に遷移
    POST：更新処理を実施
    """

    # データの取得と存在チェック
    item = get_item_and_check(item_id)

    if request.method == 'GET':
        # 更新画面に遷移
        return render_template('item/update_item.html',
                               item=item,
                               title='物品の編集',
                               year=datetime.now().year)

    # 物品編集処理

    # 登録フォームから送られてきた値を取得
    name = request.form['name']
    detail = request.form['detail']

    # デフォルトで設定する値
    current_date = datetime.now().strftime('%Y-%m-%d')

    # DBと接続
    db = get_db()

    # エラーチェック
    error_message = None

    if not name:
        error_message = '物品タイトルの入力は必須です'

    if error_message is not None:
        # エラーがあれば、それを画面に表示させる
        flash(error_message, category='alert alert-danger')
        return redirect(url_for('item.update_item'))


    # エラーがなければテーブルに登録する
    db.execute(
        'UPDATE item SET name=?, last_update=?, detail=? WHERE id=?',
        (name, current_date, detail, item_id)
    )
    db.commit()

    # 物品一覧画面へ遷移
    flash('編集内容を保存しました', category='alert alert-info')
    return redirect(url_for('item.index_item'))


@item_bp.route('/<int:item_id>/delete_item', methods=('GET', 'POST'))
@login_required
def delete_item(item_id):
    """
    GET ：物品削除確認画面に遷移
    POST：物品削除処理を実施
    """
    # 物品データの取得と存在チェック
    item = get_item_and_check(item_id)

    if request.method == 'GET':
        # 物品削除確認画面に遷移
        return render_template('item/delete_item.html',
                               item=item,
                               title='物品の削除',
                               year=datetime.now().year)

    # 物品の削除処理

    db = get_db()
    db.execute('DELETE FROM item WHERE id = ?', (item_id,))
    db.commit()

    # 物品一覧画面へ遷移
    flash('物品が削除されました', category='alert alert-info')
    return redirect(url_for('item.index_item'))


@item_bp.route('/<int:item_id>/lend_item', methods=('GET', 'POST'))
@login_required
def lend_item(item_id):
    """
    GET ：更新画面に遷移
    POST：更新処理を実施
    """

    # データの取得と存在チェック
    item = get_item_and_check(item_id)

    if request.method == 'GET':
        # 画面遷移
        return render_template('item/lend_item.html',
                               item=item,
                               title='物品の編集',
                               year=datetime.now().year)

    # 物品貸し出し処理 ####################################

    # 登録フォームから送られてきた値を取得
    return_schedule = request.form['return_schedule']
    note = request.form['note']
    if not return_schedule:
        # return_scheduleが入力されていない場合にアラートを表示
        flash('返却予定日を入力してください', category='alert alert-danger')
        return render_template('item/lend_item.html',
                               item=item,
                               title='物品の編集',
                               year=datetime.now().year)

    # デフォルトで設定する値
    current_date = datetime.now().strftime('%Y-%m-%d')

    # DBと接続
    db = get_db()

    # データの取得
    user_id = session.get('user_id')

    # テーブルに登録する
    db.execute(
        'UPDATE item SET user_id=?, last_update=?, return_schedule=?, note=? WHERE id=?',
        (user_id, current_date, return_schedule, note, item_id)
    )
    db.commit()

    # 物品一覧画面へ遷移
    flash('内容を保存しました', category='alert alert-info')
    return redirect(url_for('item.index_item'))


@item_bp.route('/<int:item_id>/return_item', methods=('GET', 'POST'))
@login_required
def return_item(item_id):
    """
    GET ：更新画面に遷移
    POST：更新処理を実施
    """

    # データの取得と存在チェック
    item = get_item_and_check(item_id)

    if request.method == 'GET':
        # 画面遷移
        return render_template('item/return_item.html',
                               item=item,
                               title='物品の返却',
                               year=datetime.now().year)

    # 物品返却処理 ####################################

    # デフォルトで設定する値
    current_date = datetime.now().strftime('%Y-%m-%d')

    # DBと接続
    db = get_db()

    # データの取得
    user_id = session.get('user_id')

    # テーブルに登録する
    db.execute(
        'UPDATE item SET user_id=NULL, last_update=?, return_schedule=NULL, note=NULL WHERE id=?',
        (current_date, item_id)
    )
    db.commit()

    # 物品一覧画面へ遷移
    flash('内容を保存しました', category='alert alert-info')
    return redirect(url_for('item.my_status'))


def get_item_and_check(item_id):
    """物品の取得と存在チェックのための関数"""

    # 物品データの取得
    db = get_db()
    item = db.execute(
        'SELECT * FROM item WHERE id = ? ', (item_id,)
    ).fetchone()

    if item is None:
        abort(404, 'There is no such item!!')

    return item