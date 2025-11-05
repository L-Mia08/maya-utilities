#include <maya/MFnPlugin.h>
#include <maya/MGlobal.h>
#include <maya/MModelMessage.h>
#include <maya/MMessage.h>
#include <maya/MSelectionList.h>
#include <maya/MItSelectionList.h>
#include <maya/MDagPath.h>
#include <maya/MFnDagNode.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MEventMessage.h>
#include <maya/MStatus.h>
#include <maya/MString.h>
#include <maya/MPxCommand.h>

#include <sstream>
#include <vector>

static MCallbackId g_afterDuplicateCallback = 0;
static MCallbackId g_sceneOpenedCallback = 0;
static MCallbackId g_newSceneOpenedCallback = 0;
static bool g_ready = false; // シーン準備完了フラグ


// シーンロードまたは新規作成完了時に呼ばれる
void setReady(void* /*clientData*/)
{
    g_ready = true;
    MGlobal::displayInfo("複製通知プラグイン: シーン準備完了。通知を有効化しました。");
}

// 選択から名前リストを取得
static std::vector<std::string> getSelectionNames()
{
    std::vector<std::string> names;
    MSelectionList sel;
    if (MGlobal::getActiveSelectionList(sel) != MS::kSuccess)
        return names;

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
    // シーン準備完了前は無視（起動直後や内部複製を回避）
    if (!g_ready)
        return;

    // 現在のフォーカスパネルを取得
    MString panel;
    MGlobal::executeCommand("getPanel -wf", panel);

    // Hypershade での操作なら無視
    if (panel.indexW("hyperShadePanel") != -1)
        return;

    std::vector<std::string> names = getSelectionNames();
    MString pythonCmd;

    // デフォルト系オブジェクトを除外
    bool containsDefault = false;
    for (const auto& name : names) {
        if (name == "defaultObjectSet" ||
            name == "defaultLightSet" ||
            name == "defaultHideFaceDataSet" ||
            name.find("default") != std::string::npos) {
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
        // 0件 → 内部複製などの場合は何も表示しない
        return;
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
        std::stringstream ss;
        ss << "import maya.cmds as cmds\n"
            << "cmds.inViewMessage(amg='<hl>" << count
            << " つのオブジェクトが複製されました</hl>', "
            << "pos=\"topCenter\", fade=True, fadeStayTime=2000, alpha=.9)";
        pythonCmd = ss.str().c_str();
    }

    if (!pythonCmd.isEmpty()) {
        MGlobal::executePythonCommand(pythonCmd);
    }
}

//--------------------------------------------
// MELコマンドクラス: 複製通知を手動で有効化
//--------------------------------------------
class EnableDuplicateNotifyCmd : public MPxCommand
{
public:
    EnableDuplicateNotifyCmd() {}
    virtual MStatus doIt(const MArgList&) override
    {
        g_ready = true;
        MGlobal::displayInfo("複製通知プラグイン: 手動で通知を有効化しました。");
        return MS::kSuccess;
    }

    static void* creator() { return new EnableDuplicateNotifyCmd(); }
};

//--------------------------------------------
// initializePlugin に MELコマンド登録を追加
//--------------------------------------------
MStatus initializePlugin(MObject obj)
{
    MStatus status;
    MFnPlugin plugin(obj, "Naruse,GPT-5", "2025.11.05 v1.3", "2025", &status);
    if (!status) {
        MGlobal::displayError("オブジェクト複製通知プラグイン: MFnPlugin の初期化に失敗しました");
        return status;
    }

    // MELコマンド登録
    status = plugin.registerCommand("enableDuplicateNotify", EnableDuplicateNotifyCmd::creator);
    if (!status) {
        MGlobal::displayError("enableDuplicateNotify コマンド登録に失敗しました");
        return status;
    }

    // --- 以下は元の処理 ---
    if (g_afterDuplicateCallback != 0) {
        MMessage::removeCallback(g_afterDuplicateCallback);
        g_afterDuplicateCallback = 0;
    }

    g_afterDuplicateCallback = MModelMessage::addAfterDuplicateCallback(afterDuplicateCallback, nullptr, &status);
    if (!status) {
        MGlobal::displayError("afterDuplicate コールバックの登録に失敗しました");
        return status;
    }

    g_sceneOpenedCallback = MEventMessage::addEventCallback("SceneOpened", setReady);
    g_newSceneOpenedCallback = MEventMessage::addEventCallback("NewSceneOpened", setReady);

    MGlobal::displayInfo(
        "オブジェクト複製通知プラグインがロードされました。\n"
        "シーンロード後に通知が有効になります。\n"
        "通知が表示されない場合は [enableDuplicateNotify;] を MEL で実行してください。"
    );

    return MS::kSuccess;
}

//--------------------------------------------
// uninitializePlugin に MELコマンド解除を追加
//--------------------------------------------
MStatus uninitializePlugin(MObject obj)
{
    MFnPlugin plugin(obj);
    plugin.deregisterCommand("enableDuplicateNotify");

    if (g_afterDuplicateCallback != 0) {
        MMessage::removeCallback(g_afterDuplicateCallback);
        g_afterDuplicateCallback = 0;
    }
    if (g_sceneOpenedCallback != 0) {
        MMessage::removeCallback(g_sceneOpenedCallback);
        g_sceneOpenedCallback = 0;
    }
    if (g_newSceneOpenedCallback != 0) {
        MMessage::removeCallback(g_newSceneOpenedCallback);
        g_newSceneOpenedCallback = 0;
    }

    MGlobal::displayInfo("オブジェクト複製通知プラグインがアンロードされました。");
    return MS::kSuccess;
}
