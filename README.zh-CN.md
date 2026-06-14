[English](README.md) | 中文

# 插件

本仓库包含一系列 Codex 插件示例。

每个插件位于 `plugins/<name>/` 目录下，包含一个必需的
`.codex-plugin/plugin.json` 清单文件，以及可选的附属组件，如
`skills/`、`.app.json`、`.mcp.json`、插件级 `agents/`、`commands/`、
`hooks.json`、`assets/` 等。

精选的优秀示例包括：

- `plugins/figma` — `use_figma`、Code to Canvas、Code Connect 和设计系统规则
- `plugins/notion` — 规划、调研、会议和知识管理
- `plugins/build-ios-apps` — SwiftUI 实现、重构、性能优化和调试
- `plugins/build-macos-apps` — macOS SwiftUI/AppKit 工作流、构建/运行/调试循环和打包指导
- `plugins/build-web-apps` — 部署、UI、支付和数据库工作流
- `plugins/expo` — Expo 和 React Native 应用、SDK 升级、EAS 工作流和 Codex Run 操作
- `plugins/netlify`、`plugins/remotion` 和 `plugins/google-slides` — 其他公开的 skill 和 MCP 支持的插件包

## Claude Code 插件市场

本仓库也可作为 [Claude Code](https://claude.ai/code) 插件市场使用。

```bash
# 添加市场（一次性操作，在 Claude Code 中执行）
/plugin marketplace add yangtzech/openai-plugins

# 安装任意插件
/plugin install figma
/plugin install notion
/plugin install github
```

也可以使用命令行：

```bash
claude plugin marketplace add yangtzech/openai-plugins
claude plugin install figma@openai-plugins
```

完整插件列表和更多详情请见 [CLAUDE-CODE.zh-CN.md](CLAUDE-CODE.zh-CN.md)。
