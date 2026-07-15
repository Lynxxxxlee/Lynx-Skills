---
name: explain-new-concepts
description: Explain unfamiliar concepts, terms, acronyms, frameworks, architectures, methods, protocols, paper ideas, tools, systems, or engineering and technical jargon. Use when the user asks what something is, says they have never heard of a concept, requests a quick conceptual explanation, asks for a card-style explanation, wants a selectable explanation depth, or wants a concise technical overview with optional paper/web citations or optional horizontal-vertical analysis.
---

# Explain New Concepts

Use this skill to help the user quickly understand an unfamiliar technical or engineering concept. Default to Chinese unless the user asks for another language.

## Selection Step

When the user has not already specified length, depth, research mode, and horizontal-vertical mode, open the local selector before explaining:

`assets/selector.html`

In a local desktop environment, open the file in the browser and ask the user to send back the generated configuration line. Do not answer the concept until the user returns the selector output, unless the user asks to skip selection.

If the selector cannot be opened, ask one short fallback question for the missing choices, or use defaults when the user clearly wants an immediate answer.

Selector fields:

- Length: `极简`, `标准`, `深入`
- Depth focus, multi-select: `概念入门`, `原理机制`, `工程落地`, `论文背景`
- Research: `不查`, `必要时查`, `必查`
- Horizontal-vertical analysis: `关闭`, `轻量`, `完整`

Defaults:

- Length: `标准`
- Depth focus: `概念入门`
- Research: `必要时查`
- Horizontal-vertical analysis: `关闭`

If the user returns a line like `解释设置：篇幅=标准；重点=概念入门、工程落地；资料检索=必要时查；纵横分析=轻量`, apply every selected focus. Combine the selected depth focuses instead of treating them as mutually exclusive.

## Response Shape

Prefer a compact concept card. Scale each section to the requested depth:

```markdown
**一句话定义**
...

**底层定义**
...

**逻辑内涵**
...

**简单类比**
...

**工程/实际应用**
...

**容易混淆的点**
...

**需要记住的核心**
...
```

Keep the answer short by default: usually 5-8 concise bullets or short paragraphs total. Do not turn the answer into a long survey unless the user asks for depth.

## Depth Selection

- If the user asks for `简单说`, `快速解释`, `一句话`, or similar, give a very short card and skip lower-value detail.
- If the user asks for `详细`, `深入`, `论文背景`, `原理`, or similar, expand the card and include more mechanism, assumptions, tradeoffs, and examples.
- If multiple depth focuses are selected, balance them in the same answer. For example, `原理机制、工程落地` should explain both how the concept works and where it is used.
- If the user asks for a visual interface, selector, options panel, or wants to choose length/depth, use the selection step before answering when available.
- If no depth is specified and the concept can be explained well at medium-short length, proceed with the default card.
- If the right depth materially changes the answer, ask one brief question about depth before answering.

## Horizontal-Vertical Analysis Option

Use horizontal-vertical analysis only when the user enables it, asks for `横纵分析`, asks for `纵横分析`, or the concept is broad enough that a simple definition would miss important context.

Interpret the method as:

- Vertical axis: trace the concept's origin, birth context, evolution, key turning points, and why it became what it is today.
- Horizontal axis: compare the concept at the current time slice with adjacent concepts, competing approaches, substitutes, or earlier-generation solutions.
- Intersection insight: explain how the historical path shaped the current position, what tradeoffs are inherited from that path, and what this implies for future use.

Modes:

- `轻量`: add a short `横纵视角` section with 2-4 bullets after the concept card.
- `完整`: expand into `纵向脉络`, `横向对比`, and `交汇洞察`. This mode usually requires research unless the topic is stable and well-known.
- `关闭`: do not include horizontal-vertical analysis.

Do not turn normal term explanations into long research reports. For this skill, horizontal-vertical analysis is an explanation enhancer, not a PDF-report workflow.

## Research and Citations

- Do not browse for every term by default.
- If the concept is new, niche, fast-moving, paper-specific, ambiguous, or you are uncertain, ask whether to look it up. Recommend the default of looking it up only when necessary.
- If the user asks for sources, papers, latest information, precise attribution, or says to查资料, search before answering.
- If the user selects `必查` or `完整` horizontal-vertical analysis, search before answering.
- Prefer primary or reliable sources: original papers, official docs, standards, or authoritative project pages. Use secondary web pages only when they clarify adoption or practical usage.
- Cite only the few sources that materially support the explanation. Avoid link dumps.

## Explanation Guidelines

- Start from the lowest useful definition: what object, process, abstraction, or guarantee the term names.
- Explain the logic inside the concept, not just the surface description.
- Use one simple analogy only when it clarifies the mechanism.
- Tie the concept to practical engineering use: where it appears, why engineers care, and what problem it solves.
- Include common confusions when they help prevent misunderstanding.
- End with the smallest durable takeaway the user should remember.

## Avoid

- Do not over-explain prerequisites unless they are necessary.
- Do not use hype, vague praise, or marketing language.
- Do not invent citations. If sources are needed but unavailable, say so clearly.
- Do not include many references when one paper or official page is enough.
