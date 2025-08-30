import maya.cmds as cmds

class SelectionManager:
    def __init__(self):
        # 保存された選択セットを保持するリスト
        self.saved_selections = []
        # UIウィンドウの名前
        self.window = "selectionManagerUI"

    def save_selection(self):
        # 現在選択されているオブジェクトを取得
        selection = cmds.ls(selection=True)
        if selection:
            # 選択がある場合はリストに保存
            self.saved_selections.append(selection)
            # UIのリストを更新
            self.refresh_list()
        else:
            # 選択がない場合は警告を表示
            cmds.warning("No objects selected.")

    def restore_selection(self, indices):
        # 渡されたインデックスに対応する選択セットを取り出す
        selections = [self.saved_selections[i] for i in indices if 0 <= i < len(self.saved_selections)]
        if selections:
            # 複数の選択セットを展開して選択を復元
            cmds.select(sum(selections, []), replace=True)
        else:
            # 無効なインデックスの場合は警告
            cmds.warning("Invalid selection index.")

    def delete_selection(self, indices):
        # 指定されたインデックスの選択セットを削除
        # （大きいインデックスから削除しないとズレるので reverse=True）
        for index in sorted(indices, reverse=True):
            if 0 <= index < len(self.saved_selections):
                del self.saved_selections[index]
        # UIのリストを更新
        self.refresh_list()

    def refresh_list(self):
        # リストをクリア
        cmds.textScrollList("selectionList", edit=True, removeAll=True)
        # 保存済みの選択セットをリストに表示
        for i, selection in enumerate(self.saved_selections):
            cmds.textScrollList(
                "selectionList", edit=True,
                append=f"Set {i+1}: {', '.join(selection)}"
            )

    def create_ui(self):
        # 既に同名のウィンドウが存在する場合は削除
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window)

        # 新規ウィンドウを作成
        self.window = cmds.window(self.window, title="Selection Manager", widthHeight=(300, 400))
        cmds.columnLayout(adjustableColumn=True)

        # 選択セット一覧を表示するリスト
        cmds.textScrollList(
            "selectionList",
            height=200,
            allowMultiSelection=True,
            selectCommand=lambda: self.on_select()
        )

        # 選択を保存するボタン
        cmds.button(label="Save Selection", command=lambda _: self.save_selection())
        # 選択を削除するボタン
        cmds.button(label="Delete Selection", command=lambda _: self.delete_selected())

        # ウィンドウを表示
        cmds.showWindow(self.window)

    def on_select(self):
        # UIリストで選択されたインデックスを取得
        selected_indices = cmds.textScrollList("selectionList", query=True, selectIndexedItem=True)
        if selected_indices:
            # Mayaのリストは1始まりなので -1 して変換
            self.restore_selection([i - 1 for i in selected_indices])

    def delete_selected(self):
        # UIリストで選択されたインデックスを取得
        selected_indices = cmds.textScrollList("selectionList", query=True, selectIndexedItem=True)
        if selected_indices:
            # Mayaのリストは1始まりなので -1 して変換
            self.delete_selection([i - 1 for i in selected_indices])


# 実行部分
selection_manager = SelectionManager()
selection_manager.create_ui()
