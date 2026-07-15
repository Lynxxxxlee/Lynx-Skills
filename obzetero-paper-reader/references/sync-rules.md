# Sync Rules

Reading status values:

| Zotero tag | Obsidian status | Index marker |
| --- | --- | --- |
| 已读 | read | `[x]` |
| 阅读中 | reading | `[>]` |
| 未读 | unread | `[ ]` |

Intensive-reading trigger:

| Zotero tag | Meaning |
| --- | --- |
| 待阅读, /待阅读, 马上读, /马上读, 阅读中, or /阅读中 | Prepare this paper for automatic Chinese intensive-reading notes |

Rules:

- Existing nested Zotero tags like `/已读`, `/阅读中`, and `/未读` count as status tags when reading.
- Writeback creates plain tags `已读`, `阅读中`, and `未读` unless the user asks to keep nested tag paths.
- `待阅读` and `马上读` are work-queue tags. `阅读中` is both a reading status and a trigger that controls whether `read` prepares a paper for Chinese intensive reading.
- A paper should have at most one Zotero reading-status tag.
- If multiple Zotero status tags exist, use priority `阅读中 > 已读 > 未读`.
- If no Zotero status tag exists, treat the paper as `unread` but do not write `未读` unless Obsidian explicitly asks for `unread` during writeback.
- Obsidian frontmatter `status` and collection index markers should agree.
- When writing Zotero status, remove old status tags before adding the desired tag.
- Keep `.obzetero/state.json` as the sync ledger.
- If a conflict is detected that cannot be resolved, preserve both values and report it to the user instead of overwriting silently.
