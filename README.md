# Clissa Skills

我自己日常使用的一些 AI Skills 合集，偏学术检索、论文阅读、资料整理、存储分析和技术概念解释。

每个目录都是一个可独立安装的 Skill，核心入口是对应目录下的 `SKILL.md`。

## 目录

| Skill | 一句话 |
| --- | --- |
| `explain-new-concepts` | 用中文快速解释陌生技术概念，可选择篇幅、深度、资料检索和纵横分析。 |
| `storage-analyzer` | 扫描 macOS / Windows 存储占用，生成分级清理建议和交互式 HTML 报告。 |
| `obzetero-paper-reader` | 从 Zotero 读取待阅读论文，生成中文精读笔记并同步到 Obsidian。 |
| `merge-md-review-pdf` | 将 Markdown / Obsidian 复习资料合并成带目录、公式和样式校验的 PDF。 |
| `cnki-search` | 在 CNKI 按关键词搜索论文并返回结构化结果。 |
| `cnki-advanced-search` | 在 CNKI 使用作者、标题、期刊、年份、来源类别等条件做高级检索。 |
| `cnki-paper-detail` | 从 CNKI 论文页提取题名、作者、单位、摘要、关键词、基金等完整信息。 |
| `cnki-download` | 从 CNKI 下载指定论文 PDF / CAJ，需要已登录并有下载权限。 |
| `cnki-export` | 从 CNKI 导出论文引用，保存 RIS 或推送到 Zotero。 |
| `cnki-journal-search` | 按名称、ISSN、CN 或主办方搜索 CNKI 期刊。 |
| `cnki-journal-index` | 查询 CNKI 期刊收录状态、核心库、影响因子和评价信息。 |
| `cnki-journal-toc` | 浏览 CNKI 期刊某年某期目录，并可下载原版目录页。 |
| `cnki-navigate-pages` | 控制 CNKI 搜索结果翻页和排序。 |
| `cnki-parse-results` | 解析当前 CNKI 搜索结果页，提取结构化论文列表。 |
| `gs-search` | 在 Google Scholar 按关键词搜索论文。 |
| `gs-advanced-search` | 构造 Google Scholar 高级搜索，支持作者、期刊、年份、精确短语等过滤。 |
| `gs-cited-by` | 查找引用某篇 Google Scholar 论文的后续论文。 |
| `gs-fulltext` | 获取 Google Scholar 论文的 PDF、DOI、出版社和全文访问链接。 |
| `gs-export` | 从 Google Scholar 导出 BibTeX，并推送到 Zotero。 |
| `gs-navigate-pages` | 控制 Google Scholar 搜索结果翻页。 |

## 安装方式

在支持 `SKILL.md` 的 Agent 中，可以让 Agent 安装单个目录：

```text
帮我安装这个 skill：https://github.com/Lynxxxxlee/clissa-skills/tree/main/explain-new-concepts
```

也可以手动复制某个 skill 目录到本地 Skills 目录，例如：

```bash
cp -R explain-new-concepts ~/.codex/skills/
```

## Skills

### `explain-new-concepts`

解释你没听过的新技术名词、工程概念、框架、论文术语或协议。默认打开本地选择页，让你选择篇幅、深度重点、是否查资料，以及是否启用纵横分析法。

触发示例：

```text
什么是 LLVM IR
解释一下编译器优化 pass
这个新名词我没听过：speculative decoding
```

### `storage-analyzer`

只读扫描磁盘占用，找出空间大户，并把清理对象分成可自动清理、需要人工判断、谨慎清理等层级。报告使用本地 HTML 呈现。

触发示例：

```text
帮我看看存储
电脑空间不够了
C 盘满了
```

### `obzetero-paper-reader`

把 Zotero 中标记为待阅读的论文转成 Obsidian 阅读系统：提取 PDF、生成中文精读笔记、维护阅读状态和索引。

触发示例：

```text
把 Zotero 里待阅读的论文精读一下
同步 Zotero 和 Obsidian 的阅读状态
生成 LLM collection 的论文索引
```

### `merge-md-review-pdf`

把课程复习 Markdown、Obsidian 笔记和案例材料合并成一份排版稳定的 PDF，支持公式、表格、callout、高亮和目录。

触发示例：

```text
把这个复习目录合成 PDF
合并这些 Obsidian 复习笔记，保留公式和表格
```

### CNKI Skills

这一组 skills 用于 CNKI 检索、详情解析、期刊查询、导出和下载。它们通常依赖浏览器中已登录的 CNKI 状态。

包含：

- `cnki-search`
- `cnki-advanced-search`
- `cnki-paper-detail`
- `cnki-download`
- `cnki-export`
- `cnki-journal-search`
- `cnki-journal-index`
- `cnki-journal-toc`
- `cnki-navigate-pages`
- `cnki-parse-results`

### Google Scholar Skills

这一组 skills 用于 Google Scholar 检索、翻页、引用追踪、全文链接解析和 BibTeX / Zotero 导出。

包含：

- `gs-search`
- `gs-advanced-search`
- `gs-cited-by`
- `gs-fulltext`
- `gs-export`
- `gs-navigate-pages`

## 说明

- 这个仓库只包含 skill 指令、脚本和模板，不包含 Zotero 数据库、PDF、Obsidian 笔记或私有缓存。
- 部分 skill 依赖本机应用状态，例如 Zotero、浏览器登录态或本地文件路径。
- 上传前已排除各 skill 内部的 `.git` 目录。

## License

MIT
