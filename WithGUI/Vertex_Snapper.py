# --------------------------------------------------------------------------
# ScriptName: Vertex Snapper
# Author: Naruse,GPT-5,GPT-4o
# Contents: 複数の頂点を同時にスナップ移動できるスクリプト
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
import maya.api.OpenMaya as om

# 頂点データを保持するデータ
vertex_log = []
record_enabled = True  # デフォルトで記録は有効

def log_selected_vertices():
    """新しく選択された頂点とその座標を記録する"""
    global vertex_log, record_enabled
    if not record_enabled:
        return  # 記録が無効なら処理しない

    selection = cmds.ls(selection=True, flatten=True)
    if not selection:
        print("何も選択されていません。")
        clear_vertex_log()
        return

    for obj in selection:
        if ".vtx[" in obj and obj not in [v[0] for v in vertex_log]:  # 頂点であり、未記録の場合のみ処理
            position = cmds.pointPosition(obj, world=True)
            vertex_log.append((obj, position))

def snap_and_merge_vertices(tolerance=None, merge_same_object=False):
    """記録された頂点をペアリングしてスナップし、必要に応じてマージする"""
    global vertex_log
    if len(vertex_log) < 2:
        cmds.warning("スナップに必要な頂点が不足しています。")
        return

    if len(vertex_log) % 2 != 0:
        cmds.error("偶数個の頂点を選択してください。")
        return

    snap_processed = False
    merge_processed = False

    for i in range(0, len(vertex_log) - 1, 2):
        source_vertex, source_position = vertex_log[i]
        target_vertex, target_position = vertex_log[i + 1]

        source_object = source_vertex.split(".")[0]
        target_object = target_vertex.split(".")[0]

        if tolerance is not None:
            source_pos = om.MVector(*source_position)
            target_pos = om.MVector(*target_position)
            distance = (source_pos - target_pos).length()
            if distance > tolerance:
                print("距離が許容範囲外であるためスナップとマージ処理はスキップされました")
                continue

        cmds.xform(source_vertex, worldSpace=True, translation=target_position)
        snap_processed = True

        if merge_same_object and source_object == target_object:
            cmds.polyMergeVertex([source_vertex, target_vertex], distance=0.001)
            merge_processed = True

    if snap_processed and merge_processed:
        print("スナップとマージ処理が完了しました。")
    elif snap_processed:
        print("スナップ処理が完了しました。")

    vertex_unlock()
    clear_vertex_log()

# 選択解除
def vertex_unlock():
    sel = cmds.ls(sl=True, fl=True)

    # 頂点以外を再選択
    non_vertices = [s for s in sel if ".vtx[" not in s]

    cmds.select(non_vertices, r=True)
    print("頂点解除しました")

# 頂点データ削除
def clear_vertex_log():
    global vertex_log
    vertex_log = []
    print("頂点データをクリアしました")

# 頂点データ表示
def show_vertex_log():
    global vertex_log
    if not vertex_log:
        print("記録された頂点がありません")
        return
    print("頂点データ:")
    for i, (vertex, position) in enumerate(vertex_log):
        print(f"{i + 1}: {vertex} - {position}")

# ---------------------------------------------------------------------------
# ここからUI
class VertexSnapperUI:
    def __init__(self):
        self.script_job = None
        self.create_ui()

    def create_ui(self):
        if cmds.window("vertexSnapperWindow", exists=True):
            cmds.deleteUI("vertexSnapperWindow")

        self.window = cmds.window("vertexSnapperWindow", title="Vertex Snapper", sizeable=False, widthHeight=(200, 270))
        cmds.columnLayout(adjustableColumn=True, rowSpacing=10)

        # 許容範囲設定
        cmds.frameLayout(label="偶数個の頂点を選択してください", collapsable=False, marginWidth=10, marginHeight=10)
        cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnAttach=[(1, 'left', 5), (2, 'both', 5), (3, 'right', 5)])
        cmds.text(label="許容範囲:")
        self.tolerance_field = cmds.floatField(enable=False, value=1.0, precision=2, width=40, changeCommand=self.on_field_change)
        self.tolerance_slider = cmds.floatSlider(minValue=0.0, maxValue=10.0, value=1.0, step=0.1, enable=False, width=60, dragCommand=self.on_slider_change)
        cmds.setParent('..')
        cmds.setParent('..')

        # 記録有効/無効チェックボックス
        self.record_checkbox = cmds.checkBox(label="座標を記録する", value=True, changeCommand=self.on_record_checkbox_change)

        # 許容範囲チェックボックス
        self.tolerance_checkbox = cmds.checkBox(label="許容範囲を有効にする", value=False, changeCommand=self.on_tolerance_checkbox_change)

        # 同オブジェクトならマージチェックボックス
        self.merge_checkbox = cmds.checkBox(label="同オブジェクトならマージする", value=False, changeCommand=self.on_merge_checkbox_change)

        cmds.button(label="スナップ", command=self.on_snap_button_clicked)

        cmds.separator(height=1, style='in')#仕切り

        cmds.button(label="頂点データの初期化", command=self.on_clear_button_clicked)
        cmds.button(label="頂点データの表示", command=self.on_show_log_button_clicked)

        self.script_job = cmds.scriptJob(event=["SelectionChanged", log_selected_vertices], parent=self.window)

        cmds.showWindow(self.window)

    def on_record_checkbox_change(self, *args):
        """
        '座標を記録する'チェックボックスの状態が変更された際に呼び出される。
        グローバル変数 record_enabled を更新し、記録が有効か無効かを設定する。
        """
        global record_enabled
        record_enabled = cmds.checkBox(self.record_checkbox, query=True, value=True)

    def on_tolerance_checkbox_change(self, *args):
        """
        '許容範囲を有効にする'チェックボックスの状態が変更された際に呼び出される。
        有効化された場合、許容範囲スライダーとフィールドが操作可能になり、
        '同オブジェクトならマージする'チェックボックスが無効化される。
        """
        use_tolerance = cmds.checkBox(self.tolerance_checkbox, query=True, value=True)
        cmds.floatSlider(self.tolerance_slider, edit=True, enable=use_tolerance)
        cmds.floatField(self.tolerance_field, edit=True, enable=use_tolerance)
        cmds.checkBox(self.merge_checkbox, edit=True, value=False, enable=not use_tolerance)

    def on_merge_checkbox_change(self, *args):
        """
        '同オブジェクトならマージする'チェックボックスの状態が変更された際に呼び出される。
        有効化された場合、許容範囲チェックボックス、スライダー、フィールドが無効化される。
        """
        use_merge = cmds.checkBox(self.merge_checkbox, query=True, value=True)
        cmds.checkBox(self.tolerance_checkbox, edit=True, value=False, enable=not use_merge)
        cmds.floatSlider(self.tolerance_slider, edit=True, enable=False)
        cmds.floatField(self.tolerance_field, edit=True, enable=False)

    def on_slider_change(self, *args):
        """
        許容範囲スライダーが操作された際に呼び出される。
        スライダーの値をフィールドに反映する。
        """
        value = cmds.floatSlider(self.tolerance_slider, query=True, value=True)
        cmds.floatField(self.tolerance_field, edit=True, value=value)

    def on_field_change(self, *args):
        """
        許容範囲フィールドが操作された際に呼び出される。
        フィールドの値をスライダーに反映する。
        """
        value = cmds.floatField(self.tolerance_field, query=True, value=True)
        cmds.floatSlider(self.tolerance_slider, edit=True, value=value)

    def on_snap_button_clicked(self, *args):
        """
        'スナップ'ボタンがクリックされた際に呼び出される。
        現在の設定を基に、スナップとマージを実行する。
        許容範囲が有効な場合はその値を使用する。
        '同オブジェクトならマージする'設定も考慮する。
        """
        use_tolerance = cmds.checkBox(self.tolerance_checkbox, query=True, value=True)
        tolerance = cmds.floatSlider(self.tolerance_slider, query=True, value=True) if use_tolerance else None
        merge_same_object = cmds.checkBox(self.merge_checkbox, query=True, value=True)
        snap_and_merge_vertices(tolerance, merge_same_object)

    def on_clear_button_clicked(self, *args):
        """
        'データをクリア'ボタンがクリックされた際に呼び出される。
        記録された頂点データを削除する。
        """
        clear_vertex_log()

    def on_show_log_button_clicked(self, *args):
        """
        'データを出力'ボタンがクリックされた際に呼び出される。
        現在記録されている頂点データをコンソールに表示する。
        """
        show_vertex_log()

# UI表示
VertexSnapperUI()
