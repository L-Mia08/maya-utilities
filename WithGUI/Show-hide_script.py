#--------------------------------------------------------------------------
# ScriptName: Show-hide_script
# Author: Naruse,GPT-5
# Contents  :非表示にしたオブジェクトを記録して、再度一括で表示できる。
# CreatedDate: 2025年08月30日
# LastUpdate: 2025年08月30日
# Version: 1.3
#
# 《License》
# Copyright (c) 2025 Naruse
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php
#--------------------------------------------------------------------------

import maya.cmds as cmds

# 非表示オブジェクトのリストを保持する
hidden_objects = set()

def toggle_visibility():
    global hidden_objects
    selected_objects = cmds.ls(selection=True)

    if not selected_objects:
        cmds.warning("オブジェクトを選択してください。")
        return

    for obj in selected_objects:
        if not cmds.objExists(obj):
            continue

        current_visibility = cmds.getAttr(f"{obj}.visibility")

        if current_visibility:
            # 表示中なら非表示にしてリストへ追加
            cmds.setAttr(f"{obj}.visibility", False)
            hidden_objects.add(obj)
        else:
            # 非表示なら表示にしてリストから削除
            cmds.setAttr(f"{obj}.visibility", True)
            hidden_objects.discard(obj)  # remove ではなく discard にすることで存在しなくても安全

def show_all_hidden():
    global hidden_objects
    # 存在するものだけ処理
    for obj in list(hidden_objects):
        if cmds.objExists(obj):
            cmds.setAttr(f"{obj}.visibility", True)
    # 全てリセット
    hidden_objects.clear()

def create_ui():
    if cmds.window("toggleVisibilityWindow", exists=True):
        cmds.deleteUI("toggleVisibilityWindow")

    window = cmds.window("toggleVisibilityWindow", title="Visibility Toggle", widthHeight=(180, 90))
    cmds.columnLayout(adjustableColumn=True)

    cmds.button(label="Toggle Visibility", command=lambda x: toggle_visibility())
    cmds.button(label="Show All Hidden", command=lambda x: show_all_hidden())

    cmds.showWindow(window)

create_ui()
