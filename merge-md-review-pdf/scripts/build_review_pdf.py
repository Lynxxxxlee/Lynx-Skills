#!/usr/bin/env python3
"""Build a formula-safe PDF from a directory of Markdown review notes."""

from __future__ import annotations

import argparse
import asyncio
import html
import re
import sys
from pathlib import Path


SKIP_DIRS = {
    ".git",
    ".obsidian",
    "__pycache__",
    "node_modules",
    "outputs",
    "output",
    "work",
    "tmp",
    "temp",
}


def natural_key(path: Path) -> list[object]:
    parts: list[object] = []
    for part in path.as_posix().split("/"):
        for chunk in re.split(r"(\d+)", part):
            if chunk.isdigit():
                parts.append(int(chunk))
            elif chunk:
                parts.append(chunk.lower())
    return parts


SourceNote = tuple[Path, str | None]


def discover_markdown(source_dir: Path) -> list[SourceNote]:
    files: list[Path] = []
    for path in source_dir.rglob("*.md"):
        if any(part in SKIP_DIRS for part in path.relative_to(source_dir).parts):
            continue
        if path.name.startswith("."):
            continue
        files.append(path)
    return [(path, None) for path in sorted(files, key=lambda p: natural_key(p.relative_to(source_dir)))]


def read_file_list(source_dir: Path, file_list: Path) -> list[SourceNote]:
    files: list[SourceNote] = []
    for raw_line in file_list.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        note_path, _, chapter_title = line.partition("\t")
        note_path = note_path.strip()
        chapter_title = chapter_title.strip() or None
        path = (source_dir / note_path).resolve()
        if not path.is_file():
            raise SystemExit(f"File listed but not found: {note_path}")
        files.append((path, chapter_title))
    return files


def build_asset_index(source_dir: Path) -> dict[str, list[Path]]:
    assets: dict[str, list[Path]] = {}
    for path in source_dir.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(source_dir).parts):
            continue
        assets.setdefault(path.name, []).append(path)
    return assets


def strip_frontmatter(text: str) -> str:
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[end + 5 :].lstrip()
    return text


def light_inline_html(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"__(.+?)__", r"<strong>\1</strong>", escaped)
    return escaped


def convert_highlights(text: str) -> str:
    out: list[str] = []
    in_fence = False
    fence_re = re.compile(r"^\s*(```|~~~)")
    highlight_re = re.compile(r"==(.+?)==")
    color_open_re = re.compile(r"~=\{([A-Za-z0-9_-]+)\}")

    for line in text.splitlines():
        if fence_re.match(line):
            in_fence = not in_fence
            out.append(line)
            continue
        if not in_fence:
            line = color_open_re.sub(
                lambda m: f'<mark class="hl-{html.escape(m.group(1).lower())}">',
                line,
            )
            line = line.replace("=~", "</mark>")
            line = highlight_re.sub(lambda m: f"<mark>{light_inline_html(m.group(1))}</mark>", line)
        out.append(line)
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def resolve_asset(raw_target: str, current_file: Path, source_dir: Path, asset_index: dict[str, list[Path]]) -> Path | None:
    target = raw_target.strip().replace("\\", "/").split("#", 1)[0]
    if not target or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
        return None
    for candidate in (current_file.parent / target, source_dir / target):
        if candidate.exists():
            return candidate.resolve()
    matches = asset_index.get(Path(target).name, [])
    if matches:
        return sorted(matches, key=lambda p: len(p.relative_to(source_dir).parts))[0].resolve()
    return None


def convert_links_and_images(text: str, current_file: Path, source_dir: Path, asset_index: dict[str, list[Path]]) -> str:
    def wiki_image(match: re.Match[str]) -> str:
        inner = match.group(1).strip()
        target, _, label = inner.partition("|")
        path = resolve_asset(target, current_file, source_dir, asset_index)
        alt = label or Path(target).stem
        if path:
            return f'<img src="{path.as_uri()}" alt="{html.escape(alt)}">'
        return f"![{alt}]({target})"

    def markdown_image(match: re.Match[str]) -> str:
        alt = match.group(1)
        target = match.group(2)
        path = resolve_asset(target, current_file, source_dir, asset_index)
        if path:
            return f"![{alt}]({path.as_uri()})"
        return match.group(0)

    def wiki_link(match: re.Match[str]) -> str:
        inner = match.group(1).strip()
        target, _, label = inner.partition("|")
        return label or target.split("#", 1)[0]

    text = re.sub(r"!\[\[([^\]]+)\]\]", wiki_image, text)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", markdown_image, text)
    text = re.sub(r"(?<!!)\[\[([^\]]+)\]\]", wiki_link, text)
    return text


def convert_callouts(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    callout_re = re.compile(r"^>\s*\[!([A-Za-z][A-Za-z0-9_-]*)\]\s*(.*)$")

    while i < len(lines):
        match = callout_re.match(lines[i])
        if not match:
            out.append(lines[i])
            i += 1
            continue

        kind = match.group(1).lower()
        title = match.group(2).strip() or match.group(1).upper()
        body: list[str] = []
        i += 1
        while i < len(lines):
            line = lines[i]
            if line.startswith(">"):
                body.append(re.sub(r"^>\s?", "", line))
                i += 1
                continue
            if line.strip() == "":
                body.append("")
                i += 1
                continue
            break

        out.append(f'<div class="callout callout-{kind}" markdown="1">')
        out.append(f'<div class="callout-title">{html.escape(title)}</div>')
        out.append("")
        out.extend(body)
        out.append("</div>")
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def separate_markdown_tables(text: str) -> str:
    """Add a blank line after pipe tables so following notes do not become cells."""
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    in_fence = False
    fence_re = re.compile(r"^\s*(```|~~~)")
    table_line_re = re.compile(r"^\s*\|?.+\|.+$")
    separator_re = re.compile(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$")

    while i < len(lines):
        line = lines[i]
        if fence_re.match(line):
            in_fence = not in_fence
            out.append(line)
            i += 1
            continue

        if (
            not in_fence
            and i + 1 < len(lines)
            and table_line_re.match(line)
            and separator_re.match(lines[i + 1])
        ):
            out.append(line)
            i += 1
            out.append(lines[i])
            i += 1
            while i < len(lines) and table_line_re.match(lines[i]):
                out.append(lines[i])
                i += 1
            if i < len(lines) and lines[i].strip():
                out.append("")
            continue

        out.append(line)
        i += 1

    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def prepare_markdown(text: str, current_file: Path, source_dir: Path, asset_index: dict[str, list[Path]]) -> str:
    text = strip_frontmatter(text)
    text = convert_links_and_images(text, current_file, source_dir, asset_index)
    text = convert_callouts(text)
    text = convert_highlights(text)
    text = separate_markdown_tables(text)
    return text


def starts_with_heading(text: str, heading: str) -> bool:
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("<!--"):
            continue
        return stripped == f"# {heading}" or stripped == f"# {heading} "
    return False


def build_combined_markdown(source_dir: Path, md_files: list[SourceNote], title: str, case_summary: Path | None) -> str:
    asset_index = build_asset_index(source_dir)
    chunks = [f"# {title}", ""]
    for path, chapter_title in md_files:
        rel = path.relative_to(source_dir).as_posix()
        text = prepare_markdown(path.read_text(encoding="utf-8"), path, source_dir, asset_index)
        chunks.extend(['<div class="source-break"></div>', "", f"<!-- source: {rel} -->", ""])
        if chapter_title and not starts_with_heading(text, chapter_title):
            chunks.extend([f"# {chapter_title}", ""])
        chunks.extend([text.strip(), ""])

    if case_summary:
        case_source = case_summary.resolve().parent
        case_text = prepare_markdown(
            case_summary.read_text(encoding="utf-8"),
            case_summary.resolve(),
            case_source,
            build_asset_index(case_source),
        )
        chunks.extend(
            [
                '<div class="source-break"></div>',
                "",
                "# 老师案例总结",
                "",
                case_text.strip(),
                "",
            ]
        )
    return "\n".join(chunks)


def markdown_to_html(markdown_text: str) -> str:
    try:
        import markdown
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: markdown. Install it with `python3 -m pip install markdown`."
        ) from exc

    math_blocks: list[str] = []

    def stash_math(match: re.Match[str]) -> str:
        math_blocks.append(match.group(0))
        return f"@@MATH{len(math_blocks) - 1}@@"

    # Protect TeX from Markdown emphasis parsing, especially underscores in
    # symbols such as \bar{P}_t and subscripts in finance formulas.
    protected = re.sub(r"\$\$(.+?)\$\$", stash_math, markdown_text, flags=re.DOTALL)
    protected = re.sub(r"(?<!\$)\$(?!\$)([^\n$]+?)(?<!\$)\$(?!\$)", stash_math, protected)

    rendered = markdown.markdown(
        protected,
        extensions=[
            "extra",
            "fenced_code",
            "footnotes",
            "tables",
            "toc",
            "sane_lists",
            "attr_list",
            "md_in_html",
        ],
        output_format="html5",
    )
    for index, math in enumerate(math_blocks):
        rendered = rendered.replace(f"@@MATH{index}@@", math)
    return wrap_tables_like_obsidian(rendered)


def add_heading_toc(rendered: str, title: str) -> str:
    """Insert a clickable h1/h2 table of contents after the document title."""
    heading_re = re.compile(r'<h([12]) id="([^"]+)">(.*?)</h\1>', flags=re.DOTALL)
    entries: list[tuple[int, str, str]] = []

    for match in heading_re.finditer(rendered):
        level = int(match.group(1))
        target_id = match.group(2)
        raw_text = re.sub(r"<[^>]+>", "", match.group(3))
        text = html.unescape(re.sub(r"\s+", " ", raw_text)).strip()
        if not entries and text == title:
            continue
        entries.append((level, target_id, text))

    if not entries:
        return rendered

    items = [
        '<nav class="toc" aria-label="目录">',
        "<h1>目录</h1>",
        '<ol class="toc-list">',
    ]
    for level, target_id, text in entries:
        safe_id = html.escape(target_id, quote=True)
        safe_text = html.escape(text)
        items.append(
            f'<li class="toc-item toc-level-{level}"><a href="#{safe_id}">{safe_text}</a></li>'
        )
    items.extend(["</ol>", "</nav>"])
    toc_html = "\n".join(items)

    first_h1 = re.search(r"</h1>", rendered)
    if not first_h1:
        return toc_html + "\n" + rendered
    insert_at = first_h1.end()
    return rendered[:insert_at] + "\n" + toc_html + "\n" + rendered[insert_at:]


def wrap_tables_like_obsidian(rendered: str) -> str:
    """Wrap Markdown tables so print CSS can size them like Obsidian notes."""

    def classify_table(match: re.Match[str]) -> str:
        table = match.group(0)
        first_row = re.search(r"<tr[^>]*>(.*?)</tr>", table, flags=re.DOTALL)
        first_row_html = first_row.group(1) if first_row else ""
        columns = len(re.findall(r"<t[dh][^>]*>", first_row_html))
        visible_text = re.sub(r"<[^>]+>", " ", table)
        text_len = len(re.sub(r"\s+", "", visible_text))

        classes = ["table-wrap"]
        if columns >= 4 or text_len > 700:
            classes.append("wide")
        if columns >= 5 or text_len > 1300:
            classes.append("very-wide")

        return f'<div class="{" ".join(classes)}">{table}</div>'

    return re.sub(r"<table[^>]*>.*?</table>", classify_table, rendered, flags=re.DOTALL)


def wrap_html(body: str, title: str) -> str:
    safe_title = html.escape(title)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{safe_title}</title>
<script>
window.MathJax = {{
  tex: {{
    inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
    displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
    processEscapes: true,
    tags: 'ams'
  }},
  options: {{ skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'] }}
}};
</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
<style>
@page {{
  size: A4;
  margin: 18mm 16mm 20mm 16mm;
  @bottom-center {{
    content: counter(page);
    font-size: 9px;
    color: #6b7280;
  }}
}}
* {{ box-sizing: border-box; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans CJK SC", Arial, sans-serif;
  color: #111827;
  font-size: 13px;
  line-height: 1.65;
  letter-spacing: 0;
}}
h1, h2, h3, h4 {{
  color: #0f172a;
  line-height: 1.25;
  break-after: avoid;
}}
h1 {{
  font-size: 26px;
  border-bottom: 2px solid #111827;
  padding-bottom: 8px;
  margin: 0 0 18px;
}}
h2 {{ font-size: 20px; margin: 24px 0 10px; }}
h3 {{ font-size: 16px; margin: 18px 0 8px; }}
p, ul, ol, pre, blockquote, .callout, .table-wrap {{ margin-top: 0; margin-bottom: 12px; }}
a {{ color: #075985; text-decoration: none; }}
.toc {{
  margin: 12px 0 24px;
}}
.toc h1 {{
  font-size: 22px;
  margin-top: 8px;
}}
.toc-list {{
  list-style: none;
  padding: 0;
  margin: 0;
  column-count: 2;
  column-gap: 28px;
}}
.toc-item {{
  break-inside: avoid;
  margin: 0 0 5px;
  line-height: 1.35;
}}
.toc-level-1 {{
  font-weight: 700;
  margin-top: 8px;
}}
.toc-level-2 {{
  padding-left: 14px;
  font-size: 12px;
  color: #334155;
}}
.toc a {{
  color: inherit;
  text-decoration: none;
}}
mark {{
  background: #fff3a3;
  color: #111827;
  padding: 0 2px;
  border-radius: 2px;
}}
.hl-red {{
  background: #fee2e2;
  color: #991b1b;
}}
.hl-blue {{
  background: #dbeafe;
  color: #1e3a8a;
}}
.hl-green {{
  background: #dcfce7;
  color: #166534;
}}
.hl-yellow {{
  background: #fef3c7;
  color: #92400e;
}}
blockquote {{
  border-left: 4px solid #94a3b8;
  background: #f8fafc;
  margin-left: 0;
  padding: 8px 12px;
  color: #334155;
}}
.callout {{
  border: 1px solid #cbd5e1;
  border-left: 5px solid #2563eb;
  background: #f8fafc;
  border-radius: 6px;
  padding: 10px 12px;
  break-inside: avoid;
}}
.callout-title {{
  font-weight: 700;
  margin-bottom: 6px;
  color: #0f172a;
}}
.callout-warning, .callout-caution, .callout-danger {{
  border-left-color: #dc2626;
  background: #fff7ed;
}}
.callout-tip, .callout-success, .callout-example {{
  border-left-color: #16a34a;
  background: #f0fdf4;
}}
.table-wrap {{
  width: 100%;
  overflow: visible;
  break-inside: auto;
}}
.table-wrap table {{
  border-collapse: collapse;
  width: auto;
  max-width: 100%;
  table-layout: auto;
  font-size: 12px;
  line-height: 1.45;
}}
.table-wrap.wide table {{ font-size: 10.5px; }}
.table-wrap.very-wide table {{ font-size: 9.2px; }}
thead {{ display: table-header-group; }}
tr {{ break-inside: avoid; }}
th, td {{
  border: 1px solid #d0d7de;
  padding: 6px 10px;
  vertical-align: top;
  min-width: 64px;
  max-width: 260px;
  overflow-wrap: anywhere;
  word-break: normal;
}}
.table-wrap.wide th, .table-wrap.wide td {{
  max-width: 220px;
  padding: 5px 7px;
}}
.table-wrap.very-wide th, .table-wrap.very-wide td {{
  max-width: 180px;
  padding: 4px 6px;
}}
th {{ background: #f6f8fa; font-weight: 700; }}
code {{
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  background: #f1f5f9;
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 12px;
}}
pre {{
  background: #0f172a;
  color: #e5e7eb;
  padding: 10px 12px;
  border-radius: 6px;
  white-space: pre-wrap;
  word-break: break-word;
  break-inside: avoid;
}}
pre code {{
  background: transparent;
  color: inherit;
  padding: 0;
}}
img {{ max-width: 100%; }}
.source-break {{
  break-before: page;
  height: 0;
}}
.MathJax, mjx-container {{
  break-inside: avoid;
}}
</style>
</head>
<body>
{body}
</body>
</html>
"""


async def html_to_pdf(html_path: Path, output_pdf: Path) -> None:
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: playwright. Install it with `python3 -m pip install playwright` "
            "and `python3 -m playwright install chromium`."
        ) from exc

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1240, "height": 1754})
        await page.goto(html_path.as_uri(), wait_until="networkidle")
        await page.wait_for_function("window.MathJax && MathJax.startup && MathJax.startup.promise")
        await page.evaluate("MathJax.typesetPromise && MathJax.typesetPromise()")
        await page.pdf(
            path=str(output_pdf),
            format="A4",
            print_background=True,
            margin={"top": "18mm", "right": "16mm", "bottom": "20mm", "left": "16mm"},
        )
        await browser.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_dir", type=Path, help="Directory containing Markdown review notes.")
    parser.add_argument("output_pdf", type=Path, help="Final PDF path.")
    parser.add_argument("--title", default="复习资料合订本", help="Document title.")
    parser.add_argument("--case-summary", type=Path, help="Markdown case summary to append at the end.")
    parser.add_argument("--file-list", type=Path, help="UTF-8 text file listing Markdown files in merge order.")
    parser.add_argument("--work-dir", type=Path, help="Directory for combined Markdown and HTML.")
    parser.add_argument("--toc", action="store_true", help="Insert a clickable h1/h2 table of contents.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_dir = args.source_dir.resolve()
    output_pdf = args.output_pdf.resolve()
    work_dir = (args.work_dir or output_pdf.parent / "_review_pdf_work").resolve()

    if not source_dir.is_dir():
        raise SystemExit(f"Source directory does not exist: {source_dir}")
    if args.case_summary and not args.case_summary.is_file():
        raise SystemExit(f"Case summary does not exist: {args.case_summary}")

    md_files = read_file_list(source_dir, args.file_list) if args.file_list else discover_markdown(source_dir)
    if not md_files:
        raise SystemExit(f"No Markdown files found under: {source_dir}")

    work_dir.mkdir(parents=True, exist_ok=True)
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    combined_md = build_combined_markdown(source_dir, md_files, args.title, args.case_summary)
    combined_md_path = work_dir / "combined.md"
    html_path = work_dir / "combined.html"
    combined_md_path.write_text(combined_md, encoding="utf-8")

    body = markdown_to_html(combined_md)
    if args.toc:
        body = add_heading_toc(body, args.title)
    html_path.write_text(wrap_html(body, args.title), encoding="utf-8")

    asyncio.run(html_to_pdf(html_path, output_pdf))

    print(f"Markdown files: {len(md_files)}")
    print(f"Combined Markdown: {combined_md_path}")
    print(f"Combined HTML: {html_path}")
    print(f"Output PDF: {output_pdf}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
