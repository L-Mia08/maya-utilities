#--------------------------------------------------------------------------
# ScriptName: face_Invert_Normal
# Author: Naruse,GPT-4o
# Contents   :選択したオブジェクトの法線を外側に向けてスムースするスクリプト
# CreatedDate: 2025年08月16日
# LastUpdate: 2025年09月29日
# Version: 0.2
#
# 《License》
# Copyright (c) 2025 Naruse
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php
#--------------------------------------------------------------------------

import maya.cmds as cmds

def reset_normals_from_inside_to_outside():
    sel = cmds.ls(selection=True, long=True)
    if not sel:
        cmds.warning("オブジェクトを選択してください。")
        return

    for obj in sel:
        try:
            # 一度すべてのフェース法線を内側に反転
            cmds.polySetToFaceNormal(obj)
            cmds.polyNormal(obj, normalMode=1, userNormalMode=0, ch=False)  # 1 = 内側

            # 再度外側に向けて法線を修正
            cmds.polyNormal(obj, normalMode=0, userNormalMode=0, ch=False)  # 0 = 外側

            # スムース法線を再適用（必要なら角度を調整）
            cmds.polySoftEdge(obj, angle=180, ch=False)

        except Exception as e:
            cmds.warning(f"{obj} の処理中にエラーが発生しました: {e}")

    print("法線を一度内側に反転 → 外側に修正しました。")

reset_normals_from_inside_to_outside()
