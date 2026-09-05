# Mainframe Modernization Edge-Case Checklist

Check only items applicable to discovered source, but explicitly record applicability.

## Files and datasets

RECFM F/V/VB, LRECL/BLKSIZE, EBCDIC/code pages, CR/LF translation, binary fields, COMP/COMP-3, signed zoned decimal, implied decimals, truncation/ROUNDED, copybook offsets, REDEFINES, OCCURS and OCCURS DEPENDING ON, 88-level values, filler, variable layouts, headers/trailers, empty files, short/malformed records, duplicate records/keys, stable sort and EBCDIC-vs-Unicode collation, DFSORT/SYNCSORT/ICETOOL control cards, IEBGENER/IDCAMS behavior, concatenated DDs, DISP/CATLG/DELETE/PASS, temporary datasets, GDG relative generations, file allocation/replacement, partial writes, record-count reconciliation.

## COBOL execution

PERFORM ranges, fall-through, GO TO, EVALUATE, nested IF scope, INITIALIZE, STRING/UNSTRING/INSPECT, reference modification, subscripts/indexes, SEARCH/SEARCH ALL assumptions, arithmetic size error, numeric class tests, HIGH/LOW-VALUES, spaces/zeros, MOVE CORRESPONDING, truncation, CALL linkage and copybooks, RETURN-CODE, STOP RUN/GOBACK, abend/error paths.

## JCL and scheduler

PROC expansion, symbolic parameters, overrides, step names/program binding, PARM, DD *, control cards, COND/IF/THEN/ELSE, return-code dependencies, restart step behavior, job/step time limits, environment variables, predecessor/successor jobs, calendars, rerun semantics, stdout/stderr, exit-code mapping.

## DB2 / SQL

Host variable type/scale, indicator variables, NULL behavior, SQLCODE/SQLSTATE branches, singleton SELECT no-row/multi-row behavior, cursor ORDER BY, WITH HOLD, isolation/locks, commit frequency, rollback, savepoints, duplicate keys, identity/sequence, CHAR/VARCHAR padding, DECIMAL precision, DATE/TIME/TIMESTAMP, CURRENT DATE/TIMESTAMP, DB2 functions/syntax, MERGE, temporary tables, indexes that affect deterministic access assumptions, empty string differences, Oracle conversion behavior.

## Operational correctness

Atomic output replacement, checkpoint/restart, idempotency, duplicate rerun prevention, concurrent invocations, large-file streaming, disk-full/write failure, DB unavailable/locked, cleanup after failure, log sensitivity, secrets/configuration, timezone/locale, deterministic results, exit codes and monitoring signals.
