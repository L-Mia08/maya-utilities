#--------------------------------------------------------------------------
# ScriptName: ConnectComponents_SoftenEdge
# Author: Naruse,GPT-5
# Contents :Connect Componentsで生成したエッジをソフトエッジにするスクリプト
# CreatedDate: 2025年11月19日
# LastUpdate: 2025年11月19日
# Version: 0.1
#
# 《License》
# Copyright (c) 2025 Naruse
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php
#--------------------------------------------------------------------------

import maya.cmds as cmds

# 初回のみグローバル変数を作る
if "USE_EDGE_FLOW" not in globals():
    USE_EDGE_FLOW = False

print(f"USE_EDGE_FLOW:{USE_EDGE_FLOW}")

def connect_or_edgeflow():
    global USE_EDGE_FLOW

    sel = cmds.ls(sl=True, fl=True)

    # 今の選択モード（True なら component mode / False なら object mode）
    is_component_mode = cmds.selectMode(q=True, component=True)

    # -----------------------------------------------------------
    # コンポーネント選択 + component mode のとき：Connect 実行
    # -----------------------------------------------------------
    if sel and is_component_mode:
        base_comp = sel[0].split('.')[0]
        mesh = cmds.listRelatives(base_comp, s=True, type="mesh")
        if not mesh:
            cmds.warning("メッシュが見つかりませんでした。")
            return
        mesh = mesh[0]

        before_edges = set(cmds.ls(mesh + ".e[*]", fl=True))

        if USE_EDGE_FLOW:
            cmds.polyConnectComponents(sel, insertWithEdgeFlow=True)
        else:
            cmds.polyConnectComponents(sel)

        after_edges = set(cmds.ls(mesh + ".e[*]", fl=True))
        new_edges = list(after_edges - before_edges)

        if not new_edges:
            cmds.warning("新規エッジが見つかりませんでした。")
            return

        cmds.polySoftEdge(new_edges, angle=180, ch=False)
        print("新規エッジ:", new_edges)
        print("Soft Edge を適用しました")
        print(f"Edge Flow {'有効' if USE_EDGE_FLOW else '無効'} で Connect を実行しました")

    else:
        # -----------------------------------------------------------
        # オブジェクトモード or 選択なし → GUI 表示
        # -----------------------------------------------------------
        window_name = "edgeFlowWindow"
        if cmds.window(window_name, exists=True):
            cmds.deleteUI(window_name)

        window = cmds.window(window_name, title="Edge Flow Control", widthHeight=(250, 100))
        cmds.columnLayout(adjustableColumn=True, rowSpacing=10)
        cmds.text(label="ラジオボタンで Edge Flow の有効無効を設定できます")

        default_select = 1 if USE_EDGE_FLOW else 2

        radio_btn = cmds.radioButtonGrp(
            label='Edge Flow', labelArray2=['有効', '無効'],
            numberOfRadioButtons=2, select=default_select,
            cc=lambda _: update_edgeflow_state(radio_btn)
        )

        cmds.showWindow(window)


def update_edgeflow_state(radio_btn):
    """ラジオボタンの状態をグローバル変数に保存"""
    global USE_EDGE_FLOW
    state = cmds.radioButtonGrp(radio_btn, q=True, select=True)
    USE_EDGE_FLOW = (state == 1)
    # 表示が2回出るためコメントアウト
    # print(f"Edge Flow : {'有効' if USE_EDGE_FLOW else '無効'}")


# 実行
connect_or_edgeflow()
