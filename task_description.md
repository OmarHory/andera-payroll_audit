### 1. Metadata dictionary — a compact, *extensible* core

Below is a lean set of keys that works for **any** file type, plus a few type-specific add-ons.  
Keep everything in one flat dict per file; if a key is not applicable simply omit it.

| Key | Why it matters |
|-----|----------------|
| `file_name` | Anchor for humans & logs. |
| `file_type` | `png / jpeg / pdf / xlsx / csv / …`. |
| `size_bytes` | Quick sanity check (e.g. empty files). |
| `created_ts` & `modified_ts` | Traceability / versioning. |
| `hash_sha256` | De-duplication, tamper check. |
| `source_path` | Re-locate the file later. |
| `detected_domain` | Broad label such as **payroll_export / bank_statement / settlement_runs** (filled by the *Document-Classifier* agent). |
| `preview_text` | First 500 chars of OCR/text — boosts retrieval. |
| `language` | Useful for non-English docs. |
| `tables_detected` | `true/false` (down-stream agents know to parse as tabular). |
| `pages` | For PDFs only. |
| `image_dims` | `(w,h)` – images only. |
| `sheet_names` | List – spreadsheets only. |
| `column_headers` | First row of any CSV / sheet; helps the reasoning model map concepts. |
| `possible_use_cases` | *LLM-generated*, e.g. “Compare ADP gross pay vs bank withdrawals”. |
| `quality_score` | Heuristic (clarity / parse success) so the agent can skip junk. |

> **Tip:** store each dict as a row in a lightweight DuckDB table; that gives you SQL-like retrieval *and* in-memory speed.

---

### 2. Multi-agent workflow (high level)

```mermaid
graph TD
A[Ingestion Agent] --> B[Metadata Extractor(s)]
B --> C[Document Classifier]
C -->|indexed metadata| D[Task Manager]
D -->|one task| E[Doc-Selector Agent]
E -->|doc handles| F[Execution / Reasoning Agent]
F --> G[Reflector & Validator]
G -->|pass/fail & rationales| H[Reporter]
G -->|needs more evidence| E


| Stage | Role & key decisions |
|-------|----------------------|
| **B. Metadata Extractors** | Modular: Vision→OCR, PDF→text+tables, Excel/CSV→DataFrame, etc. Output = dicts above. |
| **C. Document Classifier** | LLM (few-shot) that tags each dict with `detected_domain`. Relies only on text/headers — no hard-coded filenames. |
| **D. Task Manager** | Reads `payroll_rec_tasks.txt`; spawns one *Task-Run* per bullet. |
| **E. Doc-Selector Agent** | Vector / keyword search over metadata to produce a ranked doc list for the task. |
| **F. Execution / Reasoning** | • Uses tool-calling: pandas for tabular, vision model for images, PDF parser for statements.<br>• Produces a structured **Verdict** object: `{task_id, status, evidence, reasoning}`. |
| **G. Reflector & Validator** | Self-critique pass: if confidence < τ or evidence sparse, returns control to **E** with new hints (e.g. “look for bank withdrawals sheet”). |
| **H. Reporter** | Aggregates all verdicts, writes the final JSON / spreadsheet for the auditor. |

**Concurrency pattern:** run one *Task-Run* per task; inside it keep the **E → F → G** loop until success or max-tries.  
**State store:** tiny Postgres or Redis keyed by `task_run_id` to make the system resumable.

---

### 3. Handling Excel/CSV gracefully
1. **Load to DataFrame** (pandas or Polars).  
2. **Optional:** register the DataFrame in DuckDB (`duckdb.register('sheet1', df)`) — run pure SQL *and* keep DataFrame flexibility.  
3. **Normalize headers** (strip, lowercase) once; later agents operate on canonical names.  
4. Keep the DataFrame inside the metadata dict under a lazy getter (only materialize when the Execution agent requests it).

---

### 4. Putting it together quickly
- **LangGraph** or **CrewAI** gives you the loop & shared state out of the box.  
- Use **LLM function-calling** to generate SQL, pandas code, or to pick which extractor to invoke.  
- **Logging:** have every agent append a short entry to the metadata store; that becomes your audit trail for *how* the AI reached its decisions.
