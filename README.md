# literatureHub

自动化科研、文献搜索、文献问答与研究 Agent 的共享调研档案。

## 在线浏览

发布完成后访问：

<https://TomWhite-tgz.github.io/literatureHub/>

站点页面包含 `noindex` 声明，供获得链接的协作者浏览，不主动进入正规搜索引擎索引。仓库本身是公开的，仓库内容仍可被 GitHub 用户查看。

## 本地浏览

直接用浏览器打开：

```text
Literature_文献调研档案_2026-08-03/index.html
```

## 协作

请从新分支提交修改，并通过 Pull Request 合并。详细规范见 [CONTRIBUTING.md](CONTRIBUTING.md)。

新增或更新 HTML 后运行：

```bash
python3 scripts/add_noindex.py
```

推送到 `main` 后，GitHub Actions 会自动发布文献站点。

