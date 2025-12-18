#--------------------------------------------------------------------------
# ScriptName: autoSave
# Author: Naruse,T.T,GPT-4o
# Contents: autoSaveを設定するスクリプト
# CreatedDate: 2024年06月04日
# LastUpdate: 2025年11月25日
# Version: 0.3
#
# 《License》
# Copyright (c) 2025 Naruse
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php
#--------------------------------------------------------------------------

import maya.cmds as cmds
import maya.mel as mel
import os

autosave_interval = 600  # オートセーブ間隔（秒） 60以上に設定する

def set_autosave_directory():
    scene_path = cmds.file(query=True, sceneName=True)
    if not scene_path:
        print("シーンファイルが開かれていません。")
        return

    scene_name = os.path.basename(scene_path)
    scene_name_no_ext = os.path.splitext(scene_name)[0]
    project_dir = cmds.workspace(query=True, rootDirectory=True)

    autosave_dir = os.path.join(project_dir, "autosave", scene_name_no_ext)
    autosave_dir = autosave_dir.replace('\\', '/')
    print("取得パス: {}".format(autosave_dir))

    if not os.path.exists(autosave_dir):
        os.makedirs(autosave_dir)

    # MELスクリプトとしてオートセーブ設定を反映（パスは "" で囲む）
    mel.eval('autoSave -en true;')
    mel.eval('autoSave -dst 1;')
    mel.eval(f'autoSave -fol "{autosave_dir}";')
    mel.eval(f'autoSave -int {autosave_interval};')

    mel_autosave_path = mel.eval('autoSave -q -fol;')
    print("オートセーブディレクトリを設定しました: {}".format(mel_autosave_path))

# 「名前を付けて保存」時にディレクトリを更新
def on_file_saved(*args):
    set_autosave_directory()

# ファイルが開かれたときにスクリプトを実行
callbacks = []

def on_scene_opened(*args):
    set_autosave_directory()

# ScriptJobの登録
callbacks.append(cmds.scriptJob(event=["SceneOpened", on_scene_opened]))
callbacks.append(cmds.scriptJob(event=["SceneSaved", on_file_saved]))

# Mayaを閉じるときにscriptJobを削除
def remove_callbacks(*args):
    for callback in callbacks:
        if cmds.scriptJob(exists=callback):
            cmds.scriptJob(kill=callback, force=True)

callbacks.append(cmds.scriptJob(event=["quitApplication", remove_callbacks]))
