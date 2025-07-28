@echo off
echo ========================================
echo AGIX Fund Monitor 定时任务设置脚本
echo ========================================
echo.

REM 获取当前目录
set "PROJECT_DIR=%~dp0"
set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"

echo 项目目录: %PROJECT_DIR%
echo.

REM 创建任务名称
set "TASK_NAME=AGIX Fund Monitor 数据更新"
set "TASK_DESC=每日自动更新AGIX基金监控数据"

echo 任务名称: %TASK_NAME%
echo 任务描述: %TASK_DESC%
echo.

REM 创建schtasks命令
set "SCHTASKS_CMD=schtasks /create /tn "%TASK_NAME%" /tr "python %PROJECT_DIR%\auto_update.py --full-update" /sc daily /st 09:00 /f"

echo 创建定时任务...
echo 命令: %SCHTASKS_CMD%
echo.

REM 执行命令
%SCHTASKS_CMD%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ 定时任务创建成功！
    echo.
    echo 任务详情:
    echo - 名称: %TASK_NAME%
    echo - 执行时间: 每天上午9:00
    echo - 执行程序: python auto_update.py --full-update
    echo - 工作目录: %PROJECT_DIR%
    echo.
    echo 管理任务:
    echo - 查看任务: schtasks /query /tn "%TASK_NAME%"
    echo - 删除任务: schtasks /delete /tn "%TASK_NAME%" /f
    echo - 立即运行: schtasks /run /tn "%TASK_NAME%"
    echo.
) else (
    echo.
    echo ❌ 定时任务创建失败！
    echo 错误代码: %ERRORLEVEL%
    echo.
    echo 请尝试手动创建:
    echo 1. 打开"任务计划程序"
    echo 2. 创建基本任务
    echo 3. 设置每天运行
    echo 4. 程序: python
    echo 5. 参数: auto_update.py --full-update
    echo 6. 起始位置: %PROJECT_DIR%
    echo.
)

pause 