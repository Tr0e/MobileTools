@echo off
setlocal enabledelayedexpansion

REM 获取当前的 TopActivity 的第二行输出
set count=0
for /f "tokens=*" %%i in ('adb shell dumpsys activity top ^| findstr "ACTIVITY"') do (
    set /a count+=1
    if !count! equ 2 (
        set output=%%i
        goto :process
    )
)

:process
REM 提取 TopActivity 的全路径
for /f "tokens=2 delims= " %%a in ("%output%") do (
    set fullActivity=%%a
)

REM 提取包名（提取 / 之前的部分）
for /f "tokens=1 delims=/" %%b in ("%fullActivity%") do (
    set packageName=%%b
)

REM 查询 APK 安装路径，只获取第一行
for /f "tokens=*" %%i in ('adb shell pm path %packageName%') do (
    set apkPath=%%i
    goto :pull
)

:pull
REM 提取实际的 APK 路径
set apkPath=%apkPath:package=%
echo %apkPath:~2%
set apkPath=%apkPath:~2%


REM 拉取 APK 到本地
adb pull %apkPath% %packageName%.apk

echo APK 已成功拉取到当前目录
pause