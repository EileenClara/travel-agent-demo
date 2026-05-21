#!/bin/bash
# PostToolUse Hook: 代码修改后提醒 Git 推送
# 触发条件：Edit 或 Write 工具修改了代码文件

TOOL_NAME="${CLAUDE_TOOL_NAME:-}"
FILE_PATH="${CLAUDE_TOOL_INPUT_FILE_PATH:-}"
PROJECT_DIR="/e/me/Python/Agent"
FLAG_FILE="$PROJECT_DIR/.claude/.code_modified"

# 只关心 Edit / Write 工具
case "$TOOL_NAME" in
    Edit|Write) ;;
    *) exit 0 ;;
esac

# 只关心代码文件
case "$FILE_PATH" in
    *.html|*.py|*.js|*.ts|*.css|*.json|*.yaml|*.yml|*.md|*.sh|*.txt|*.toml|*.cfg)
        ;;
    *) exit 0 ;;
esac

# 设置修改标记
touch "$FLAG_FILE"

# 记录修改信息
echo "[$TOOL_NAME] $FILE_PATH" >> "$FLAG_FILE"
