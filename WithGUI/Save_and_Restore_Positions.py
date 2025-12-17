#--------------------------------------------------------------------------
# ScriptName: Save_and_Restore_Positions
# Author: Naruse,GPT-4o
# Contents  :オブジェクトをリストに追加し移動、回転の座標を記録し、記録した座標に戻す。
# CreatedDate: 2024年12月02日
# LastUpdate: 2024年12月22日
# Version: 1.1
#
# 《License》
# Copyright (c) 2024 Naruse
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php
#--------------------------------------------------------------------------


import maya.cmds as cmds

# グローバル変数を定義
saved_object_data = {}  # UUIDをキーとして、オブジェクト名と座標を保持


# 選択されたオブジェクトがオブジェクトモードであるかをチェックする
def is_object_mode(selection):
    for obj in selection:
        if not cmds.objectType(obj, isType="transform"):
            return False
    return True


# 選択されているオブジェクトとその座標を保存する
def save_selected_objects_and_positions():
    global saved_object_data

    # 現在の選択状態を取得
    initial_selection = cmds.ls(selection=True)
    if not initial_selection:
        cmds.warning("オブジェクトが選択されていません。")
        return

    if not is_object_mode(initial_selection):
        cmds.warning("オブジェクトモードのみ利用できます。")
        return

    # 上書きされたオブジェクトを記録するリスト
    updated_objects = []

    for obj in initial_selection:
        uuid = cmds.ls(obj, uuid=True)[0]  # UUID取得
        position = cmds.xform(obj, query=True, worldSpace=True, translation=True)  # 座標取得
        rotation = cmds.xform(obj, query=True, worldSpace=True, rotation=True)  # 回転取得

        if uuid in saved_object_data:
            # 名前が変更された場合、保存データも更新
            if saved_object_data[uuid]["name"] != obj:
                saved_object_data[uuid]["name"] = obj
                print(f"オブジェクト名が更新されました: {saved_object_data[uuid]['name']} -> {obj}")

            # 座標を上書き保存
            saved_object_data[uuid]["position"] = position
            # 回転を上書き保存
            saved_object_data[uuid]["rotation"] = rotation
            updated_objects.append(obj)  # 上書きされたオブジェクトを記録

        else:
            # 新規データとして保存
            saved_object_data[uuid] = {"name": obj, "position": position, "rotation": rotation}

    # リスト表示を更新
    cmds.textScrollList("objectList", edit=True, removeAll=True)
    for data in saved_object_data.values():
        # リスト名を変数に
        list_item = f"{data['name']} || Tra: {' '.join(map(lambda x: str(int(x)), data['position']))} | Rot: {' '.join(map(lambda x: str(int(x)), data['rotation']))}"

        cmds.textScrollList("objectList", edit=True, append=list_item)

        # アイテムを選択状態にする
        cmds.textScrollList("objectList", edit=True, selectItem=list_item)

        # 変数を出力
        print(f"オブジェクト名:{obj} | 座標:{position} | 回転:{rotation}を保存または上書きしました。")
        print(f"オブジェクト名:{obj} | UUID:{uuid}を保存または上書きしました。")

    # 上書きされたオブジェクトをログに表示
    if updated_objects:
        print(f"上書きされたオブジェクト名: {updated_objects}")
    else:
        print("上書きされたオブジェクトはありません。")


# 保存された座標に選択されたオブジェクトを移動する
def restore_selected_object_position():
    global saved_object_data

    selected_in_list = cmds.textScrollList("objectList", query=True, selectItem=True)
    if not selected_in_list:
        cmds.warning("リストからオブジェクトを選択してください。")
        return

    for selected_obj in selected_in_list:
        obj_name = selected_obj.split(" || ")[0]

        for uuid, data in saved_object_data.items():
            if data["name"] == obj_name:
                # オブジェクト名で特定
                if cmds.objExists(obj_name):
                    cmds.xform(obj_name, worldSpace=True, translation=data["position"])
                    cmds.xform(obj_name, worldSpace=True, rotation=data["rotation"])
                    print(f"{obj_name} を座標 {data['position']} と回転 {data['rotation']} に移動しました。")
                else:
                    # UUIDでオブジェクトを特定
                    new_obj_name = cmds.ls(uuid)
                    if new_obj_name:
                        print(f"UUID: {uuid} から取得したオブジェクト名: {new_obj_name[0]}")
                        cmds.xform(new_obj_name[0], worldSpace=True, translation=data["position"])
                        cmds.xform(new_obj_name[0], worldSpace=True, rotation=data["rotation"])
                        print(f"UUIDを使用して {new_obj_name[0]} を座標 {data['position']} と回転 {data['rotation']} に移動しました。")

                        # 名前を更新し、リストの表示も置き換え
                        obj_name = new_obj_name[0]  # 名前を更新
                        data["name"] = obj_name

                        # リストアイテムを置き換える
                        all_items = cmds.textScrollList("objectList", query=True, allItems=True)
                        if all_items:
                            for i, item in enumerate(all_items):
                                if selected_obj == item:
                                    new_item = f"{obj_name} || Tra: {' '.join(map(lambda x: str(int(x)), data['position']))} | Rot: {' '.join(map(lambda x: str(int(x)), data['rotation']))}"
                                    cmds.textScrollList("objectList", edit=True, removeIndexedItem=(i + 1))  # 古い項目を削除
                                    cmds.textScrollList("objectList", edit=True, appendPosition=[i + 1, new_item])  # 新しい項目を挿入
                                    print(f"UUID: {uuid} | オブジェクト名: {obj_name} | リスト内のオブジェクト名を {obj_name} に変更しました")

                                    # 新しいアイテムを選択状態にする
                                    cmds.textScrollList("objectList", edit=True, selectItem=new_item)
                                    break
                    else:
                        print(f"UUID: {uuid} に対応するオブジェクトが見つかりません。")
                break
        else:
            cmds.warning(f"{obj_name} は保存リストに存在しません。")


# リストから選択されたオブジェクトを削除する
def delete_selected_from_list():
    global saved_object_data

    selected_in_list = cmds.textScrollList("objectList", query=True, selectItem=True)
    if not selected_in_list:
        cmds.warning("リストからオブジェクトを選択してください。")
        return

    for selected_obj in selected_in_list:
        obj_name = selected_obj.split(" || ")[0]

        for uuid, data in list(saved_object_data.items()):
            if data["name"] == obj_name:
                saved_object_data.pop(uuid)
                cmds.textScrollList("objectList", edit=True, removeItem=selected_obj)
                print(f"{obj_name} をリストから削除しました。")
                break
        else:
            cmds.warning(f"{obj_name} は保存リストに存在しません。")

# ここからGUI
# Save and Restore Positions GUI
def create_gui():
    if cmds.window("saveRestoreWindow", exists=True):
        cmds.deleteUI("saveRestoreWindow")

    window = cmds.window("saveRestoreWindow", title="Save and Restore Positions", widthHeight=(300, 400))
    cmds.columnLayout(adjustableColumn=True)

    cmds.textScrollList("objectList", allowMultiSelection=True, height=200)

    cmds.separator(height=10, style='in')  # 仕切り

    cmds.button(label="Save Selected Positions", command=lambda x: save_selected_objects_and_positions())

    cmds.separator(height=3, style='none')  # 隙間

    cmds.button(label="Restore Selected Positions", command=lambda x: restore_selected_object_position())

    cmds.separator(height=10, style='in')  # 仕切り

    cmds.button(label="Delete Selected from List", command=lambda x: delete_selected_from_list(), backgroundColor=(0.8, 0.3, 0.3))

    cmds.showWindow(window)

# GUI表示
create_gui()