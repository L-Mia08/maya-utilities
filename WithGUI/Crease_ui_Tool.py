#--------------------------------------------------------------------------
# ScriptName: Crease UI Tool
# Author: Naruse,GPT-4o
# Contents   :クリースをUIで操作できるようにし、削除もできる。
# CreatedDate: 2025年07月19日
# LastUpdate: 2025年08月30日
# Version: 0.4
#
# 《License》
# Copyright (c) 2025 Naruse
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php
#--------------------------------------------------------------------------

import maya.cmds as cmds

# スライダーを動かすと動的に適用
def update_crease_from_slider(value):
    edges = cmds.filterExpand(sm=32)
    if not edges:
        cmds.warning("エッジを選択してください。")
        return
    cmds.polyCrease(edges, value=value)
    update_crease_label()

# 「設定」ボタン：現在のスライダー値を適用
def apply_crease_from_button(*args):
    value = cmds.floatSliderGrp("creaseSliderGrp", query=True, value=True)
    update_crease_from_slider(value)

# スライダーの値を 0.0 にリセット（UIのみ）
def reset_slider_value(*args):
    cmds.floatSliderGrp("creaseSliderGrp", edit=True, value=0.0)

# ラベル更新（平均表示）
def update_crease_label(*args):
    edges = cmds.filterExpand(sm=32)
    if not edges:
        cmds.text("creaseValueLabel", edit=True, label="現在のクリース値: なし")
        return
    values = cmds.polyCrease(edges, query=True, value=True)
    if values:
        avg = sum(values) / len(values)
        cmds.text("creaseValueLabel", edit=True, label=f"現在のクリース値（平均）: {avg:.2f}")
    else:
        cmds.text("creaseValueLabel", edit=True, label="現在のクリース値: 未設定")

# クリース値を 0 にリセット
def reset_crease_and_label(*args):
    edges = cmds.filterExpand(sm=32)
    if not edges:
        cmds.warning("エッジを選択してください。")
        return
    cmds.polyCrease(edges, value=0)
    update_crease_label()

# UI作成
def create_crease_ui():
    if cmds.window("creaseWindow", exists=True):
        cmds.deleteUI("creaseWindow")

    cmds.window("creaseWindow", title="Crease 設定ツール(GUI)", widthHeight=(300, 200))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10)

    cmds.text(label="クリース値を調整 (0.0 - 10.0)")

    # スライダー（動的適用）
    cmds.floatSliderGrp(
        "creaseSliderGrp",
        label="",
        field=True,
        minValue=0.0,
        maxValue=10.0,
        value=0.0,
        step=0.1,
        changeCommand=update_crease_from_slider
    )

    # 設定ボタン（明示的に適用）
    cmds.button(label="スライダーの値を適用", command=apply_crease_from_button)

    # スライダーリセットボタン（UI値のみ 0.0 に戻す）
    cmds.button(label="スライダーを0.0にリセット", command=reset_slider_value)

    cmds.separator(height=1, style='in')  # 仕切り

    # クリース値リセットボタン（エッジ値を0に）
    cmds.button(label="クリース削除", command=reset_crease_and_label)

    cmds.separator(height=1, style='in')  # 仕切り

    # 表示を更新する手動ボタン（任意）
    cmds.button(label="現在のクリース値を再取得", command=update_crease_label)

	# 現在のクリース値表示ラベル
    cmds.text("creaseValueLabel", label="現在のクリース値: 未取得")

    cmds.showWindow("creaseWindow")

# 実行
create_crease_ui()