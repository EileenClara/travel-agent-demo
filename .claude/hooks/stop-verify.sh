#!/bin/bash
# Stop Hook: 交付验收检查
# 如果本轮修改了代码/配置/文档但未完成验证，阻止结束

PROJECT="/e/me/Python/Agent"
FLAGS="$PROJECT/.claude"
VERIFIED="$FLAGS/.stop_verified"
SESSION_START="$FLAGS/.session_start"

# 已通过验证 → 放行，清理标记
if [ -f "$VERIFIED" ]; then
    rm -f "$VERIFIED" "$FLAGS/.stop_requested"
    exit 0
fi

# 确保 session 基准时间存在
if [ ! -f "$SESSION_START" ]; then
    touch "$SESSION_START"
fi

# 扫描可验证类型的文件是否有修改
CHANGED=$(find "$PROJECT" -maxdepth 3 -type f \
    \( -name "*.py"    -o -name "*.js"  -o -name "*.ts"   -o \
       -name "*.json"  -o -name "*.html" -o -name "*.css"  -o \
       -name "*.md"    -o -name "*.yaml" -o -name "*.yml"  -o \
       -name "*.toml"  -o -name "*.cfg"  -o -name "*.ini"  -o \
       -name "*.sh"    -o -name "*.xml"  -o -name "*.txt"  -o \
       -name "*.env"   -o -name "*.tf"   -o -name "*.dockerfile" \) \
    -newer "$SESSION_START" 2>/dev/null | head -5)

# 无修改 → 放行
if [ -z "$CHANGED" ]; then
    exit 0
fi

# 有修改但未验证 → 输出验收清单，阻止结束
touch "$FLAGS/.stop_requested"

cat << EOF
⚠️  Stop 被阻止 — 交付验收未完成

本轮修改了以下文件（部分）：
$CHANGED

请逐项完成验证并报告结果：
1. 🧪 测试      — 运行测试套件，报告通过/失败及覆盖率
2. 🔍 Lint      — 运行 lint 工具，报告新增 warning/error
3. 📐 Typecheck — 运行类型检查，报告是否通过
4. ✅ 功能验证   — 实际运行/手动测试，确认功能正常
5. 📋 TODO 检查 — 检查是否遗留未完成的 TODO/FIXME/HACK

全部通过后，执行以下命令创建验收标记，然后再次结束：
  echo done > "$VERIFIED"
EOF

exit 0
