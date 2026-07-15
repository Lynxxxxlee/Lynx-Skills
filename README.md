# Lynx-Skills

我自己日常使用的一些 AI Skills 合集，偏论文阅读、资料整理和技术概念解释。

每个目录都是一个可独立安装的 Skill，核心入口是对应目录下的 `SKILL.md`。

## 目录

| Skill | 一句话 |
| --- | --- |
| `explain-new-concepts` | 用中文快速解释陌生技术概念，可选择篇幅、深度、资料检索和纵横分析。 |
| `obzetero-paper-reader` | 从 Zotero 读取待阅读论文，生成中文精读笔记并同步到 Obsidian。 |
| `merge-md-review-pdf` | 将 Markdown / Obsidian 复习资料合并成带目录、公式和样式校验的 PDF。 |

## 安装方式

在支持 `SKILL.md` 的 Agent 中，可以让 Agent 安装单个目录：

```text
帮我安装这个 skill：https://github.com/Lynxxxxlee/Lynx-Skills/tree/main/explain-new-concepts
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

## 说明

- 这个仓库只包含 skill 指令、脚本和模板，不包含 Zotero 数据库、PDF、Obsidian 笔记或私有缓存。
- 部分 skill 依赖本机应用状态，例如 Zotero、浏览器登录态或本地文件路径。
- 上传前已排除各 skill 内部的 `.git` 目录。

## License

MIT
