#--------------------------------------------------------------------------
# ScriptName: Random animation generation
# Author: Naruse,GPT-5
# Contents   :選択したオブジェクトをアニメーションレイヤーに追加してランダムアニメーションを生成する
# CreatedDate: 2025年12月15日
# LastUpdate: 2025年12月16日
# Version: 0.2
#
# 《License》
# Copyright (c) 2025 Naruse
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php
#--------------------------------------------------------------------------


import maya.cmds as cmds
import random

WINDOW_NAME = "RandomAnimationGenerationUI"

# 指定フレームを Maya のタイムライン範囲内に収める。
def clamp_to_timeline(frame):
    min_f = int(cmds.playbackOptions(q=True, min=True)) # 最小フレーム未満 → 最小フレーム
    max_f = int(cmds.playbackOptions(q=True, max=True)) # 最大フレーム超過 → 最大フレーム
    return max(min_f, min(frame, max_f))

# =============================================
# UI のチェック状態(flags)を元に、実際にキーを打てるアトリビュートのみを収集する。
# 存在しない属性は除外
# ロックされている属性は除外
def collect_attrs(obj, flags):
    result = []
    for attr, enabled in flags.items():
        if not enabled:
            continue
        full = f"{obj}.{attr}"
        if cmds.objExists(full) and not cmds.getAttr(full, lock=True):
            result.append(full)
    return result

# =============================================
# 線形補間関数（Linear Interpolation）
# t=0 → a
# t=1 → b
def lerp(a, b, t):
    return a + (b - a) * t

# =============================================
# 選択オブジェクトをアニメーションレイヤーに追加し、
# ランダム値＋任意フェード＋可変フレーム間隔でキーを生成するメイン処理
def add_selected_to_anim_layer_with_keys(
    layer_name, start_frame, end_frame,
    flags,
    random_value_min,
    random_value_max,
    fade_enabled,
    fade_start_frame,
    fade_end_value,
    frame_step_input,
    random_step_enabled,
    random_step_limit,
    disable_random_step_limit
):

    # Transform ノードのみ対象にする
    sel = cmds.ls(sl=True, type="transform")
    if not sel:
        cmds.warning("オブジェクトが選択されていません。")
        return

    # どのチャンネルにもチェックが入っていない場合は中断
    if not any(flags.values()):
        cmds.warning("キーを生成する要素が選択されていません。")
        return

    # 開始・終了フレームを確定
    start = int(start_frame)
    end = clamp_to_timeline(int(end_frame))

    if start > end:
        cmds.warning("開始フレームが終了フレームを超えています。")
        return

    # ランダム最大値（float前提）

    rand_min = float(random_value_min)
    rand_max = float(random_value_max)

    # 入力逆転の安全処理
    if rand_min > rand_max:
        rand_min, rand_max = rand_max, rand_min

    # フレームステップは「最低 1 フレーム進む」ようにする
    step_input = max(0, int(frame_step_input))
    step = step_input + 1

    # フェード設定が有効な場合の入力チェック
    if fade_enabled:
        fade_start = int(fade_start_frame)
        fade_end = float(fade_end_value)

        if fade_start is None or fade_end is None:
            cmds.warning("減衰の入力が空白、または不正です。処理を中断します。")
            return

        if fade_start > end:
            cmds.warning("減衰の開始フレームが最終フレームを超えています。処理を中断します。")
            return

        fade_start = int(fade_start)

    # アニメーションレイヤーが存在しなければ新規作成
    if not cmds.objExists(layer_name):
        layer_name = cmds.animLayer(layer_name)

    # 実際にキーを打つアトリビュート一覧を構築
    attrs_to_add = []
    for obj in sel:
        attrs_to_add.extend(collect_attrs(obj, flags))

    if not attrs_to_add:
        cmds.warning("有効なアトリビュートがありません。")
        return

    # Undo を 1 ステップにまとめる
    cmds.undoInfo(openChunk=True)
    try:
        # 対象アトリビュートをアニメーションレイヤーに登録
        cmds.animLayer(layer_name, edit=True, attribute=attrs_to_add)

        current_frame = start
        current_step = step

        # ランダムステップの上限設定
        # 無効時は None にして分岐を単純化
        if not disable_random_step_limit:
            step_limit = max(1, int(random_step_limit))
        else:
            step_limit = None  # 上限なし

        # フレーム生成ループ
        while current_frame <= end:
            frame = current_frame
            cmds.currentTime(frame, edit=True)

            # 現在フレームで使用するランダム最大値
            current_max = rand_max

            # フェード有効時は、開始フレーム以降で値を補間
            if fade_enabled and frame >= fade_start:
                denom = max(1, end - fade_start)
                t = (frame - fade_start) / float(denom)
                t = max(0.0, min(1.0, t))
                current_max = lerp(rand_max, fade_end, t)

            # 各アトリビュートにランダム値を設定
            for attr in attrs_to_add:

                # 元となるランダム値を生成
                base_value = random.uniform(rand_min, rand_max)

                if fade_enabled and frame >= fade_start:
                    denom = max(1, end - fade_start)
                    t = (frame - fade_start) / float(denom)
                    t = max(0.0, min(1.0, t))

                    # ease-out フェード
                    t = 1.0 - pow(1.0 - t, 2)
                    value = lerp(base_value, fade_end, t)

                else:
                    value = base_value

                cmds.setAttr(attr, value)

            # 現在フレームにキーを作成
            cmds.setKeyframe(attrs_to_add, animLayer=layer_name)

            # ---- フレーム間隔のランダム成長処理 ----
            if random_step_enabled:
                # 現在のステップ幅を基準にランダム増加
                random_add = random.randint(0, current_step)
                current_step += random_add

                # 上限がある場合はクランプ
                if step_limit is not None:
                    current_step = min(current_step, step_limit)

            # 次のフレームへ進める
            current_frame += current_step

    finally:
        # Undo チャンクを必ず閉じる
        cmds.undoInfo(closeChunk=True)

def sync_all(parent, children):
    # 「ALL」チェックボックス用。
    # 親の状態を子チェックボックス全てに同期させる。
    state = cmds.checkBox(parent, q=True, value=True)
    for cb in children:
        cmds.checkBox(cb, e=True, value=state)


# =============================================
# ここからUI
# =============================================

def build_ui():
    if cmds.window(WINDOW_NAME, exists=True):
        cmds.deleteUI(WINDOW_NAME)

    ui = {}

    cmds.window(WINDOW_NAME, title="Random animation generation", widthHeight=(330, 860))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=6)

    # -------------------------------------------------
    # アニメーションレイヤー
    # -------------------------------------------------
    cmds.text(label="アニメーションレイヤー名")
    ui["layer_field"] = cmds.textField(text="AnimLayer_1")

    cmds.separator(style="in")

    cmds.rowLayout(numberOfColumns=4, adjustableColumn=2)
    cmds.text(label="開始")
    ui["start_field"] = cmds.intField(value=0, minValue=0)
    cmds.text(label="終了")
    ui["end_field"] = cmds.intField(value=0)
    cmds.setParent("..")

    cmds.separator(style="in")

    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
    cmds.text(label="生成フレーム間隔")
    ui["step_field"] = cmds.intField(value=0, minValue=0)
    cmds.setParent("..")

    cmds.separator(style="in")

    # -------------------------------------------------
    # ランダムステップ設定
    # -------------------------------------------------
    ui["random_step_cb"] = cmds.checkBox(
        label="生成フレーム間隔をランダムに（+方向）",
        value=False
    )

    ui["disable_limit_cb"] = cmds.checkBox(
        label="ランダム上限を無効にする",
        value=False
    )

    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
    cmds.text(label="ランダム上限")
    ui["random_step_limit_field"] = cmds.intField(
        value=10,
        minValue=1
    )
    cmds.setParent("..")

    # ---- UI 状態制御 ----
    def update_random_ui(*_):
        random_enabled = cmds.checkBox(ui["random_step_cb"], q=True, value=True)
        limit_disabled = cmds.checkBox(ui["disable_limit_cb"], q=True, value=True)

        # ランダム無効時はすべて無効
        cmds.checkBox(ui["disable_limit_cb"], e=True, enable=random_enabled)

        cmds.intField(
            ui["random_step_limit_field"],
            e=True,
            enable=(random_enabled and not limit_disabled)
        )

    cmds.checkBox(ui["random_step_cb"], e=True, cc=update_random_ui)
    cmds.checkBox(ui["disable_limit_cb"], e=True, cc=update_random_ui)

    cmds.separator(style="in")
    cmds.text(label="キーを生成する要素")

    # -------------------------------------------------
    # Transform チェックボックス
    # -------------------------------------------------
    checkboxes = {}

    def axis_block(title, prefix):
        cmds.frameLayout(label=title, collapsable=False)
        cmds.rowLayout(numberOfColumns=4)
        all_cb = cmds.checkBox(label="ALL")
        x = cmds.checkBox(label="X")
        y = cmds.checkBox(label="Y")
        z = cmds.checkBox(label="Z")
        cmds.setParent("..")

        cmds.checkBox(all_cb, e=True, cc=lambda *_: sync_all(all_cb, [x, y, z]))

        checkboxes[f"{prefix}X"] = x
        checkboxes[f"{prefix}Y"] = y
        checkboxes[f"{prefix}Z"] = z
        cmds.setParent("..")

    axis_block("Translate", "translate")
    axis_block("Rotate", "rotate")
    axis_block("Scale", "scale")

    cmds.separator(style="in")

    # -------------------------------------------------
    # ランダム Value
    # -------------------------------------------------
    cmds.text(label="ランダム最大 Value")
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
    cmds.text(label="Min")
    ui["random_value_min_field"] = cmds.floatField(value=0.0)
    cmds.setParent("..")
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
    cmds.text(label="Max")
    ui["random_value_max_field"] = cmds.floatField(value=1.0)
    cmds.setParent("..")
    cmds.separator(style="in")



    # -------------------------------------------------
    # フェード
    # -------------------------------------------------

    ui["fade_cb"] = cmds.checkBox(label="減衰（フェード）を使用", value=False)
    cmds.rowLayout(numberOfColumns=4, adjustableColumn=2)
    cmds.text(label="開始フレーム")
    ui["fade_start_field"] = cmds.intField(value=0, minValue=0)
    cmds.text(label="最終Value")
    ui["fade_end_field"] = cmds.floatField(value=0.0)
    cmds.setParent("..")

    def update_fade_ui(*_):
        fade_enabled = cmds.checkBox(ui["fade_cb"], q=True, value=True)

        cmds.intField(
            ui["fade_start_field"],
            e=True,
            enable=fade_enabled
        )
        cmds.floatField(
            ui["fade_end_field"],
            e=True,
            enable=fade_enabled
        )

    cmds.checkBox(ui["fade_cb"], e=True, cc=update_fade_ui)

    cmds.separator(style="in")

    # -------------------------------------------------
    # 実行ボタン
    # -------------------------------------------------

    # *_field → UI部品
    # *_cb → checkBox
    # *_btn → button
    cmds.button(
        label="選択オブジェクトを追加してキー生成",
        height=40,
        command=lambda *_: add_selected_to_anim_layer_with_keys(
            cmds.textField(ui["layer_field"], q=True, text=True),
            cmds.intField(ui["start_field"], q=True, value=True),
            cmds.intField(ui["end_field"], q=True, value=True),
            {k: cmds.checkBox(v, q=True, value=True) for k, v in checkboxes.items()},
            cmds.floatField(ui["random_value_min_field"], q=True, value=True),
            cmds.floatField(ui["random_value_max_field"], q=True, value=True),
            cmds.checkBox(ui["fade_cb"], q=True, value=True),
            cmds.intField(ui["fade_start_field"], q=True, value=True),
            cmds.floatField(ui["fade_end_field"], q=True, value=True),
            cmds.intField(ui["step_field"], q=True, value=True),
            cmds.checkBox(ui["random_step_cb"], q=True, value=True),
            cmds.intField(ui["random_step_limit_field"], q=True, value=True),
            cmds.checkBox(ui["disable_limit_cb"], q=True, value=True),

        )
    )

    # 初期状態同期
    update_random_ui()
    update_fade_ui()

    cmds.showWindow(WINDOW_NAME)

build_ui()