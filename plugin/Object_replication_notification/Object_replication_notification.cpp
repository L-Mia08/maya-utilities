#include <maya/MFnPlugin.h>
#include <maya/MGlobal.h>
#include <maya/MModelMessage.h>
#include <maya/MMessage.h>
#include <maya/MSelectionList.h>
#include <maya/MItSelectionList.h>
#include <maya/MDagPath.h>
#include <maya/MFnDagNode.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MStatus.h>
#include <maya/MString.h>

#include <sstream>
#include <vector>

static MCallbackId g_afterDuplicateCallback = 0;

// 選択から名前リストを取得
static std::vector<std::string> getSelectionNames()
{
    std::vector<std::string> names;
    MSelectionList sel;
    if (MGlobal::getActiveSelectionList(sel) != MS::kSuccess) return names;

    MItSelectionList it(sel);
    for (; !it.isDone(); it.next()) {
        MDagPath dagPath;
        MObject node;
        MStatus stat;

        // DAG パスを試す
        stat = it.getDagPath(dagPath);
        if (stat == MS::kSuccess) {
            MFnDagNode fnDag(dagPath, &stat);
            if (stat == MS::kSuccess) {
                // フルパスじゃなく短い名前だけにする
                names.push_back(std::string(fnDag.name().asChar()));
                continue;
            }
        }

        // DAG でなければ依存ノード名を取る
        stat = it.getDependNode(node);
        if (stat == MS::kSuccess) {
            MFnDependencyNode fnDep(node, &stat);
            if (stat == MS::kSuccess) {
                names.push_back(std::string(fnDep.name().asChar()));
                continue;
            }
        }
    }

    return names;
}


// コールバック本体：複製後に呼ばれる
void afterDuplicateCallback(void* /*clientData*/)
{
    // 現在のフォーカスパネルを取得
    MString panel;
    MGlobal::executeCommand("getPanel -wf", panel);

    // Hypershade での操作なら無視する
    if (panel.indexW("hyperShadePanel") != -1) {
        return;
    }

    std::vector<std::string> names = getSelectionNames();
    MString pythonCmd;

    // デフォルトオブジェクトセットが含まれている場合
    bool containsDefault = false;
    for (const auto& name : names) {
        if (name == "defaultObjectSet" ||
            name == "defaultLightSet" ||
            name == "defaultHideFaceDataSet") {
            containsDefault = true;
            break;
        }
    }

    if (containsDefault) {
        pythonCmd =
            "import maya.cmds as cmds\n"
            "cmds.inViewMessage(amg='<hl>一部のオブジェクト、またはそのオブジェクトは複製できませんでした</hl>', "
            "pos='topCenter', fade=True, fadeStayTime=2000, alpha=.9)";
    }
    else if (names.empty()) {
        // 0件 → 複製失敗の可能性
        pythonCmd =
            "import maya.cmds as cmds\n"
            "cmds.inViewMessage(amg='<hl>複製に失敗している可能性があります</hl>', "
            "pos='topCenter', fade=True, fadeStayTime=2000, alpha=.9)";
    }
    else if (names.size() == 1) {
        // 1件 → オブジェクト名を表示
        MString objName(names[0].c_str());
        pythonCmd =
            "import maya.cmds as cmds\n"
            "cmds.inViewMessage(amg='<hl>" + objName +
            " が複製されました</hl>', "
            "pos='topCenter', fade=True, fadeStayTime=2000, alpha=.9)";
    }
    else {
        // 2件以上 → 件数だけ表示
        int count = static_cast<int>(names.size());
        pythonCmd =
            "import maya.cmds as cmds\n"
            "cmds.inViewMessage(amg='<hl>" + MString() + count +
            " つのオブジェクトが複製されました</hl>', "
            "pos='topCenter', fade=True, fadeStayTime=2000, alpha=.9)";
    }

    if (!pythonCmd.isEmpty()) {
        MGlobal::executePythonCommand(pythonCmd);
    }
}


// プラグイン初期化
MStatus initializePlugin(MObject obj)
{
    MStatus status;
    MFnPlugin plugin(obj, "Naruse,GPT-5", "2025.09.12 v1.2", "2025", &status);
    if (!status) {
        MGlobal::displayError("オブジェクト複製通知プラグイン: MFnPlugin の初期化に失敗しました");
        return status;
    }

    // 既存コールバックを削除してから登録（多重登録防止）
    if (g_afterDuplicateCallback != 0) {
        MMessage::removeCallback(g_afterDuplicateCallback);
        g_afterDuplicateCallback = 0;
    }

    g_afterDuplicateCallback = MModelMessage::addAfterDuplicateCallback(afterDuplicateCallback, nullptr, &status);
    if (!status) {
        MGlobal::displayError("オブジェクト複製通知プラグイン: afterDuplicate コールバックの登録に失敗しました");
        return status;
    }

    MGlobal::displayInfo("オブジェクト複製通知プラグインがロードされました。: 複製後に通知します。");
    return MS::kSuccess;
}


// プラグイン終了時クリーンアップ
MStatus uninitializePlugin(MObject obj)
{
    MStatus status;
    // コールバック削除
    if (g_afterDuplicateCallback != 0) {
        MMessage::removeCallback(g_afterDuplicateCallback);
        g_afterDuplicateCallback = 0;
    }
    MFnPlugin plugin(obj);
    MGlobal::displayInfo("オブジェクト複製通知プラグインがアンロードされました。");
    return MS::kSuccess;
}
