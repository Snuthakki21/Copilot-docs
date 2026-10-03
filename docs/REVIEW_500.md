# 500 distinct executable reviews — 3 October 2026

All **500 numbered scenarios passed** in one combined execution, with no skips and an unchanged code fingerprint. The complete regression suite then passed **748 tests in 68.775 seconds**. TypeScript, the committed frontend build, folder validation and diff checks passed.

The six subsystem reviews and integration review reproduced failures in **146 scenarios** before their associated fixes. Several scenarios share one defect, so this is not a claim of that many unique bugs. These are 500 different named scenarios, not 500 repetitions of one suite or 500 independent reviewers. Every case has its own trigger, expectation, executable selector, action and limitation in [review500.json](review500.json).

## Where the 500 reviews went

| Area | IDs | Reviews | Previously failing scenarios | Final passes |
|---|---|---:|---:|---:|
| Input, identity, archive and folder boundaries | R001–R080 | 80 | 23 | 80 |
| Mainframe classification, utilities and custom knowledge | R081–R160 | 80 | 25 | 80 |
| COBOL semantics, generated Python, oracle and synthetic cases | R161–R240 | 80 | 22 | 80 |
| SME review, persistence, recovery and knowledge provenance | R241–R320 | 80 | 30 | 80 |
| Read-only connectors, provider, preflight and HTTP | R321–R400 | 80 | 28 | 80 |
| Source coverage, metrics, reports, bundles and orchestration | R401–R480 | 80 | 15 | 80 |
| Frontend file preservation and operating-system writer locks | R481–R500 | 20 | 3 | 20 |

## What changed

| Failure family | Corrective action |
|---|---|
| Lost or ambiguous source input | Preserve prototype-like upload filenames; reject duplicate archive entries, ambiguous XML members, malformed types/Unicode and cross-line Markdown attributes; inspect symlink roots before resolving them. |
| Misclassified mainframe content | Distinguish in-stream DD data and comments from executable declarations; preserve separate utility occurrences; validate and detach frozen knowledge. Recognition still requires an audited semantic adapter before conversion credit. |
| Incorrect COBOL interpretation | Block orphan fields, FILLER, incorrectly grouped level-77 items, repeated sections, invalid ownership, reserved statements and empty branches; bound parsing; preserve supported long predicates. |
| Unsafe or incorrect target execution | Reject unexpected generated definitions/annotations and caller-record aliasing. Direct hand-derived expectations, invalid records and mutation checks exercise the supported target contract. |
| Unreliable SME and knowledge evidence | Preserve zero/False corrections; bind returns to process/source/packet; validate recovered workbooks; retain each accepted review’s provenance rather than overwriting prior process knowledge. |
| Connector authority and malformed transport | Enforce read-only operations at the low-level MCP entrypoint; validate endpoint authorities, message identities, row shape, ambiguous headers and provider egress types; detach cached suggestion objects. |
| Inflated completion or overwritten evidence | Require job-integration evidence even without JCL rows; validate accepted report hashes; refuse existing report outputs; retain full spreadsheet text; show Unknown for empty metrics. |
| Incorrect job/bundle execution | Hash exact target bytes, reject symlinks/orphan versions/empty jobs, align return-code parsing, and safely quote continuation commands. |
| Cross-component regression during hardening | A new JSON depth guard initially rejected supported long source predicates. The final 256-level bound preserves the 192-comparison maximum plus evidence wrappers, with regression coverage for both accepted and excessive depth. |

## Repeat the review

Use the locked Python environment and install the pinned frontend development dependencies with `npm ci` in `frontend` for Node-based intake tests. Normal operators continue using the committed frontend without Node. Run from the repository:

```sh
PYTHONPATH=. python tools/review500.py
python -m unittest discover -s tests -v
python -m workbench.layout --workspace .
```

The harness requires exactly one test for each ID R001–R500, clears inherited workbench connection settings, records every outcome, and fails acceptance on skips, missing cases, failures or code changes. It writes logs and the receipt to a fresh private `.implementation/tmp/` directory. The consolidated JSON preserves selectors, source fingerprint and log hashes. Neither hashes nor fixture tests constitute an independent mainframe oracle.

## What the result establishes

The local implementation now passes these concrete safeguards and supported-behavior checks. Every supplied source line remains accountable, unsupported behavior remains visible, platform-specific omissions require verified replacements, and source/target/job/report evidence gates completion. The 500 cases include both successful behavior and expected rejection of unsupported or invalid input. A green rejection case means the guard works; it does not mean the rejected feature is implemented.

The converter still supports the bounded flat LINKAGE POC. General native I/O, SQL/CICS, packed/binary encoding, scheduler behavior, advanced control flow and custom utilities need audited adapters. Live Zowe/Db2/LLM credentials were not supplied. Native Windows, browser event interaction and PowerPoint rendering remain unverified. Source-derived tests share some extraction assumptions and do not establish observed legacy parity or zero defects. Actual human SME approval is still required once per process.

## Every numbered review

Each final result below is PASS. “Fixed” means a failing scenario was reproduced before its associated correction; “Verified” means this review found the expected existing behavior. Exact setup, expectation, action, selector and limits are in the matching JSON entry.

| ID | Scenario | Outcome |
|---|---|
| R001 | Identity nontext is validation error | Verified → PASS |
| R002 | Identity grammar prevents path injection | Verified → PASS |
| R003 | Identity length boundary | Verified → PASS |
| R004 | Identity windows device names | Verified → PASS |
| R005 | Json duplicate top level key | Verified → PASS |
| R006 | Json duplicate nested key | Verified → PASS |
| R007 | Json nonfinite numbers | Verified → PASS |
| R008 | Json invalid unicode bytes | Verified → PASS |
| R009 | Json excessive nesting | Fixed → PASS |
| R010 | Json text limit counts encoded bytes | Fixed → PASS |
| R011 | Json non document input | Fixed → PASS |
| R012 | Json lone surrogate | Fixed → PASS |
| R013 | Atomic nonfinite value preserves original | Verified → PASS |
| R014 | Zip nonbinary input | Fixed → PASS |
| R015 | Json exact byte limit | Verified → PASS |
| R016 | Json canonical evidence roundtrip | Verified → PASS |
| R017 | Path parent traversal | Verified → PASS |
| R018 | Path absolute and drive paths | Verified → PASS |
| R019 | Path backslash and unc | Verified → PASS |
| R020 | Path control characters | Verified → PASS |
| R021 | Path device basename with extension | Verified → PASS |
| R022 | Path ambiguous suffixes | Verified → PASS |
| R023 | Path symlink leaf | Verified → PASS |
| R024 | Path symlink parent | Verified → PASS |
| R025 | Path symlink root | Fixed → PASS |
| R026 | Path symlink above root | Fixed → PASS |
| R027 | Path root alias is not relative file | Fixed → PASS |
| R028 | Immutable write rejects overwrite | Verified → PASS |
| R029 | Immutable write rejects dangling link | Verified → PASS |
| R030 | Immutable write rejects parent link | Verified → PASS |
| R031 | Invalid evidence data leaves no partial file | Fixed → PASS |
| R032 | Atomic replace failure cleans temp | Fixed → PASS |
| R033 | Layout unknown root file | Verified → PASS |
| R034 | Layout tmp prefix not exemption | Verified → PASS |
| R035 | Layout workspace is regular directory | Verified → PASS |
| R036 | Layout invalid process identity | Verified → PASS |
| R037 | Layout process must be directory | Verified → PASS |
| R038 | Layout category must be directory | Verified → PASS |
| R039 | Layout input has designated filenames | Verified → PASS |
| R040 | Layout generated code and database placement | Verified → PASS |
| R041 | Layout no markdown per rule | Verified → PASS |
| R042 | Layout shared version filename | Verified → PASS |
| R043 | Layout knowledge entry types | Fixed → PASS |
| R044 | Layout nested symlink is reported without read | Verified → PASS |
| R045 | Intake row collection shape | Fixed → PASS |
| R046 | Intake individual row shape | Fixed → PASS |
| R047 | Intake row count boundary | Verified → PASS |
| R048 | Intake order type | Verified → PASS |
| R049 | Intake order range | Verified → PASS |
| R050 | Intake duplicate step order | Verified → PASS |
| R051 | Intake duplicate step name | Verified → PASS |
| R052 | Intake job order conflicts | Verified → PASS |
| R053 | Intake generated job method collision | Verified → PASS |
| R054 | Intake optional cells are text | Fixed → PASS |
| R055 | Intake unicode line separators | Fixed → PASS |
| R056 | Intake process name line separators | Fixed → PASS |
| R057 | Intake blank condition remains unknown | Fixed → PASS |
| R058 | Intake file lists preserve all names | Verified → PASS |
| R059 | Intake order not physical row order | Verified → PASS |
| R060 | Manifest duplicate attributes | Verified → PASS |
| R061 | Manifest blank name cannot capture next line | Fixed → PASS |
| R062 | Manifest table header contract | Verified → PASS |
| R063 | Manifest no steps | Verified → PASS |
| R064 | Manifest row width | Verified → PASS |
| R065 | Zip duplicate member identity | Fixed → PASS |
| R066 | Zip case insensitive xml guard | Fixed → PASS |
| R067 | Zip relationship xml guard | Fixed → PASS |
| R068 | Zip member path traversal | Verified → PASS |
| R069 | Zip member count limit | Verified → PASS |
| R070 | Zip total expansion limit | Verified → PASS |
| R071 | Zip individual expansion limit | Verified → PASS |
| R072 | Zip unsupported compression is validation error | Fixed → PASS |
| R073 | Xlsx formula intake rejected | Verified → PASS |
| R074 | Xlsx process name requires text | Fixed → PASS |
| R075 | Xlsx named sheet required | Verified → PASS |
| R076 | Xlsx forged dimensions | Verified → PASS |
| R077 | Xlsx duplicate cell coordinates | Verified → PASS |
| R078 | Xlsx cell row identity mismatch | Verified → PASS |
| R079 | Xlsx hidden job is accounted | Verified → PASS |
| R080 | Xlsx actual row bound | Verified → PASS |
| R081 | blank sequence debug line recognition | Fixed → PASS |
| R082 | blank sequence identification area is not code | Fixed → PASS |
| R083 | blank sequence comment does not supply rexx marker | Fixed → PASS |
| R084 | rexx marker inside literal is not source header | Fixed → PASS |
| R085 | real rexx header keeps line number | Verified → PASS |
| R086 | icetool select not confused with sql select | Fixed → PASS |
| R087 | icetool copy does not create copybook dependency | Fixed → PASS |
| R088 | national character copy dependency | Fixed → PASS |
| R089 | malformed copy operand does not truncate identity | Fixed → PASS |
| R090 | program copybook suffix conflict | Verified → PASS |
| R091 | embedded source in dd data does not reclassify job | Fixed → PASS |
| R092 | custom data delimiter hides inner job identity | Fixed → PASS |
| R093 | multiline block comment cannot supply program | Fixed → PASS |
| R094 | block comment ends before real sql | Verified → PASS |
| R095 | jcl delimiter does not start unclosed comment | Verified → PASS |
| R096 | empty export has explicit unknown evidence | Verified → PASS |
| R097 | evidence cap is declared without changing classification | Verified → PASS |
| R098 | nontext export fails with validation error | Fixed → PASS |
| R099 | mixed type path keys fail before sort | Fixed → PASS |
| R100 | comment copy statement does not create dependency | Verified → PASS |
| R101 | iefbr14 allocation risk remains blocking | Verified → PASS |
| R102 | sort site alias not product certification | Verified → PASS |
| R103 | tso variants preserve actual program identity | Verified → PASS |
| R104 | icegener fallback is not plain copy | Verified → PASS |
| R105 | iebcopy library member semantics retained | Verified → PASS |
| R106 | db2 driver alias is not read only certification | Verified → PASS |
| R107 | dd data embedded exec is not an invocation | Fixed → PASS |
| R108 | quoted custom delimiter resumes real invocations | Fixed → PASS |
| R109 | default dd star ends at next jcl statement | Verified → PASS |
| R110 | two unnamed steps remain two invocations | Fixed → PASS |
| R111 | separate procedure members keep own invocations | Fixed → PASS |
| R112 | duplicate named source steps are not silently merged | Fixed → PASS |
| R113 | manifest source exact match has single row | Verified → PASS |
| R114 | manifest match does not swallow second export occurrence | Fixed → PASS |
| R115 | jcl comment does not invoke program | Verified → PASS |
| R116 | symbolic program does not guess utility | Verified → PASS |
| R117 | procedure named like utility is not program invocation | Verified → PASS |
| R118 | finding risk edits do not mutate frozen snapshot | Fixed → PASS |
| R119 | application details are detached from snapshot | Fixed → PASS |
| R120 | malformed manifest program type is validation error | Fixed → PASS |
| R121 | impossible catalog date is rejected | Fixed → PASS |
| R122 | boolean schema is not integer schema | Verified → PASS |
| R123 | unknown execution field is rejected | Verified → PASS |
| R124 | conversion support claim is rejected | Verified → PASS |
| R125 | missing required evidence is rejected | Verified → PASS |
| R126 | empty utility risks are rejected | Verified → PASS |
| R127 | alias shadowing standard utility is rejected | Verified → PASS |
| R128 | duplicate utility identity is rejected | Verified → PASS |
| R129 | self alias is rejected | Verified → PASS |
| R130 | topic duplicate identity is rejected | Verified → PASS |
| R131 | missing classification category is rejected | Verified → PASS |
| R132 | duplicate category is rejected | Verified → PASS |
| R133 | identifier control character is rejected | Verified → PASS |
| R134 | nul in free text is rejected | Verified → PASS |
| R135 | oversized note is rejected | Verified → PASS |
| R136 | excessive note count is rejected | Verified → PASS |
| R137 | raw application size is bounded | Verified → PASS |
| R138 | application duplicate json keys are rejected | Verified → PASS |
| R139 | application directory is not json file | Verified → PASS |
| R140 | application parent symlink is rejected | Verified → PASS |
| R141 | application content requires provenance hash | Fixed → PASS |
| R142 | standard hash format is validated | Verified → PASS |
| R143 | snapshot tampering is detected | Verified → PASS |
| R144 | absent standard catalog is validation error | Fixed → PASS |
| R145 | bms definition does not establish business ui | Verified → PASS |
| R146 | db2 ddl does not establish sqlite equivalence | Verified → PASS |
| R147 | dclgen does not become supported layout | Verified → PASS |
| R148 | sort cards do not create sort adapter | Verified → PASS |
| R149 | cics resource definition does not replace transaction | Verified → PASS |
| R150 | scheduler definition does not establish calendar parity | Verified → PASS |
| R151 | rexx host commands remain unsupported | Verified → PASS |
| R152 | clist nested command semantics remain unsupported | Verified → PASS |
| R153 | pli procedure is not cobol translation | Verified → PASS |
| R154 | assembler section is not retired platform code | Verified → PASS |
| R155 | proc symbol expansion requires adapter | Verified → PASS |
| R156 | dd gdg lifecycle is not verified allocation | Verified → PASS |
| R157 | cond bypass is not manifest execute if | Verified → PASS |
| R158 | ims controller recognition does not supply ims adapter | Verified → PASS |
| R159 | uss command driver never executes collected text | Verified → PASS |
| R160 | custom owner fact never grants conversion support | Verified → PASS |
| R161 | orphan level05 field | Fixed → PASS |
| R162 | repeated linkage section | Fixed → PASS |
| R163 | filler field is not a named input | Fixed → PASS |
| R164 | filler group is not a using name | Fixed → PASS |
| R165 | level77 must not inherit group | Fixed → PASS |
| R166 | empty group has no layout | Fixed → PASS |
| R167 | program id outside identification | Fixed → PASS |
| R168 | group and field name collision | Fixed → PASS |
| R169 | reserved verb is not a paragraph | Fixed → PASS |
| R170 | terminal repeated period | Fixed → PASS |
| R171 | endif repeated period | Fixed → PASS |
| R172 | missing true body | Fixed → PASS |
| R173 | missing false body | Fixed → PASS |
| R174 | deep condition has named bound | Fixed → PASS |
| R175 | numeric literal parsing bound | Fixed → PASS |
| R176 | picture width parsing bound | Fixed → PASS |
| R177 | fixed continuation blocks | Verified → PASS |
| R178 | fixed column overflow blocks | Verified → PASS |
| R179 | duplicate else blocks | Verified → PASS |
| R180 | inline statements are not split by guess | Verified → PASS |
| R181 | perform requires control adapter | Verified → PASS |
| R182 | file section is not caller linkage | Verified → PASS |
| R183 | redefines aliasing stays unsupported | Verified → PASS |
| R184 | occurs does not become scalar | Verified → PASS |
| R185 | signed picture does not become unsigned | Verified → PASS |
| R186 | packed picture does not become display | Verified → PASS |
| R187 | overwidth comparison is not truncated | Verified → PASS |
| R188 | string ordering requires collation | Verified → PASS |
| R189 | unequal character layouts block | Verified → PASS |
| R190 | nested if does not flatten | Verified → PASS |
| R191 | boolean precedence matches hand expectation | Verified → PASS |
| R192 | left character literal padding | Verified → PASS |
| R193 | doubled quote is one character | Verified → PASS |
| R194 | comment marker inside literal | Verified → PASS |
| R195 | numeric field comparison widths | Verified → PASS |
| R196 | later condition reads prior write | Verified → PASS |
| R197 | assignment order in one arm | Verified → PASS |
| R198 | absent else preserves false record | Verified → PASS |
| R199 | explicit continue preserves true record | Verified → PASS |
| R200 | eighteen digit integer exactness | Verified → PASS |
| R201 | outside domain condition has unreachable gap | Verified → PASS |
| R202 | stop run is supported terminal | Verified → PASS |
| R203 | lowercase paragraph case insensitivity | Fixed → PASS |
| R204 | string literal case is preserved | Verified → PASS |
| R205 | copybook line provenance | Verified → PASS |
| R206 | copybook change invalidates semantic hash | Verified → PASS |
| R207 | self comparison does not invent false witness | Verified → PASS |
| R208 | literal only comparison is explicit | Verified → PASS |
| R209 | bool is not numeric input | Verified → PASS |
| R210 | pairs list is not record object | Verified → PASS |
| R211 | dict subclass cannot execute get hook | Verified → PASS |
| R212 | equal size wrong field set | Verified → PASS |
| R213 | null integer input | Verified → PASS |
| R214 | exact fixed width includes trailing space | Verified → PASS |
| R215 | target return record is independent | Verified → PASS |
| R216 | prepared target has no cross call state | Verified → PASS |
| R217 | oracle does not cache mutable results | Verified → PASS |
| R218 | unknown contract version blocks all paths | Fixed → PASS |
| R219 | boolean contract version is not version one | Fixed → PASS |
| R220 | nested target function is rejected | Fixed → PASS |
| R221 | eager target annotation is rejected | Fixed → PASS |
| R222 | forbidden import is rejected | Verified → PASS |
| R223 | comprehension iteration is rejected | Verified → PASS |
| R224 | attribute escape is rejected | Verified → PASS |
| R225 | direct caller assignment is rejected | Verified → PASS |
| R226 | alias cannot bypass caller write guard | Fixed → PASS |
| R227 | fixture budget bound is strict | Verified → PASS |
| R228 | seed replay is byte identical | Verified → PASS |
| R229 | ledger key order cannot change cases | Verified → PASS |
| R230 | cross group matching fixtures | Verified → PASS |
| R231 | budget exhaustion retains obligations | Verified → PASS |
| R232 | forged expected output is rejected | Verified → PASS |
| R233 | forged coverage credit is rejected | Verified → PASS |
| R234 | stale source suite is rejected | Verified → PASS |
| R235 | every input guard has rejecting witness | Verified → PASS |
| R236 | each literal effect is mutated | Verified → PASS |
| R237 | overwritten effect has adversarial gap | Verified → PASS |
| R238 | runtime target error is failed evidence | Verified → PASS |
| R239 | checkpoint is retained per case | Verified → PASS |
| R240 | oracle does not call target generation | Verified → PASS |
| R241 | Blank answer stays unanswered | Verified → PASS |
| R242 | Zero correction is retained | Fixed → PASS |
| R243 | False correction is retained | Fixed → PASS |
| R244 | Numeric zero answer is not blank | Fixed → PASS |
| R245 | Boolean answer is not blank | Fixed → PASS |
| R246 | Numeric reviewer is not silently replaced | Fixed → PASS |
| R247 | Empty global reviewer rejected | Verified → PASS |
| R248 | Oversized reviewer rejected | Verified → PASS |
| R249 | Formula answer rejected | Verified → PASS |
| R250 | Formula correction rejected | Verified → PASS |
| R251 | Frozen context edit rejected | Verified → PASS |
| R252 | Packet metadata process edit rejected | Verified → PASS |
| R253 | Repeated question id rejected | Verified → PASS |
| R254 | Missing question row rejected | Verified → PASS |
| R255 | Extra hidden question rejected | Verified → PASS |
| R256 | Extra hidden sheet rejected | Verified → PASS |
| R257 | Evidence reference edit rejected | Verified → PASS |
| R258 | Rule category edit rejected | Verified → PASS |
| R259 | Invalid answer vocabulary rejected | Verified → PASS |
| R260 | No answer correction preserved | Verified → PASS |
| R261 | Uncertainty preserved | Verified → PASS |
| R262 | Oversized correction rejected | Verified → PASS |
| R263 | Merged answer and correction rejected | Fixed → PASS |
| R264 | Changed packet payload with old hash rejected | Verified → PASS |
| R265 | Reordered rows keep identity binding | Verified → PASS |
| R266 | Duplicate packet rule ids rejected before publication | Fixed → PASS |
| R267 | Rule id colliding with global question rejected | Fixed → PASS |
| R268 | Recovery rejects forged packet self hash | Fixed → PASS |
| R269 | Recovery rejects missing companion | Fixed → PASS |
| R270 | Recovery rejects answered issued workbook | Fixed → PASS |
| R271 | Double packet issue keeps original fingerprint | Verified → PASS |
| R272 | Return requires issued packet | Verified → PASS |
| R273 | Return packet fingerprint must match | Fixed → PASS |
| R274 | Return source snapshot must match | Fixed → PASS |
| R275 | Return reviewer required at commit | Fixed → PASS |
| R276 | Return byte fingerprint required | Fixed → PASS |
| R277 | Double return keeps first answer | Verified → PASS |
| R278 | Return transaction rolls back failed process update | Verified → PASS |
| R279 | Document save cannot reset quota columns | Verified → PASS |
| R280 | Identical snapshots are deduplicated | Verified → PASS |
| R281 | Changed snapshots preserve history | Verified → PASS |
| R282 | Completion rejects missing inspection | Fixed → PASS |
| R283 | Completion rejects unpinned report | Fixed → PASS |
| R284 | Completion rejects stale nonreporting stage | Fixed → PASS |
| R285 | Completion snapshot and event rollback together | Verified → PASS |
| R286 | Completion keeps blocker status | Verified → PASS |
| R287 | Asset identity collision rejected | Fixed → PASS |
| R288 | Asset batch rolls back prior insert on collision | Fixed → PASS |
| R289 | Portfolio excludes demo membership | Verified → PASS |
| R290 | Durable controls do not drop cancellation | Verified → PASS |
| R291 | Changed source before return does not consume quota | Fixed → PASS |
| R292 | Added frozen source file cannot disappear from accounting | Fixed → PASS |
| R293 | Deleted source file remains integrity failure | Verified → PASS |
| R294 | Foreign packet process identity cannot consume return | Fixed → PASS |
| R295 | Pause checkpoint keeps durable pause | Verified → PASS |
| R296 | Cancel checkpoint preserves blocker | Verified → PASS |
| R297 | Retry bound stops after three transient failures | Verified → PASS |
| R298 | Permission error is not retried | Verified → PASS |
| R299 | Stage success only clears its failure | Verified → PASS |
| R300 | Preserved return conflict does not consume quota | Verified → PASS |
| R301 | Return write crash replay consumes only once | Verified → PASS |
| R302 | Registered artifact cannot be rebaselined | Verified → PASS |
| R303 | Paused return is not imported | Verified → PASS |
| R304 | Completed controls cannot rewrite terminal evidence | Verified → PASS |
| R305 | Restart interrupted analysis preserves issued packet | Verified → PASS |
| R306 | Unconsumed hypothetical answers not published | Fixed → PASS |
| R307 | No answer never becomes approved knowledge | Verified → PASS |
| R308 | Uncertain answer never becomes approved knowledge | Verified → PASS |
| R309 | Blank answer never becomes approved knowledge | Verified → PASS |
| R310 | Yes with correction never becomes approved knowledge | Verified → PASS |
| R311 | Yes rule keeps reviewer packet and source provenance | Verified → PASS |
| R312 | Same source second process keeps first review provenance | Fixed → PASS |
| R313 | Knowledge replay does not duplicate records | Verified → PASS |
| R314 | Changed inmemory answer not published | Fixed → PASS |
| R315 | Changed rule statement not published | Fixed → PASS |
| R316 | Changed accepted return not published | Fixed → PASS |
| R317 | Records projection matches canonical database | Verified → PASS |
| R318 | Index symlink cannot overwrite unrelated file | Fixed → PASS |
| R319 | Knowledge projection failure is replayable | Verified → PASS |
| R320 | Conflicting existing knowledge is not overwritten | Fixed → PASS |
| R321 | Endpoint rejects nontext configuration | Fixed → PASS |
| R322 | Endpoint rejects parser stripped controls | Fixed → PASS |
| R323 | Endpoint rejects unbalanced ipv6 as validation | Fixed → PASS |
| R324 | Endpoint rejects out of range port | Fixed → PASS |
| R325 | Endpoint rejects embedded credentials | Verified → PASS |
| R326 | Endpoint limits plain http to loopback | Verified → PASS |
| R327 | Endpoint rejects client only fragment | Verified → PASS |
| R328 | Redirects never forward bearer credentials | Verified → PASS |
| R329 | Remote response byte limit is enforced | Verified → PASS |
| R330 | Remote html is not interpreted as json | Verified → PASS |
| R331 | Transport failures redact private endpoint details | Verified → PASS |
| R332 | Notification cannot open response stream | Verified → PASS |
| R333 | Sse progress and multiline result | Verified → PASS |
| R334 | Sse boolean identity cannot match integer request | Fixed → PASS |
| R335 | Sse rejects unsolicited execution request | Verified → PASS |
| R336 | Sse stream bound includes comment bytes | Verified → PASS |
| R337 | Sql rejects unlisted mutating operation | Verified → PASS |
| R338 | Sql catalog filter stays bound parameter | Verified → PASS |
| R339 | Sql sampling identifier injection is denied | Verified → PASS |
| R340 | Sql boolean cannot bypass integer row limit | Verified → PASS |
| R341 | Sql unknown arguments do not expand capability | Verified → PASS |
| R342 | Sql false schema does not widen discovery | Fixed → PASS |
| R343 | Sql column cursor requires integer ordinal | Verified → PASS |
| R344 | Sql description binds names and fetches sentinel | Verified → PASS |
| R345 | Sql sample is bounded and has no sentinel | Verified → PASS |
| R346 | Mcp requires negotiation before tool calls | Verified → PASS |
| R347 | Mcp rejects boolean response identity | Verified → PASS |
| R348 | Mcp unsupported negotiated version stops initialization | Verified → PASS |
| R349 | Mcp requires advertised tools capability | Verified → PASS |
| R350 | Mcp notification response cannot inject result | Verified → PASS |
| R351 | Mcp tool listing entry must have text name | Verified → PASS |
| R352 | Mcp tools cursor cycle is rejected | Verified → PASS |
| R353 | Mcp tools pagination has finite page budget | Verified → PASS |
| R354 | Mcp schema only server is not complete discovery | Verified → PASS |
| R355 | Mcp session header rejects control characters | Verified → PASS |
| R356 | Mcp session cannot change after negotiation | Verified → PASS |
| R357 | Mcp structured content requires object | Fixed → PASS |
| R358 | Mcp malformed content is named validation | Fixed → PASS |
| R359 | Mcp unpaired unicode text is named validation | Fixed → PASS |
| R360 | Mcp advertised write tool still cannot run | Fixed → PASS |
| R361 | Discovery page budget retains resume cursor | Verified → PASS |
| R362 | Discovery byte budget discards unaccepted page | Verified → PASS |
| R363 | Discovery rejects scalar rows | Verified → PASS |
| R364 | Discovery repeated cursor does not duplicate rows | Verified → PASS |
| R365 | Discovery second page failure preserves first | Verified → PASS |
| R366 | Discovery restores client timeout after deadline | Verified → PASS |
| R367 | Discovery time budget requires numeric duration | Fixed → PASS |
| R368 | Discovery malformed unicode page stays partial | Fixed → PASS |
| R369 | Zowe nontext profile is named validation | Fixed → PASS |
| R370 | Zowe dataset cannot inject option | Verified → PASS |
| R371 | Zowe member reads require explicit dataset | Verified → PASS |
| R372 | Zowe write operation is not dispatchable | Verified → PASS |
| R373 | Zowe subprocess uses argv and filtered environment | Verified → PASS |
| R374 | Command timeout kills and reaps child | Verified → PASS |
| R375 | Command output overflow stops before decode | Verified → PASS |
| R376 | Provider truthy string does not approve egress | Fixed → PASS |
| R377 | Provider malformed source unicode never transfers | Fixed → PASS |
| R378 | Provider missing message is named validation | Verified → PASS |
| R379 | Provider invalid output unicode is named validation | Fixed → PASS |
| R380 | Provider cannot add approval authority field | Verified → PASS |
| R381 | Provider tool call output is not valid analysis | Fixed → PASS |
| R382 | Provider boolean usage is not token accounting | Verified → PASS |
| R383 | Provider caller mutation does not poison cache | Fixed → PASS |
| R384 | Provider cache hit has no new request usage | Verified → PASS |
| R385 | Provider excerpt limit precedes network | Verified → PASS |
| R386 | Gateway requires bearer authentication | Verified → PASS |
| R387 | Gateway rejects duplicate authentication headers | Fixed → PASS |
| R388 | Gateway rejects transfer encoding content length conflict | Fixed → PASS |
| R389 | Gateway requires json content type | Fixed → PASS |
| R390 | Gateway driver requests read only with finite timeouts | Verified → PASS |
| R391 | Gateway mismatched row width cannot drop values | Fixed → PASS |
| R392 | Gateway oversize encoded envelope returns safe error | Verified → PASS |
| R393 | Gateway nonfinite database value is named validation | Fixed → PASS |
| R394 | Gateway unknown protocol does not execute reads | Verified → PASS |
| R395 | Preflight invalid port cannot be unverified valid | Fixed → PASS |
| R396 | Preflight nontext dataset hint is diagnostic | Fixed → PASS |
| R397 | Preflight model identifier must be text | Fixed → PASS |
| R398 | Api duplicate host does not pass origin gate | Fixed → PASS |
| R399 | Api duplicate json keys rejected before intake | Verified → PASS |
| R400 | Api denied mutation has security response headers | Fixed → PASS |
| R401 | physical source line order is exact | Verified → PASS |
| R402 | each source line hash covers unmodified text | Verified → PASS |
| R403 | all source rows have disposition and reason | Verified → PASS |
| R404 | rule span has one semantic unit | Verified → PASS |
| R405 | target spans are bounded by actual file | Verified → PASS |
| R406 | terminal replacement names bounded adapter | Verified → PASS |
| R407 | applicable denominator excludes nonexecutables | Verified → PASS |
| R408 | missing manifest revokes all verified credit | Verified → PASS |
| R409 | source tamper preserves frozen original rows | Verified → PASS |
| R410 | missing source preserves frozen original rows | Verified → PASS |
| R411 | analysis tamper blocks replay | Verified → PASS |
| R412 | expected evidence tamper revokes program | Verified → PASS |
| R413 | actual evidence tamper revokes program | Verified → PASS |
| R414 | missing target copy revokes program | Verified → PASS |
| R415 | database hash tamper blocks target replay | Verified → PASS |
| R416 | cancelled evidence is not reexecuted | Verified → PASS |
| R417 | correction prevents credit despite yes | Verified → PASS |
| R418 | missing job comparison blocks completion without jcl | Fixed → PASS |
| R419 | forged job comparison blocks completion without jcl | Fixed → PASS |
| R420 | job order unconfirmed blocks completion without jcl | Fixed → PASS |
| R421 | source symlink is rejected even with matching bytes | Verified → PASS |
| R422 | formula escape does not truncate excel limit | Fixed → PASS |
| R423 | xml control text chunks are reversible | Verified → PASS |
| R424 | html escapes original markup | Verified → PASS |
| R425 | csv formula safety and exact canonical json | Verified → PASS |
| R426 | known rule metric uses extracted rule denominator | Verified → PASS |
| R427 | unknown interface metrics are none | Verified → PASS |
| R428 | workbench ui is excluded from business replacements | Verified → PASS |
| R429 | matching cases revoked with target corruption | Verified → PASS |
| R430 | shared target loc is deduplicated | Verified → PASS |
| R431 | portfolio demo memberships are excluded | Verified → PASS |
| R432 | portfolio shared versions keep two memberships | Verified → PASS |
| R433 | portfolio changed hash is distinct version | Verified → PASS |
| R434 | scope union selects version if any membership selects | Verified → PASS |
| R435 | discovered out of scope version is not selected | Verified → PASS |
| R436 | report projection does not mutate live status | Verified → PASS |
| R437 | report projection does not double count completed | Verified → PASS |
| R438 | report projection removes revoked completion | Verified → PASS |
| R439 | report inspection hashes all eight outputs | Verified → PASS |
| R440 | management deck has six editable bounded slides | Verified → PASS |
| R441 | management deck does not render none percent | Fixed → PASS |
| R442 | report output refuses existing frozen artifacts | Fixed → PASS |
| R443 | coverage output refuses existing artifacts | Fixed → PASS |
| R444 | metrics csv matches json values | Verified → PASS |
| R445 | metrics workbook matches json values | Verified → PASS |
| R446 | manifest baseline is never inferred | Verified → PASS |
| R447 | start requires exact manifest bytes | Verified → PASS |
| R448 | continuation shell quotes sensitive workspace | Fixed → PASS |
| R449 | summary separates packet from reports | Verified → PASS |
| R450 | waiting summary requires actual human return | Verified → PASS |
| R451 | wait timeout bounds reject nonfinite values | Verified → PASS |
| R452 | watch requires reviewer before worker launch | Verified → PASS |
| R453 | wait stops at waiting sme without answers | Verified → PASS |
| R454 | wait preserves terminal states | Verified → PASS |
| R455 | bounded wait returns timeout without state mutation | Verified → PASS |
| R456 | import idempotency requires same return and reviewer | Verified → PASS |
| R457 | import refuses second workbook | Verified → PASS |
| R458 | import refuses changed reviewer | Verified → PASS |
| R459 | bundle is reused byte for byte | Verified → PASS |
| R460 | bundle entries match frozen sources and report | Verified → PASS |
| R461 | bundle refuses nonterminal process | Verified → PASS |
| R462 | bundle requires inspected report | Verified → PASS |
| R463 | bundle refuses missing registered inspection hashes | Fixed → PASS |
| R464 | bundle refuses orphaned report hash entry | Fixed → PASS |
| R465 | bundle rejects modified existing zip | Verified → PASS |
| R466 | job baseline matches independent reference | Verified → PASS |
| R467 | job result explicitly excludes dataset and mainframe parity | Verified → PASS |
| R468 | untrusted job code is rejected before exec | Verified → PASS |
| R469 | target bytes are hashed without newline normalization | Fixed → PASS |
| R470 | target symlink is not accepted as frozen evidence | Fixed → PASS |
| R471 | unresolved program blocks integration credit | Verified → PASS |
| R472 | different field sets require explicit mapping | Verified → PASS |
| R473 | different field widths require mapping | Verified → PASS |
| R474 | target version must be lowercase sha256 | Verified → PASS |
| R475 | rc equal executes at zero | Verified → PASS |
| R476 | rc greater skips at zero | Verified → PASS |
| R477 | condition whitespace is supported consistently | Fixed → PASS |
| R478 | empty job sequence never receives integration credit | Fixed → PASS |
| R479 | orphan target version is refused | Fixed → PASS |
| R480 | job steps preserve order and record state | Verified → PASS |
| R481 | A selected __proto__ file must survive upload serialization. | Fixed → PASS |
| R482 | Two same-named selected files must not overwrite one another. | Verified → PASS |
| R483 | Object built-in names must not collide with export bookkeeping. | Verified → PASS |
| R484 | Invalid UTF-8 must not silently change source bytes to replacement text. | Verified → PASS |
| R485 | Text intake must preserve BOM, significant spaces and CRLF evidence. | Verified → PASS |
| R486 | More than 200 selections must be rejected before file reads begin. | Verified → PASS |
| R487 | An oversized selected export must fail without reading every member. | Verified → PASS |
| R488 | One oversized member must fail before allocating its byte buffer. | Verified → PASS |
| R489 | A failure after a valid first member must reject the whole selection. | Verified → PASS |
| R490 | Clearing an upload must not invent a source file or keep stale content. | Verified → PASS |
| R491 | A file read error must surface a source-specific actionable message. | Verified → PASS |
| R492 | A second coordinator lock must not acquire the same workspace. | Verified → PASS |
| R493 | An abruptly terminated writer must not leave a permanent stale lock. | Verified → PASS |
| R494 | Workspace locking must not serialize unrelated process workspaces. | Verified → PASS |
| R495 | The lock boundary must reject a root that redirects through a symlink. | Fixed → PASS |
| R496 | A redirected state directory must not create locks outside the workspace. | Verified → PASS |
| R497 | The lock file itself must not point to another file. | Verified → PASS |
| R498 | A safe-looking child path must not hide a symlink in a parent. | Fixed → PASS |
| R499 | A file named .migration must cause failure and retain its bytes. | Verified → PASS |
| R500 | A rejected OS lock must close its descriptor before returning failure. | Verified → PASS |
