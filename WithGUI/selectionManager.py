import maya.cmds as cmds

class SelectionManager:
    def __init__(self):
        # 保存された選択セットを保持するリスト
        # 各セットは [{'name': 'pCube1', 'uuid': 'xxxx-xxxx'}] のリスト
        self.saved_selections = []
        self.window = "selectionManagerUI"

    def save_selection(self):
        selection = cmds.ls(selection=True)
        if selection:
            # 名前とUUIDを保存
            selection_data = []
            for obj in selection:
                try:
                    obj_uuid = cmds.ls(obj, uuid=True)[0]
                    selection_data.append({'name': obj, 'uuid': obj_uuid})
                except IndexError:
                    # UUIDが取得できない場合はスキップ
                    cmds.warning(f"Cannot get UUID for {obj}")
            if selection_data:
                self.saved_selections.append(selection_data)
                self.refresh_list()
        else:
            cmds.warning("No objects selected.")

    def restore_selection(self, indices):
        objs_to_select = []
        for i in indices:
            if 0 <= i < len(self.saved_selections):
                for entry in self.saved_selections[i]:
                    # UUIDから現在の名前を取得して存在確認
                    try:
                        current_name = cmds.ls(entry['uuid'])[0]
                        objs_to_select.append(current_name)
                    except IndexError:
                        # 存在しないオブジェクトはスキップ
                        cmds.warning(f"Object with UUID {entry['uuid']} not found.")
        if objs_to_select:
            cmds.select(objs_to_select, replace=True)
        else:
            cmds.warning("No valid objects to select.")

    def delete_selection(self, indices):
        for index in sorted(indices, reverse=True):
            if 0 <= index < len(self.saved_selections):
                del self.saved_selections[index]
        self.refresh_list()

    def refresh_list(self):
        cmds.textScrollList("selectionList", edit=True, removeAll=True)
        for i, selection in enumerate(self.saved_selections):
            # UUIDでも参照できるよう、常に最新の名前に更新
            names = []
            for entry in selection:
                try:
                    current_name = cmds.ls(entry['uuid'])[0]
                    entry['name'] = current_name  # 名前更新
                    names.append(current_name)
                except IndexError:
                    names.append(f"<deleted:{entry['uuid']}>")
            cmds.textScrollList("selectionList", edit=True, append=f"Set {i+1}: {', '.join(names)}")

    def create_ui(self):
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window)

        self.window = cmds.window(self.window, title="Selection Manager", widthHeight=(300, 400))
        cmds.columnLayout(adjustableColumn=True)

        cmds.textScrollList(
            "selectionList",
            height=200,
            allowMultiSelection=True,
            selectCommand=lambda: self.on_select()
        )
        cmds.button(label="Save Selection", command=lambda _: self.save_selection())
        cmds.button(label="Refresh_list", command=lambda _: self.refresh_list())
        cmds.button(label="Delete Selection", command=lambda _: self.delete_selected())
        cmds.showWindow(self.window)

    def on_select(self):
        selected_indices = cmds.textScrollList("selectionList", query=True, selectIndexedItem=True)
        if selected_indices:
            self.restore_selection([i - 1 for i in selected_indices])

    def delete_selected(self):
        selected_indices = cmds.textScrollList("selectionList", query=True, selectIndexedItem=True)
        if selected_indices:
            self.delete_selection([i - 1 for i in selected_indices])

# 実行
selection_manager = SelectionManager()
selection_manager.create_ui()

#--------------------------------------------------------------------------
# ScriptName: SelectionManager
# Author: Naruse,GPT-5
# CreatedDate: 2024年12月02日
# LastUpdate: 2025年08月30日
# Version: 1.2
#
# 《License》
# Copyright (c) 2025 Naruse
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php
#--------------------------------------------------------------------------