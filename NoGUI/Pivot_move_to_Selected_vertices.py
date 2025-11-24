#--------------------------------------------------------------------------
# ScriptName: Pivot_move_to_Selected_vertices
# Contents : 選択した頂点にピポットを移動また、複数の頂点が選択されている場合は平均位置に移動する。
# Creation Date: 2024/11/19
# Update Date: 2025/11/24
# Version: 0.2

# 《License》
# Copyright (c) 2025 Naruse
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php
#--------------------------------------------------------------------------

import maya.cmds as cmds

try:
    # 現在の選択を取得
    selected_components = cmds.ls(sl=True, fl=True)

    # 頂点が選択されているかを確認
    vertex_selected = [comp for comp in selected_components if '.' in comp and 'vtx' in comp]

    if not vertex_selected:
        # 頂点が選択されていない場合、面や辺が選ばれている場合
        cmds.warning("頂点が選択されていません。頂点を選択してください。")
    else:
        if len(vertex_selected) > 1:
            # 複数頂点が選択されている場合は平均位置を計算
            positions = [cmds.pointPosition(vert, world=True) for vert in vertex_selected]
            avg_position = [sum(coord) / len(positions) for coord in zip(*positions)]
            print(f"複数選択されている頂点座標:{positions}")
        else:
            # 1つだけの場合はその頂点の位置を使用
            avg_position = cmds.pointPosition(vertex_selected[0], world=True)

        # コンポーネント選択からオブジェクト選択に切り替え
        if cmds.selectMode(q=1, component=1) == 1:
            cmds.selectMode(object=1)

        # 選択したオブジェクトのピボットを計算した位置に移動
        sl_nodes = cmds.ls(sl=True, objectsOnly=True)
        for sl_node in sl_nodes:
            cmds.move(avg_position[0], avg_position[1], avg_position[2],
                    sl_node + '.scalePivot', sl_node + '.rotatePivot', rpr=1)

    print(f"選択されている頂点名:{selected_components}")
    print(f"選択されている頂点座標:{avg_position}")

except Exception as e:
    # その他のエラーが発生した場合、エラーメッセージを表示
    cmds.error(f"予期しないエラーが発生しました: {e}")