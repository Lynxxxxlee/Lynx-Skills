---
name: merge-md-review-pdf
description: Combine Markdown review notes into a polished study PDF with verified math rendering, highlights, callout/text blocks, tables, code blocks, and an appended case-summary section. Use when a user asks to merge course review Markdown files, Obsidian-style notes, or study directories into one PDF, especially when formulas and styled blocks must render correctly.
---

# Merge Markdown Review PDF

## Workflow

1. Locate the review directory and separate source types:
   - Review notes: Markdown files intended for the main study PDF.
   - Case materials: teacher-provided examples, handouts, PDFs, DOCX, PPTX, or Markdown files that should be summarized and appended.
   - Ignore generated outputs, temporary files, package folders, and unrelated notes.
2. Read the Markdown file list before conversion. Preserve the original outline order when filenames are numbered; otherwise sort naturally by filename and path. If the user wants explicit chapter labels such as `第一章` and `第二章`, put those labels in the file list so the script inserts them as document headings and table-of-contents entries.
3. Create a concise `case-summary.md` from the teacher case materials. Include:
   - Case background and decision problem.
   - Known data and assumptions.
   - Relevant engineering-economics method, such as NPV, IRR, payback period, annual worth, cost-benefit ratio, depreciation, or sensitivity analysis.
   - Calculation logic and final takeaway.
4. Run `scripts/build_review_pdf.py` to combine the notes and optional case summary:

```bash
python3 /Users/clissa/.codex/skills/merge-md-review-pdf/scripts/build_review_pdf.py \
  "/path/to/工程经济学复习" \
  "/path/to/outputs/工程经济学复习资料合订本.pdf" \
  --title "工程经济学复习资料合订本" \
  --file-list "/path/to/work/file-order.txt" \
  --case-summary "/path/to/work/case-summary.md" \
  --toc
```

Use `--file-list` when chapter order matters or when the directory contains non-review Markdown such as an Obsidian welcome note. The file list is UTF-8 plain text, one source-dir-relative Markdown path per line. To insert a chapter divider before a file, add a tab and the chapter title after the path:

```text
工程经济学 - 第一章.md	第一章
工程经济学 - 第二章.md	第二章
工程经济学-第三章.md	第三章
```

If a source note already starts with the same `# 章节标题`, the script does not insert a duplicate heading.
Use `--toc` when the study PDF should start with a clickable table of contents built from level-1 and level-2 headings.

5. Render and inspect the final PDF before delivery:

```bash
pdfinfo "/path/to/outputs/工程经济学复习资料合订本.pdf"
pdftoppm -png -r 160 "/path/to/outputs/工程经济学复习资料合订本.pdf" "/path/to/work/rendered/page"
```

Inspect representative rendered pages, including pages with formulas, tables, highlights, callouts, and the appended case summary.

## Conversion Standards

- Keep source Markdown unchanged. Write intermediate combined Markdown/HTML under a working directory.
- Preserve TeX math delimiters: `$...$`, `$$...$$`, `\(...\)`, and `\[...\]`.
- Render formulas through MathJax in the browser and wait until `MathJax.typesetPromise()` completes before printing to PDF.
- Convert Obsidian-style `==highlight==` into `<mark>highlight</mark>` outside fenced code blocks.
- Convert Obsidian-style callouts like `> [!NOTE] Title` into styled blocks instead of plain blockquotes.
- Normalize Markdown table boundaries before rendering so headings, images, and paragraphs immediately following an Obsidian table do not get swallowed into the last row.
- Use print CSS with readable Chinese fonts, Obsidian-like table borders/header shading, non-clipped code blocks, page numbers, and section page breaks.
- Wrap Markdown tables before PDF rendering so wide Obsidian notes can use automatic column widths and smaller print font sizes instead of being forced into equal-width columns.
- When requested, insert a front table of contents with internal links to all level-1 and level-2 headings.
- When a file list provides chapter titles, insert those titles as level-1 headings before each corresponding note so they appear in the body and table of contents; skip insertion when the note already starts with the same level-1 heading.
- Avoid low-fidelity converters when formulas matter. Browser-rendered HTML-to-PDF is preferred over direct Markdown-to-PDF conversion.

## Dependencies

The script needs Python packages `markdown` and `playwright`, plus a Playwright Chromium browser:

```bash
python3 -m pip install markdown playwright
python3 -m playwright install chromium
```

For validation, use Poppler tools `pdfinfo` and `pdftoppm` when available. If Poppler is missing, still open the PDF visually and inspect the generated HTML.

## Quality Checks

- Open the generated HTML if the PDF has suspicious spacing; the HTML path is printed by the script.
- Check that formulas show as typeset math, not raw TeX, black boxes, or missing symbols.
- Check highlights render with a visible background and readable text.
- Check callouts render as boxed note/tip/warning blocks with intact body text.
- Check tables visually on representative rendered pages, especially long Obsidian tables. They should keep thin borders, readable header shading, and non-overlapping wrapped cell text.
- If a table of contents is requested, check that the first pages show the h1/h2 directory and that PDF link annotations exist.
- If chapter titles are provided through the file list, check that the table of contents shows those chapter labels and that the first page of each note begins with the intended chapter heading without duplicates.
- Confirm the appended case summary appears after all review notes and has its own heading/page break.
