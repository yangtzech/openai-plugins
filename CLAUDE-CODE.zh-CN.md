# Claude Code 插件市场

本仓库也可作为 [Claude Code](https://claude.ai/code) 插件市场使用。

## 快速开始

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

## 可用插件

本仓库包含 **174 个插件**，涵盖以下分类：

- **开发工具**: github, circleci, cloudflare, vercel, netlify, render, supabase, neon-postgres 等
- **生产力**: notion, asana, linear, clickup, monday-com, teamwork-com 等
- **通讯**: slack, teams, zoom, intercom, help-scout 等
- **金融与 CRM**: stripe, hubspot, pipedrive, salesforce, quickbooks 等
- **设计与媒体**: figma, canva, picsart, shutterstock, remotion 等
- **数据与分析**: datadog, mixpanel, posthog, amplitude 等
- **AI 与机器学习**: hugging-face, nvidia, openai-developers 等
- **更多...**

完整列表请参见 [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)。

## 脚本

- `scripts/generate-marketplace-json.py` - 重新生成 marketplace.json 清单
- `scripts/codex2claude.py` - 将 Codex 插件适配为 Claude Code 插件
