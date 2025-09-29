#include "pch.h"
#include <maya/MFnPlugin.h>
#include <maya/MPxCommand.h>
#include <maya/MGlobal.h>
#include <maya/MSelectionList.h>
#include <maya/MItSelectionList.h>
#include <maya/MFnMesh.h>
#include <maya/MDagPath.h>
#include <maya/MFnSingleIndexedComponent.h>
#include <maya/MStringArray.h>

// ========== オブジェクト数を表示 ==========
class SelInfoObjectCmd : public MPxCommand
{
public:
    virtual MStatus doIt(const MArgList& args) override
    {
        MSelectionList sel;
        MGlobal::getActiveSelectionList(sel);

        unsigned int count = sel.length();
        MGlobal::displayInfo(MString("選択オブジェクト数: ") + (int)count);

        return MStatus::kSuccess;
    }
    static void* creator() { return new SelInfoObjectCmd; }
};

// ========== 選択頂点数を表示 ==========
class SelInfoVertexCmd : public MPxCommand
{
public:
    virtual MStatus doIt(const MArgList& args) override
    {
        MSelectionList sel;
        MGlobal::getActiveSelectionList(sel);

        // コンポーネント選択のみを走査
        MItSelectionList iter(sel, MFn::kMeshVertComponent);

        if (iter.isDone())
        {
            MGlobal::displayError("コンポーネントが選択されていません。コンポーネントモードで頂点を選択してください。");
            return MStatus::kFailure;
        }

        unsigned int totalVertexCount = 0;
        for (; !iter.isDone(); iter.next())
        {
            MDagPath dagPath;
            MObject component;
            iter.getDagPath(dagPath, component);

            MFnSingleIndexedComponent compFn(component);
            totalVertexCount += compFn.elementCount();
        }

        MGlobal::displayInfo(MString("選択頂点数: ") + (int)totalVertexCount);

        return MStatus::kSuccess;
    }
    static void* creator() { return new SelInfoVertexCmd; }
};

// ========== フェース数を表示 ==========
class SelInfoFaceCmd : public MPxCommand
{
public:
    MStatus doIt(const MArgList& args) override
    {
        MSelectionList sel;
        MGlobal::getActiveSelectionList(sel);

        MItSelectionList iter(sel, MFn::kMeshPolygonComponent);
        if (iter.isDone())
        {
            MGlobal::displayError("コンポーネントが選択されていません。コンポーネントモードでフェースを選択してください。");
            return MStatus::kFailure;
        }

        unsigned int faceCount = 0;
        for (; !iter.isDone(); iter.next())
        {
            MDagPath dagPath;
            MObject component;
            iter.getDagPath(dagPath, component);

            MFnSingleIndexedComponent compFn(component);
            faceCount += compFn.elementCount();
        }

        MGlobal::displayInfo(MString("選択フェース数: ") + (int)faceCount);
        return MStatus::kSuccess;
    }
    static void* creator() { return new SelInfoFaceCmd; }
};

// ========== エッジ数を表示 ==========
class SelInfoEdgeCmd : public MPxCommand
{
public:
    MStatus doIt(const MArgList& args) override
    {
        MSelectionList sel;
        MGlobal::getActiveSelectionList(sel);

        MItSelectionList iter(sel, MFn::kMeshEdgeComponent);
        if (iter.isDone())
        {
            MGlobal::displayError("コンポーネントが選択されていません。コンポーネントモードでエッジを選択してください。");
            return MStatus::kFailure;
        }

        unsigned int edgeCount = 0;
        for (; !iter.isDone(); iter.next())
        {
            MDagPath dagPath;
            MObject component;
            iter.getDagPath(dagPath, component);

            MFnSingleIndexedComponent compFn(component);
            edgeCount += compFn.elementCount();
        }

        MGlobal::displayInfo(MString("選択エッジ数: ") + (int)edgeCount);
        return MStatus::kSuccess;
    }
    static void* creator() { return new SelInfoEdgeCmd; }
};

// ========== GUIコマンド ==========
class SelInfoUICmd : public MPxCommand
{
public:
    virtual MStatus doIt(const MArgList& args) override
    {
        MGlobal::executeCommand(
            "if (`window -exists SelInfoWin`) deleteUI SelInfoWin;"
            "window -title \"Selection Info\" -widthHeight 200 150 SelInfoWin;"
            "columnLayout -adjustableColumn true;"
            "button -label \"選択オブジェクト数を表示\" -command \"selInfoObject\";"
            "button -label \"選択頂点数を表示\" -command \"selInfoVertex\";"
            "button -label \"選択フェース数を表示\" -command \"selInfoFace\";"
            "button -label \"選択エッジ数を表示\" -command \"selInfoEdge\";"
            "showWindow SelInfoWin;"
        );

        return MStatus::kSuccess;
    }
    static void* creator() { return new SelInfoUICmd; }
};

// ========== プラグイン登録 ==========
MStatus initializePlugin(MObject obj)
{
    MFnPlugin plugin(obj, "Naruse.GPT-5", "2025.09.07 v1.1", "2025");

    MStatus status = plugin.registerCommand("selInfoObject", SelInfoObjectCmd::creator);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = plugin.registerCommand("selInfoVertex", SelInfoVertexCmd::creator);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = plugin.registerCommand("selInfoFace", SelInfoFaceCmd::creator);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = plugin.registerCommand("selInfoEdge", SelInfoEdgeCmd::creator);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = plugin.registerCommand("selInfoUI", SelInfoUICmd::creator);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    MGlobal::displayInfo("SelectionInfoPluginがロードされました。melコマンド[selInfoUI]でGUIを表示します。");
    return MStatus::kSuccess;
}

// ========== プラグイン解除 ==========
MStatus uninitializePlugin(MObject obj)
{
    MFnPlugin plugin(obj);

    MStatus status = plugin.deregisterCommand("selInfoObject");
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = plugin.deregisterCommand("selInfoVertex");
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = plugin.deregisterCommand("selInfoFace");
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = plugin.deregisterCommand("selInfoEdge");
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = plugin.deregisterCommand("selInfoUI");
    CHECK_MSTATUS_AND_RETURN_IT(status);

    MGlobal::displayInfo("SelectionInfoPluginがアンロードされました。");
    return MStatus::kSuccess;
}