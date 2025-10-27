# Streamlit 主菜单恢复

## 问题描述

用户发现Streamlit应用右上角的设置按钮（汉堡菜单）不见了，无法访问应用设置，包括主题切换等功能。

## 原因分析

在 `static/css/anthropic_theme.css` 文件中，有以下CSS规则隐藏了主菜单：

```css
#MainMenu {
    visibility: hidden;
}
```

这个设置最初可能是为了提供更简洁的界面，但同时也隐藏了用户访问设置的入口。

## 解决方案

### 1. 恢复主菜单显示

注释掉隐藏主菜单的CSS规则：

```css
/* 注意：不再隐藏主菜单，以便用户可以访问设置 */
/* #MainMenu {
    visibility: hidden;
} */
```

### 2. 配置文件优化

在 `.streamlit/config.toml` 中添加工具栏配置：

```toml
[client]
# 显示工具栏（包括设置按钮）
toolbarMode = "viewer"
```

## 工具栏模式说明

Streamlit 支持三种工具栏模式：

- **`viewer`**: 显示查看器模式的工具栏（推荐，显示必要的控制按钮）
- **`developer`**: 显示开发者模式的工具栏（包含更多调试工具）
- **`minimal`**: 最小化工具栏（隐藏大部分按钮）

当前设置为 `viewer` 模式，这将显示：
- ⚙️ 设置按钮（可以切换主题、调整设置）
- 🔄 重新运行按钮
- 📱 其他必要的控制按钮

## 主菜单功能

恢复主菜单后，用户可以访问：

1. **Settings** (设置)
   - 主题选择（Light/Dark/System）
   - 宽屏模式切换
   - 运行设置

2. **Print** (打印)
   - 打印当前页面

3. **Record a screencast** (录制屏幕)
   - 录制应用使用过程

4. **About** (关于)
   - 查看Streamlit版本信息

## 注意事项

### 关于主题切换

虽然恢复了设置按钮，但由于我们在配置文件中设置了 `base = "light"`，用户在设置中：
- ✅ **可以看到主题选择选项**
- ⚠️ **但主题已被锁定为亮色模式**
- ℹ️ 用户选择"Dark"或"System"时，应用仍会保持亮色

这是预期行为，因为我们的目标是强制保持亮色主题。

### 如何完全禁用主题切换

如果想要：
1. 保持亮色主题
2. 同时隐藏设置中的主题选择选项

可以考虑使用自定义主题配置，完全覆盖 `[theme]` 部分：

```toml
[theme]
primaryColor = "#D97A5E"
backgroundColor = "#F5F1E8"
secondaryBackgroundColor = "#FAFAF8"
textColor = "#2B2B2B"
font = "sans serif"
```

这样设置后，用户在设置中仍然可以看到主题选项，但切换无效。

## 相关配置

### CSS文件
- **文件**: `static/css/anthropic_theme.css`
- **修改**: 注释掉 `#MainMenu { visibility: hidden; }`

### 配置文件
- **文件**: `.streamlit/config.toml`
- **新增**: `[client]` 部分的 `toolbarMode = "viewer"`
- **保留**: `[theme]` 部分的 `base = "light"`

## 其他隐藏元素

注意，CSS文件中仍然保留了以下隐藏规则：

```css
footer {
    visibility: hidden;
}
```

这会隐藏Streamlit的底部"Made with Streamlit"标识。如果需要显示，也可以注释掉这行。

## 生效方式

修改生效需要：
1. **CSS修改**: 刷新浏览器页面即可
2. **配置文件修改**: 需要重启Streamlit应用

重启应用的方法：
```bash
# Ctrl+C 停止当前应用
# 然后重新启动
streamlit run homepage.py
```

## 测试验证

修复后，应该能看到：
1. ✅ 右上角出现 "⋮" 或 "☰" 菜单按钮
2. ✅ 点击可以打开下拉菜单
3. ✅ 菜单中包含 Settings、Print、About 等选项
4. ✅ 进入 Settings 可以看到主题选项（虽然被锁定为Light）

## 更新日期

2025-10-21

## 相关问题

- [DARK_MODE_FIX.md](DARK_MODE_FIX.md) - 暗黑模式配色修复
- [FORCE_LIGHT_MODE.md](../FORCE_LIGHT_MODE.md) - 强制亮色模式设置

