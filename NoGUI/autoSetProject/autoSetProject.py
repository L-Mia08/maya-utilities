#--------------------------------------------------------------------------
# ScriptName: autoSetProject
# Author: Naruse,T.T,GPT-4o
# Contents: autoSetProjectを設定するスクリプト
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
import os

def set_project_on_scene_open():
    """シーンが開かれたときにプロジェクトを設定する"""
    # 現在のシーンのファイルパスを取得
    scene_path = cmds.file(query=True, sceneName=True)

    if scene_path:
        # シーンファイルのディレクトリを取得
        scene_dir = os.path.dirname(scene_path)
        # Windows形式のパスに変換
        scene_dir = scene_dir.replace('/', '\\')

        # workspace.melのあるディレクトリを見つける
        workspace_mel_dir = find_workspace_mel_dir(scene_dir)

        if workspace_mel_dir:
            # workspace.melが見つかったディレクトリをプロジェクトとして設定
            workspace_mel_dir = workspace_mel_dir.replace('/', '\\')  # Windows形式に変換
            cmds.workspace(workspace_mel_dir, openWorkspace=True)
            print(f"セットプロジェクトしました: {workspace_mel_dir}")
        else:
            print("親ディレクトリにworkspace.melが見つかりません。プロジェクトが設定されていません。")
    else:
        print("シーンが開いていません。プロジェクトが設定されていません。")

def find_workspace_mel_dir(start_dir):
    """start_dirから上位ディレクトリを再帰的に検索してworkspace.melを見つける"""
    current_dir = start_dir
    while current_dir:
        workspace_mel_path = os.path.join(current_dir, "workspace.mel")
        workspace_mel_path = workspace_mel_path.replace('/', '\\')  # Windows形式に変換
        if os.path.exists(workspace_mel_path):
            return current_dir
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            # ルートディレクトリに到達した場合、探索を終了
            break
        current_dir = parent_dir
    return None

# コールバックを登録
callbacks = []

def register_callbacks():
    """Mayaの起動時にコールバックを登録"""
    global callbacks
    callbacks.append(cmds.scriptJob(event=["SceneOpened", set_project_on_scene_open], protected=True))

def unregister_callbacks():
    """コールバックを解除"""
    global callbacks
    for callback in callbacks:
        cmds.scriptJob(kill=callback, force=True)
    callbacks = []

# Mayaの起動時にコールバックを登録
register_callbacks()