# --------------------------------------------------------------------------
# ScriptName: Material obj Export
# Author: Naruse,GPT-4o
# Contents: 選択したオブジェクトのマテリアルを球に適用し、球または板をエクスポート、インポートできるスクリプト
# CreatedDate: 2025年3月4日
# LastUpdate: 2025年3月4日
# Version:0.1
#
# 《License》
# Copyright (c) 2025 Naruse
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php
# --------------------------------------------------------------------------

import maya.cmds as cmds
import os
import subprocess

# 現在のシーンのパスを取得
scene_path = cmds.file(q=True, sceneName=True)

if scene_path:
    scene_dir = os.path.dirname(scene_path)  # シーンのディレクトリ
    while scene_dir and not scene_dir.endswith("scenes"):
        scene_dir = os.path.dirname(scene_dir)  # "scenes" まで戻る
else:
    # シーンが未保存ならデフォルトパス
    scene_dir = os.path.expanduser("~/Documents/maya/scenes")

# MMaterial_Obj_Export フォルダを設定
export_folder = os.path.join(scene_dir, "Material_obj_Export").replace('/', '\\')
if not os.path.exists(export_folder):
    os.makedirs(export_folder)

# グローバル変数
created_objects = []  # 生成したオブジェクト（球または板）を管理するリスト

def has_texture(material):
    """ 指定されたマテリアルがテクスチャを持つか判定する """
    file_nodes = cmds.listConnections(material, type="file") or []
    return bool(file_nodes)

def apply_selected_material_to_objects():
    global created_objects

    selection = cmds.ls(selection=True)
    if not selection:
        cmds.warning("オブジェクトを選択してください。")
        return

    # shadingEngine を取得
    shading_groups = cmds.listConnections(selection[0], type='shadingEngine') or []
    if not shading_groups:
        shading_groups = cmds.listHistory(selection[0], future=True, pruneDagObjects=True)
        shading_groups = cmds.ls(shading_groups, type='shadingEngine')

    if not shading_groups:
        cmds.warning("選択したオブジェクトにマテリアルが適用されていません。")
        return

    # マテリアルを取得（shadingEngine の surfaceShader から）
    materials = []
    for sg in shading_groups:
        material = cmds.listConnections(f"{sg}.surfaceShader", source=True, destination=False)
        if material:
            materials.extend(material)

    materials = list(set(materials))  # 重複を排除

    if not materials:
        cmds.warning("マテリアルを取得できませんでした。")
        return

    # 既存のオブジェクトを削除
    if created_objects:
        for obj in created_objects:
            if cmds.objExists(obj):
                cmds.delete(obj)
    created_objects = []

    created_info = []
    for i, material in enumerate(materials):
        object_name = f"{material}_pMesh_{i+1}"

        # テクスチャの有無をチェックし、適切なオブジェクトを作成
        if has_texture(material):
            obj = cmds.polyPlane(name=object_name, width=2, height=2, subdivisionsX=1, subdivisionsY=1)[0]
            cmds.rotate(90, 0, 0, obj, absolute=True)  # X軸を90度回転
        else:
            obj = cmds.polySphere(name=object_name)[0]

        cmds.select(obj)
        cmds.hyperShade(assign=material)
        created_objects.append(obj)

        created_info.append(f"オブジェクト: {object_name}\nマテリアル: {material}")

    cmds.confirmDialog(title="マテリアル取得完了", message=f"{len(created_objects)} つのオブジェクトを作成しました。\n\n" + "\n\n".join(created_info), button="OK")



def export_objects():
    global created_objects

    if not created_objects:
        cmds.warning("エクスポートするオブジェクトが存在しません。")
        return

    if not os.path.exists(export_folder):
        os.makedirs(export_folder)

    exported_files = []
    for obj in created_objects:
        if not cmds.objExists(obj):
            continue

        material_name = obj.replace("_pMesh", "")
        export_path = os.path.join(export_folder, f"{material_name}.mb").replace('/', '\\')

        cmds.select(obj)
        cmds.file(export_path, force=True, options="v=0;", type="mayaBinary", exportSelected=True)
        exported_files.append(f"{material_name}.mb\n{export_path}")

    if exported_files:
        exported_text = "\n\n".join(exported_files)
        cmds.confirmDialog(title="エクスポート完了", message=f"{len(exported_files)} つのオブジェクトをエクスポートしました。\n\n{exported_text}", button="OK")

def import_object():
    initial_dir = export_folder if os.path.exists(export_folder) else scene_dir

    file_path = cmds.fileDialog2(fileMode=1, caption="インポートするオブジェクトを選択", fileFilter="Maya Binary (*.mb)", dir=initial_dir)
    if not file_path:
        return

    cmds.file(file_path[0], i=True, type="mayaBinary", ignoreVersion=True, mergeNamespacesOnClash=False, options="v=0;")
    cmds.confirmDialog(title="インポート完了", message="ファイルをインポートしました。", button="OK")

def apply_material_between_selected():
    selection = cmds.ls(selection=True)
    if len(selection) < 2:
        cmds.warning("2つのオブジェクトを選択してください。")
        return

    source_obj, target_obj = selection[1], selection[0]
    shading_groups = cmds.ls(cmds.listHistory(source_obj, future=True, pruneDagObjects=True) or [], type="shadingEngine")

    if not shading_groups:
        cmds.warning("マテリアルを取得できませんでした。")
        return

    materials = cmds.listConnections(shading_groups[0] + ".surfaceShader", source=True, destination=False) or []
    if not materials:
        cmds.warning("マテリアルが見つかりません。")
        return

    cmds.select(target_obj, replace=True)
    cmds.hyperShade(assign=materials[0])
    cmds.select(clear=True)

    cmds.confirmDialog(title="マテリアル適用", message=f"{target_obj} に {materials[0]} を適用しました。", button="OK")

def open_export_folder_in_explorer(*args):
    """エクスポートフォルダをエクスプローラーで開く"""
    if os.path.exists(export_folder):
        if os.name == 'nt':  # Windows
            subprocess.Popen(f'explorer "{export_folder}"')
            print(f"エクスポートフォルダのパス: {export_folder}")
        elif os.name == 'posix':  # macOS
            subprocess.Popen(['open', export_folder])
            print(f"エクスポートフォルダのパス: {export_folder}")
        else:
            cmds.warning("ファイルエクスプローラーを開くにはサポートされていないOSです")
    else:
        cmds.warning("エクスポートフォルダが存在しません")

def create_ui():
    if cmds.window("materialExportUI", exists=True):
        cmds.deleteUI("materialExportUI")

    window = cmds.window("materialExportUI", title="Material obj Export", widthHeight=(380, 240))
    cmds.columnLayout(adjustableColumn=True)

    cmds.separator(height=3, style='none')
    cmds.button(label="マテリアルを取得しオブジェクトを作成", command=lambda _: apply_selected_material_to_objects())
    cmds.separator(height=5, style='none')
    cmds.button(label="エクスポート", command=lambda _: export_objects())
    cmds.separator(height=5, style='none')
    cmds.button(label="インポート", command=lambda _: import_object())
    cmds.separator(height=5, style='none')
    cmds.button(label="B→Aにマテリアルを適用", command=lambda _: apply_material_between_selected())
    cmds.separator(height=5, style='in')
    cmds.button(label="エクスポートフォルダを開く", command=lambda _: open_export_folder_in_explorer())  # 新しいボタンを追加

    cmds.setParent("..")
    cmds.showWindow(window)

create_ui()