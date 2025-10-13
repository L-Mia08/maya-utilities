#--------------------------------------------------------------------------
# ScriptName: tx auto reload
# Author: Naruse,GPT-5
# Contents   : 選択したテクスチャノードを数秒ごとに自動的にロードする
# CreatedDate: 2025年10月13日
# LastUpdate: 2025年10月13日
# Version: 0.1
#
# 《License》
# Copyright (c) 2025 Naruse
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php
#--------------------------------------------------------------------------

import maya.cmds as cmds
import time
import threading

# -----------------------------------------------------
# グローバル変数
# -----------------------------------------------------
auto_reload_thread = None
auto_reload_running = False


# -----------------------------------------------------
# ファイルノード一覧を取得
# -----------------------------------------------------
def get_file_nodes():
    return cmds.ls(type="file") or []


# -----------------------------------------------------
# 選択されたファイルノードのテクスチャをリロード
# -----------------------------------------------------
def reload_selected_file(*args):
    sel = cmds.textScrollList("fileNodeList", q=True, si=True)
    if not sel:
        cmds.warning("ファイルノードが選択されていません。")
        return

    for node in sel:
        try:
            file_path = cmds.getAttr(f"{node}.fileTextureName")
            if not file_path:
                cmds.warning(f"{node} にファイルパスが設定されていません。")
                continue

            # ファイルを再設定してリロード
            cmds.setAttr(f"{node}.fileTextureName", file_path, type="string")
            print(f"[{time.strftime('%H:%M:%S')}] [リロード] {node}: {file_path}")
        except Exception as e:
            cmds.warning(f"{node} のリロードに失敗しました: {e}")


# -----------------------------------------------------
# ファイルノードリスト更新
# -----------------------------------------------------
def refresh_file_list(*args):
    file_nodes = get_file_nodes()
    cmds.textScrollList("fileNodeList", e=True, removeAll=True)
    if file_nodes:
        for node in file_nodes:
            cmds.textScrollList("fileNodeList", e=True, append=node)
    else:
        cmds.textScrollList("fileNodeList", e=True, append="(ファイルノードなし)")
        cmds.warning("シーン内に file ノードが見つかりません。")


# -----------------------------------------------------
# 自動リロード処理スレッド
# -----------------------------------------------------
def auto_reload_loop(interval):
    global auto_reload_running

    while auto_reload_running:
        # 実行
        cmds.evalDeferred(reload_selected_file)

        # 次回予定時間を表示
        next_time = time.strftime("%H:%M:%S", time.localtime(time.time() + interval))
        print(f"次のリロード予定時刻: {next_time}")

        # 指定秒数待機＋カウントダウン表示
        for i in range(interval):
            if not auto_reload_running:
                break

            remaining = interval - i
            # カウントダウン条件：間隔が5秒超かつ残り5秒以内
            if interval > 5 and remaining <= 5:
                print(f"リロードまで {remaining} 秒...")
            time.sleep(1)


# -----------------------------------------------------
# 自動リロード開始
# -----------------------------------------------------
def start_auto_reload(*args):
    global auto_reload_thread, auto_reload_running

    if auto_reload_running:
        cmds.warning("自動リロードはすでに実行中です。")
        return

    interval = cmds.intField("reloadIntervalField", q=True, value=True)
    if interval <= 0:
        cmds.warning("間隔は1以上の数値を入力してください。")
        return

    auto_reload_running = True
    now = time.strftime("%H:%M:%S")
    print(f"\n[{now}] 自動リロードを開始しました（{interval} 秒ごと）")
    cmds.inViewMessage(amg=f"<hl>自動リロードを開始</hl>（{interval} 秒ごと）", pos="topCenter", fade=True)

    # スレッドで実行（UIをブロックしない）
    auto_reload_thread = threading.Thread(target=auto_reload_loop, args=(interval,), daemon=True)
    auto_reload_thread.start()


# -----------------------------------------------------
# 自動リロード停止
# -----------------------------------------------------
def stop_auto_reload(*args):
    global auto_reload_running
    if not auto_reload_running:
        cmds.warning("自動リロードは実行されていません。")
        return

    auto_reload_running = False
    now = time.strftime("%H:%M:%S")
    print(f"[{now}] 自動リロードを停止しました。")
    cmds.inViewMessage(amg="<hl>自動リロードを停止しました</hl>", pos="topCenter", fade=True)


# -----------------------------------------------------
# UIを作成
# -----------------------------------------------------
def show_file_reload_ui():
    if cmds.window("fileReloadUI", exists=True):
        cmds.deleteUI("fileReloadUI")

    window = cmds.window("fileReloadUI", title="ファイルノード リロードツール", widthHeight=(320, 420))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10)

    cmds.text(label="シーン内のファイルノード一覧")
    cmds.textScrollList("fileNodeList", numberOfRows=10, allowMultiSelection=True)

    cmds.button(label="リスト更新", command=refresh_file_list)
    cmds.button(label="選択したファイルノードをリロード", command=reload_selected_file)

    cmds.separator(height=10, style='in')
    cmds.text(label="自動リロード設定")
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(150, 100))
    cmds.text(label="リロード間隔（秒）:")
    cmds.intField("reloadIntervalField", value=10, minValue=1)
    cmds.setParent("..")

    cmds.rowLayout(numberOfColumns=2, columnWidth2=(150, 100))
    cmds.button(label="▶ 自動リロード開始", bgc=(0.4, 0.8, 0.4), command=start_auto_reload)
    cmds.button(label="■ 自動リロード停止", bgc=(0.8, 0.4, 0.4), command=stop_auto_reload)
    cmds.setParent("..")

    refresh_file_list()
    cmds.showWindow(window)


# -----------------------------------------------------
# 実行
# -----------------------------------------------------
show_file_reload_ui()
