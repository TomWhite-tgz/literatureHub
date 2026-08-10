# literatureHub

自动化科研（agentic literature search / deep research）方向的文献调研档案分享站。

- **线上地址**：https://tomwhite-tgz.github.io/literatureHub/
- **站点内容**：`site/` 目录（入口 `site/index.html`）。push 到 `main` 后 GitHub Actions 自动重新部署（约 1 分钟），无需手动操作。
- **包含**：精读/审计 HTML 页面、配图、笔记、论文 PDF。
- **不包含**：源码仓库 clone、数据集、模型权重（原始档案 107 GB）——相应链接指向官方仓库或 `site/_未包含的内容.html`。

## 更新方式

1. 内容源头在维护者本地的 Literature 档案，通过 Claude Code 的 `publish-literature-hub` skill 同步发布（收录规则：从 `index.html` 可达才发布）。
2. 也可以直接修改 `site/` 下的页面提交 PR，流程见 [CONTRIBUTING.md](CONTRIBUTING.md)。
3. 新增或修改 HTML 后跑 `python3 scripts/build_search_index.py`，更新首页使用的静态全文搜索索引。
4. 发布前跑 `python3 scripts/add_noindex.py`，保证每个页面带 noindex meta（站点不进搜索引擎）。
