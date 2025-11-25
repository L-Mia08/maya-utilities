@echo off
:: 管理者権限チェック
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo 管理者権限が必要です。管理者権限が拒否されたらこのプログラムは終了します。
    powershell -Command "Start-Process '%~0' -Verb runAs"
    timeout /t 2 >nul
    exit
)

:: ここに管理者実行時の処理を書く
:: Mayaバージョンの選択
echo 使用するMayaのバージョンを1,2,3,4からを選択してください:
echo 1. Maya2022
echo 2. Maya2023
echo 3. Maya2024
echo 4. Maya2025
set /p versionChoice=番号を入力してエンターを押してください (1-4):

if "%versionChoice%"=="1" set mayaVer=2022
if "%versionChoice%"=="2" set mayaVer=2023
if "%versionChoice%"=="3" set mayaVer=2024
if "%versionChoice%"=="4" set mayaVer=2025

if "%mayaVer%"=="" (
    echo 不正な選択です。終了します。
    goto ERROR_END
)

:: 言語の選択
echo.
echo 使用する言語を1,2から選択してください:
echo 1. 英語
echo 2. 日本語
set /p langChoice=番号を入力してエンターを押してください (1-2):

if "%langChoice%"=="1" (
    set langFolder=
) else if "%langChoice%"=="2" (
    set langFolder=\ja_JP
) else (
    echo 不正な選択です。終了します。
    goto ERROR_END
)

:: フォルダー設定
set "targetFolder=%USERPROFILE%\Documents\maya\%mayaVer%%langFolder%\scripts"

:: ダウンロード先のURLと保存先のフォルダーを指定
set "url=https://github.com/phyblas/mmdpaimaya/archive/refs/heads/master.zip"
set "downloadFolder=%USERPROFILE%\Downloads"
set "zipFile=%downloadFolder%\master.zip"
set "extractFolder=%downloadFolder%\mmdpaimaya-master"

:: PowerShellを使用してファイルをダウンロード
PowerShell -Command "Invoke-WebRequest -Uri '%url%' -OutFile '%zipFile%'"

:: ダウンロードが成功したかどうかを確認
if exist "%zipFile%" (
    echo ダウンロード成功: %zipFile%
) else (
    echo ダウンロード失敗
    echo URLが変更されている可能性があります。
    echo 上記のコードのurlの欄に新しいURLに置き換えてください
    goto ERROR_END
)

:: ダウンロードしたZIPファイルを展開
PowerShell -Command "Expand-Archive -Path '%zipFile%' -DestinationPath '%downloadFolder%' -Force"

:: 展開が成功したかどうかを確認
if exist "%extractFolder%" (
    echo 展開成功: %extractFolder%
) else (
    echo 展開失敗
    goto ERROR_END
)

:: 展開後の "mmdpaimaya-master" フォルダー内の "mmdpaimaya" フォルダーを確認
set "mmdpaimayaFolder=%extractFolder%\mmdpaimaya"

:: "mmdpaimaya"フォルダーをユーザーのDocuments\maya\[バージョン][言語]\scriptsフォルダーに移動
if exist "%mmdpaimayaFolder%" (
    echo "mmdpaimaya"フォルダーを移動中...
    if exist "%targetFolder%\mmdpaimaya" (
        echo 既存のmmdpaimayaフォルダーを削除します
        rmdir /S /Q "%targetFolder%\mmdpaimaya"
    )

    move /Y "%mmdpaimayaFolder%" "%targetFolder%" >nul 2>&1

    if errorlevel 1 (
        echo フォルダー移動中に警告が発生しましたが処理は完了しています
    ) else (
        echo フォルダーを %targetFolder% に正常に移動しました
    )

    :: 移動後、ダウンロードフォルダに残ったファイルを削除
    echo ダウンロードフォルダーの不要ファイルを削除中...

    :: ZIPファイル削除
    if exist "%zipFile%" (
        del /F /Q "%zipFile%"
        if exist "%zipFile%" (
            echo ZIPファイルの削除に失敗しました: %zipFile%
        ) else (
            echo ZIPファイルを削除しました: %zipFile%
        )
    )

    :: 展開フォルダ削除
    if exist "%extractFolder%" (
        rmdir /S /Q "%extractFolder%"
        if exist "%extractFolder%" (
            echo 展開フォルダの削除に失敗しました: %extractFolder%
        ) else (
            echo 展開フォルダを削除しました: %extractFolder%
        )
    )

    echo 不要ファイルの削除が完了しました

    :: Mayaのバージョンを指定 (移動後に実行)
    cd "C:\Program Files\Autodesk\Maya%mayaVer%\bin"

    :: pipアップデート
    echo pipアップデートを開始します
    mayapy -m pip install --upgrade pip

    :: pykakasiをインストール
    echo pykakasiをインストールを開始します
    mayapy -m pip install pykakasi

) else (
    echo "mmdpaimaya"フォルダーが見つかりません
    echo エラーが発生している可能性があります
    goto ERROR_END
)

:: 完了メッセージ
echo mmdpaimayaのダウンロードとpykakasiのインストールが完了しました

:: pyコードをクリップボードへコピー
powershell -command "Set-Clipboard \"import mmdpaimaya`nmmdpaimaya.yamikuma()\""
echo mmdpaimayaのpyコードをクリップボードへコピーしました。
echo mayaのスクリプトエディタへ貼り付けできます。
pause
exit /b

:ERROR_END
echo.
echo ================================
echo エラーが発生したため処理を停止しました
echo 内容を確認してください
echo ================================
pause
exit /b

