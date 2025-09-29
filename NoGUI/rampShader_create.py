#--------------------------------------------------------------------------
# ScriptName: rampShader_create
# Author: Naruse,GPT-5
# Contents   :サーフェス シェーダやランプシェーダを作成してカラーとシャドウのテクスチャを設定してノードを作成するスクリプト
# CreatedDate: 2025年09月13日
# LastUpdate: 2025年09月29日
# Version: 0.2
#
# 《License》
# Copyright (c) 2025 Naruse
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php
#--------------------------------------------------------------------------

import maya.cmds as cmds
import os

def connect_place2d(file_node):
    """fileノードに対応するplace2dTextureノードを作成して接続"""
    place2d = cmds.shadingNode("place2dTexture", asUtility=True, name=file_node + "_place2d")
    connections = [
        ("coverage", "coverage"),
        ("translateFrame", "translateFrame"),
        ("rotateFrame", "rotateFrame"),
        ("mirrorU", "mirrorU"),
        ("mirrorV", "mirrorV"),
        ("stagger", "stagger"),
        ("wrapU", "wrapU"),
        ("wrapV", "wrapV"),
        ("repeatUV", "repeatUV"),
        ("offset", "offset"),
        ("rotateUV", "rotateUV"),
        ("noiseUV", "noiseUV"),
        ("vertexUvOne", "vertexUvOne"),
        ("vertexUvTwo", "vertexUvTwo"),
        ("vertexUvThree", "vertexUvThree"),
        ("vertexCameraOne", "vertexCameraOne"),
        ("outUV", "uv"),
        ("outUvFilterSize", "uvFilterSize")
    ]
    for src, dst in connections:
        cmds.connectAttr(place2d + "." + src, file_node + "." + dst, force=True)
    return place2d

def setup_ramp_shader(ramp_shader):
    """rampShader の設定を更新"""
    if not cmds.objExists(ramp_shader):
        cmds.warning(f"{ramp_shader} が存在しません。")
        return

    # Color タブ設定
    # Color[0] の Interpolation を None (0) に
    if cmds.attributeQuery('color', node=ramp_shader, exists=True):
        attr_name = f"{ramp_shader}.color[0].color_Interp"
        if cmds.objExists(attr_name):
            cmds.setAttr(attr_name, 0)  # 0 = None

        # Color[0] 白
        if cmds.attributeQuery('color_Color', node=f"{ramp_shader}.color[0]", exists=True):
            cmds.setAttr(f"{ramp_shader}.color[0].color_Color", 1, 1, 1, type="double3")

    # Color Input を Brightness (2) に
    if cmds.attributeQuery('colorInput', node=ramp_shader, exists=True):
        cmds.setAttr(f"{ramp_shader}.colorInput", 2)

    # Incandescence タブ設定
    if cmds.attributeQuery('incandescence', node=ramp_shader, exists=True):
        num_elements = cmds.getAttr(f"{ramp_shader}.incandescence", size=True)
        for i in range(num_elements):
            cmds.setAttr(f"{ramp_shader}.incandescence[{i}]", 1, 1, 1, type="double3")
    if cmds.attributeQuery('diffuse', node=ramp_shader, exists=True):
        cmds.setAttr(f"{ramp_shader}.diffuse", 1.0)

    # Specular タブ設定
    if cmds.attributeQuery('specularity', node=ramp_shader, exists=True):
        cmds.setAttr(f"{ramp_shader}.specularity", 0.0)
    if cmds.attributeQuery('eccentricity', node=ramp_shader, exists=True):
        cmds.setAttr(f"{ramp_shader}.eccentricity", 0.0)

    # color[1] 作成・更新（黒）
    existing_colors = cmds.getAttr(f"{ramp_shader}.color", size=True)
    if existing_colors < 2:
        cmds.setAttr(f"{ramp_shader}.color[1].color_Position", 0.5)
        cmds.setAttr(f"{ramp_shader}.color[1].color_Color", 0, 0, 0, type="double3")
        cmds.setAttr(f"{ramp_shader}.color[1].color_Interp", 1)
    else:
        cmds.setAttr(f"{ramp_shader}.color[1].color_Position", 0.5)
        cmds.setAttr(f"{ramp_shader}.color[1].color_Color", 0, 0, 0, type="double3")
        cmds.setAttr(f"{ramp_shader}.color[1].color_Interp", 1)

    # Color[1] の Interpolation を None (1) に
    if cmds.attributeQuery('color', node=ramp_shader, exists=True):
        attr_name = f"{ramp_shader}.color[1].color_Interp"
        if cmds.objExists(attr_name):
            cmds.setAttr(attr_name, 0)  # 0 = None

def create_custom_shader(shader_name="mySurfaceShader"):
    # 既存ノード削除
    if cmds.objExists(shader_name):
        cmds.delete(shader_name)
    if cmds.objExists(shader_name + "SG"):
        cmds.delete(shader_name + "SG")

    # surfaceShader
    surface_shader = cmds.shadingNode('surfaceShader', asShader=True, name=shader_name)
    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=surface_shader + "SG")
    cmds.connectAttr(surface_shader + ".outColor", shading_group + ".surfaceShader", force=True)

    # layeredTexture
    layered_tex = cmds.shadingNode('layeredTexture', asTexture=True, name=shader_name + "_layeredTex")
    cmds.connectAttr(layered_tex + ".outColor", surface_shader + ".outColor", force=True)

    # rampShader 2つ
    ramp_shader1 = cmds.shadingNode('rampShader', asTexture=True, name=shader_name + "_rampShader1")
    ramp_shader2 = cmds.shadingNode('rampShader', asTexture=True, name=shader_name + "_rampShader2")

    # layeredTexture に接続
    cmds.connectAttr(ramp_shader1 + ".outColorR", layered_tex + ".inputs[0].alpha", force=True)
    cmds.connectAttr(ramp_shader2 + ".outColorR", layered_tex + ".inputs[1].alpha", force=True)

    # rampShader 設定
    setup_ramp_shader(ramp_shader1)
    setup_ramp_shader(ramp_shader2)

    # File ノード1（シャドウ用）
    shadow_path = cmds.fileDialog2(fileMode=1, caption="シャドウテクスチャを選択してください")
    if shadow_path:
        shadow_basename = os.path.splitext(os.path.basename(shadow_path[0]))[0]
        file1 = cmds.shadingNode("file", asTexture=True, name=shadow_basename)
        connect_place2d(file1)
        cmds.setAttr(file1 + ".fileTextureName", shadow_path[0], type="string")
        cmds.connectAttr(file1 + ".outColor", layered_tex + ".inputs[1].color", force=True)

    # File ノード2（カラー用）
    color_path = cmds.fileDialog2(fileMode=1, caption="カラーテクスチャを選択してください")
    if color_path:
        color_basename = os.path.splitext(os.path.basename(color_path[0]))[0]
        file2 = cmds.shadingNode("file", asTexture=True, name=color_basename)
        connect_place2d(file2)
        cmds.setAttr(file2 + ".fileTextureName", color_path[0], type="string")
        cmds.connectAttr(file2 + ".outColor", layered_tex + ".inputs[2].color", force=True)

    print("Shader setup complete!")

# ---- 実行 ----
user_name = cmds.promptDialog(
    title='シェーダー名入力',
    message='サーフェスシェーダ名を入力:',
    button=['OK', 'Cancel'],
    defaultButton='OK',
    cancelButton='Cancel',
    dismissString='Cancel')

if user_name == 'OK':
    shader_name = cmds.promptDialog(query=True, text=True)
    create_custom_shader(shader_name)
