# --------------------------------------------------------------------------
# ScriptName: Vertex Snapper
# Author: Naruse,GPT-5,GPT-4o
# Contents: 選択した曲線の移動および回転属性のリセットツール
#           (Tool to reset translation and rotation attributes of selected curves.)
# CreatedDate: 2024年12月23日
# LastUpdate: 2025年11月24日
# Version:0.2
#
# 《License》
# Copyright (c) 2025 Naruse
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php
# --------------------------------------------------------------------------

import maya.cmds as cmds

def reset_attributes(selected_curves, translate_options, rotate_options):
    # Reset specified translate and rotate attributes for selected curves.
    # 選択した曲線の指定された移動および回転属性をリセットします。

    if selected_curves:
        for curve in selected_curves:
            # Get shape nodes
            shapes = cmds.listRelatives(curve, shapes=True, fullPath=True) or []
            # Check if at least one valid NURBS curve shape exists
            valid_curve = any(cmds.nodeType(shape) == 'nurbsCurve' for shape in shapes)

            if valid_curve:
                translate_reset = False
                rotate_reset = False

                # Reset translate attributes
                if any(translate_options.values()):
                    for axis in ['X', 'Y', 'Z']:
                        if translate_options[axis]:
                            try:
                                cmds.setAttr(f"{curve}.translate{axis}", 0)
                                translate_reset = True
                            except RuntimeError as e:
                                cmds.warning(f"Error: {curve}.translate{axis} はロックされているか接続されているため変更できません。詳細: {e}")

                # Reset rotate attributes
                if any(rotate_options.values()):
                    for axis in ['X', 'Y', 'Z']:
                        if rotate_options[axis]:
                            try:
                                cmds.setAttr(f"{curve}.rotate{axis}", 0)
                                rotate_reset = True
                            except RuntimeError as e:
                                cmds.warning(f"Error: {curve}.rotate{axis} はロックされているか接続されているため変更できません。詳細: {e}")

                # Output appropriate message
                if translate_reset and rotate_reset:
                    print(f"{curve} 移動および回転値が正常にリセットされました。")
                elif translate_reset:
                    print(f"{curve} の移動値が正常にリセットされました。")
                elif rotate_reset:
                    print(f"{curve} の回転値が正常にリセットされました。")
            else:
                cmds.warning(f"{curve} は有効な NURBS 曲線ではありません。")
    else:
        cmds.warning("NURBS 曲線が選択されていません。")

def reset_all_attributes(selected_curves):
    # Reset all translate and rotate attributes for selected curves.
    # 選択した曲線の全ての移動および回転属性をリセットします。

    if selected_curves:
        for curve in selected_curves:
            # Get shape nodes
            shapes = cmds.listRelatives(curve, shapes=True, fullPath=True) or []
            valid_curve = any(cmds.nodeType(shape) == 'nurbsCurve' for shape in shapes)

            if valid_curve:
                try:
                    for axis in ['X', 'Y', 'Z']:
                        cmds.setAttr(f"{curve}.translate{axis}", 0)
                        cmds.setAttr(f"{curve}.rotate{axis}", 0)
                    print(f"{curve} のすべての移動および回転値が正常にリセットされました。")
                except RuntimeError as e:
                    cmds.warning(f"Error: {curve} の属性はロックされているか接続されているため変更できません。詳細: {e}")
            else:
                cmds.warning(f"{curve} は有効な NURBS 曲線ではありません。")
    else:
        cmds.warning("NURBS 曲線が選択されていません。")

def create_attribute_reset_gui():
    # Create GUI for resetting translation and rotation attributes.
    # 移動および回転属性をリセットするためのGUIを作成。

    if cmds.window("resetAttributeWindow", exists=True):
        cmds.deleteUI("resetAttributeWindow")

    window = cmds.window("resetAttributeWindow", title="Reset Attributes", widthHeight=(340, 330))
    cmds.columnLayout(adjustableColumn=True)

    cmds.text(label="0にリセットする軸を選択")

    # Translate checkboxes
    cmds.text(label="移動 (Translate):")
    translate_checkboxes = {}
    for axis in ['X', 'Y', 'Z']:
        translate_checkboxes[axis] = cmds.checkBox(label=f"Translate {axis}")

    # Rotate checkboxes
    cmds.text(label="回転 (Rotate):")
    rotate_checkboxes = {}
    for axis in ['X', 'Y', 'Z']:
        rotate_checkboxes[axis] = cmds.checkBox(label=f"Rotate {axis}")

    def on_reset_button_click(*args):
        selected_curves = cmds.ls(selection=True, type="transform")
        translate_options = {axis: cmds.checkBox(translate_checkboxes[axis], query=True, value=True) for axis in ['X', 'Y', 'Z']}
        rotate_options = {axis: cmds.checkBox(rotate_checkboxes[axis], query=True, value=True) for axis in ['X', 'Y', 'Z']}
        reset_attributes(selected_curves, translate_options, rotate_options)

    def on_all_reset_button_click(*args):
        selected_curves = cmds.ls(selection=True, type="transform")
        reset_all_attributes(selected_curves)

    cmds.separator(height=10, style='in')  # 隙間
    cmds.button(label="選択した値をリセット", command=on_reset_button_click)
    cmds.separator(height=5, style='none')  # 隙間
    cmds.button(label="値を全てリセット", command=on_all_reset_button_click)
    cmds.showWindow(window)

# Call the GUI
create_attribute_reset_gui()
