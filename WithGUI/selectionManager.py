import maya.cmds as cmds

class SelectionManager:
    def __init__(self):
        self.saved_selections = []
        self.window = "selectionManagerUI"

    def save_selection(self):
        selection = cmds.ls(selection=True)
        if selection:
            self.saved_selections.append(selection)
            self.refresh_list()
        else:
            cmds.warning("No objects selected.")

    def restore_selection(self, indices):
        selections = [self.saved_selections[i] for i in indices if 0 <= i < len(self.saved_selections)]
        if selections:
            cmds.select(sum(selections, []), replace=True)
        else:
            cmds.warning("Invalid selection index.")

    def delete_selection(self, indices):
        for index in sorted(indices, reverse=True):
            if 0 <= index < len(self.saved_selections):
                del self.saved_selections[index]
        self.refresh_list()

    def refresh_list(self):
        cmds.textScrollList("selectionList", edit=True, removeAll=True)
        for i, selection in enumerate(self.saved_selections):
            cmds.textScrollList("selectionList", edit=True, append=f"Set {i+1}: {', '.join(selection)}")

    def create_ui(self):
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window)
        
        self.window = cmds.window(self.window, title="Selection Manager", widthHeight=(300, 400))
        cmds.columnLayout(adjustableColumn=True)
        cmds.textScrollList("selectionList", height=200, allowMultiSelection=True, selectCommand=lambda: self.on_select())
        cmds.button(label="Save Selection", command=lambda _: self.save_selection())
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

selection_manager = SelectionManager()
selection_manager.create_ui()
