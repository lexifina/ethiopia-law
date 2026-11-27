# Structure

How this repository is laid out, and how a commit is dated.

## Folders

| Folder | What is in it |
| --- | --- |
| `constitution/` | The Constitution of the Federal Democratic Republic of Ethiopia, Proclamation No. 1/1995 |
| `proclamations/<year>/<number>-<slug>/` | Federal proclamations of the House of Peoples' Representatives, by the year and number of the proclamation (`proclamations/2019/1156-labour/` is Labour Proclamation No. 1156/2019) |
| `regulations/<year>/<number>-<slug>/` | Council of Ministers regulations, the same way (`regulations/2020/0469-...` is Regulation No. 469/2020) |
| `directives/nbe/<year>/<code>-<slug>/` | Directives of the National Bank of Ethiopia, by the year in the directive's number (`directives/nbe/2025/sbb-95-2025-...` is Directive No. SBB/95/2025); one file per article, or `text.md` when the articles cannot be told apart; dated on the day the directive's own effective-date article names |
| `data/`, `tools/` | Tables and the scripts that read the history |

The number is written with four digits (`0469`) so that a folder listing sorts in number order. The year is the year in
the act's own number (No. 1357/2024 is in `2024/` even though its Gazette issue is dated 2025). No year folder holds
more than about 300 acts.

Inside an act's folder there is one file per article (`art-001.md`, `art-002.md`, ...), `preamble.md` (the number line,
title and the "WHEREAS" recitals), `signature.md` (the "Done at Addis Ababa" formula and the signatory) and, where the
Gazette prints text after the signature (a schedule, a table, a ratified agreement), `annex.md`. `README.md` lists the
files. Each article file starts with `# Article N: heading` as printed.

## Text

The English column of the bilingual Federal Negarit Gazette issue, read from the PDF's text layer. The Amharic text,
which prevails where the two differ, is not part of this record. No OCR is used: an issue that is only a scan is left
out until a text copy is found. Running heads, page numbers and the Amharic column are left out; PART/CHAPTER/SECTION
headings are not units.

## Commits and dates

One commit per version of an act. The commit is dated 12:00 Africa/Addis_Ababa (UTC+3) on the day the version came
into force, read from the act's own commencement article ("shall enter into force on the date of publication in the
Federal Negarit Gazette") and the issue's dates (cover, running heads, signature), which must agree. An act whose dates
disagree, or whose in-force day is not stated, is left out rather than dated by guess; the day we fetched it is never
used. Dates are Gregorian; the Ethiopian calendar date of the same day is kept in the `Ethiopian-date` trailer.

The author of a commit is the instrument (for example `Proclamation No. 1156/2019`); the committer is Lexifina.
Trailers: `Law`, `Kind`, `Published`, `In-force`, `In-force-evidence`, `Ethiopian-date`, `Source`, `Source-sha256`,
`Act`, `Provisions`, `Text`.

Acts are added in batches, so commits are in the order they were added, not in date order; the author date is the
in-force day. Each act is held as first published: amending proclamations are their own folders and are not yet
applied to the act they amend.

## Corpus

`corpus.json` names this corpus `et/national/acts` for [global-law](https://github.com/lexifina/global-law).
