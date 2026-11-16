# Tools

The scripts behind this Ethiopia-only run of global-law's vulnerability detectors. They run inside a copy of
[global-law/vulnerabilities/scripts](https://github.com/lexifina/global-law/tree/main/vulnerabilities/scripts) (Python 3.11+,
`pip install duckdb pyarrow`), with a bare clone of this repository at `sources/corpus/ethiopia-law.git`, a blobless bare
clone of global-law at `sources/global-law.git`, and a `pins.json` that names only ethiopia-law and its commit.
`build_vulns.py`, `flags_chart.py`, `late_ext_select.py` and `late_ext_rebut.py` sit two folders above the scripts, next to
`config.json`.

| Script | What it does |
| --- | --- |
| `run.sh` | Indexes the history and texts, maps paths to moved folders (`map_moved.py`), adds this repository's history rows, and runs the detectors (`bash run.sh <shards>`) |
| `map_moved.py` | For a repository that moved its act folders (`data/paths.json`), rewrites the paths in the history table to each act's folder today, so that an act's history is not split in two at the move; this repository has moved none, and it changed nothing |
| `add_root.py` | Builds the history rows from this repository's own commits (global-law replays it only up to an earlier commit), so the history detectors read every change |
| `run_triage.sh` | The model review: the 40 strongest flags per category, the 40 strongest lapsed time limits in law texts, and the empty periods (here, the five retroactive dates; there were no lapsed time limits or empty periods) |
| `late_ext_select.py` | Chooses the empty periods for global-law's review of that category (there were none here) |
| `late_ext_rebut.py` | Adds the second, arguing-against pass to the empty-period review, as `triage.py` does for the other categories |
| `build_vulns.py` | Builds `data/flags.csv`, `data/reviewed.csv` and `data/by_category.csv` from the findings and the model review |
| `flags_chart.py` | Draws the chart at the top of the README, in English, light and dark |
| `config.json` | The repository, its language (English), the category names, the paths that are not law, and the chart's labels |
| `patch_detectors.py` | Fixes blind spots found in runs on several country repositories in the copy of global-law's scripts (`python -X utf8 patch_detectors.py <scripts dir>`; a fix already in place is skipped) |
| `patch_detectors_vi.py` | The same for Vietnamese dates, references and amounts (found by the Vietnam run); it changes nothing here, but `redo.py` runs it on every repository |
| `patch_es.py`, `patch_ca.py`, `patch_de.py` | The same for Spanish, Catalan and German (Austrian) dates, references and currency names; they change nothing here either |
| `patch_en.py` | English fixes to `detectors/placeholder_ref.py` made for bhutan-law ("vacation", "null and void", an amending act's "Section … is repealed"), in the same form |
| `patch_en_et.py` | The English fixes made for this repository, in the same form (`python -X utf8 patch_en_et.py <scripts dir>`; see below); `redo.py` does not run it, so run it after the others |
| `patch_build_r7.py` | Brings a country's `build_vulns.py` up to date: lapsed-limit reviews matched on 400 characters of context, not 80, and a file deleted before a folder move linked under its old folder (already applied to the `build_vulns.py` here) |
| `redo.py` | Runs the patches above it except `patch_en_et.py`, then again only the scans and detectors the fixes change, the model review of lapsed time limits, references to deleted provisions and empty periods, and the build (`python -X utf8 redo.py <run folder> [--keep-reviews] [--full]`; `--full` runs every step again through `run.sh`, `map_moved.py` among them, sends every category to the model and keeps every review already made; `EMBED_FONTS` names the script that embeds the chart's fonts); not needed here, as the fixes were in place before the review |

The model review needs `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` and `LLM_AUTH` set for an OpenAI-compatible Responses API.
It was run as `bash run_triage.sh '^(data|tools|vulnerabilities)/'`.

Changes made for this repository:

- `pins.json` names the corpus language as `en` (global-law's list of corpora gave none), so the detectors use the English
  month names and the English currency exceptions. `add_root.py` is unchanged: the 72 commits that make a version as
  enacted carry `Kind: law`, the six that hold a proclamation's oldest available version `Kind: publisher`, which it also
  counts as law, and the 15 that change only documentation, tables and tools carry no `Kind` and are left out.
- `detectors/placeholder_ref.py` (`patch_en_et.py`) no longer takes a repeal article that repeals a whole earlier law
  ("1/ The Public Enterprises Proclamation No. 25/1992 is hereby repealed.", "… is here by repealed.") for an article
  marked repealed: `patch_en.py`'s test for a repealing provision knew only "Section/Article … is repealed", and now also
  knows a named proclamation, act, law, code, decree, regulation or directive, with its number, and "here by". It no
  longer reads "shall be deleted" ("The information registered shall be deleted by line on it") as the mark of a deleted
  article. References to repealed placeholders went from 3 to 0; dead fines, which use the same test, stayed at 0. The
  detector was run again after the fix, before the model review.
- `config.json` counts as not law `data/`, `tools/`, `vulnerabilities/`, the root files and every `README.md` (each act's
  list of its articles).
