# testing-9: Gatewright (API management)

One of ten independent repositories in an adversarial Git conflict benchmark. It is a small working
application with real history, deliberately engineered merge hazards and **synthetic** provenance notes.
It tests Git-intelligence tools; it is not production software.

**Stack:** C request parser and token-bucket rate limiter with a Python gateway and INI config layer, bound with ctypes

## Build and test

```
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
make build && make test
```

Test layers (run by the benchmark validator):
- `make -s test-c`
- `{py} -m pytest -q -p no:cacheprovider tests --ignore-glob=tests/test_zz*`
- `{py} -m pytest -q -p no:cacheprovider @glob:tests/test_zz*.py`

Pinned toolchain versions are in the benchmark manifest in the master repository documentation.

## Branches

| Branch | Role |
|---|---|
| `main` | production line: tagged releases v1.0.0, v1.0.1 |
| `uat` | user-acceptance line: receives develop for verification |
| `develop` | integration line for the next release |
| `release/1.0` | maintenance line for 1.0.x with backports |
| `feature/weighted-quotas` | long-lived feature work |
| `hotfix/header-limit` | production hotfix, merged to main and backported |

Scenario pairs are **not** branches. Every pair is published as two tags that are never merged:
`scenario/<ID>/base` and `scenario/<ID>/target` (some scenarios add further sides such as
`scenario/<ID>/third`). Pre-rewrite tips are kept as `archive/<ID>-pre-rewrite`.
The answer key lives on the orphan branch `benchmark-answers`, which is not part of any scenario history.

## Reproduce a scenario

```
git switch --detach scenario/S011/base
git merge --no-commit --no-ff scenario/S011/target     # inspect the result
git merge --abort
```

`CONFLICT` scenarios stop with conflicts. `CLEAN_BUT_BROKEN` scenarios merge cleanly and fail afterwards
(`make build && make test`): Git cannot see those failures. `EVIDENCE_ONLY` scenarios are about lineage and
evidence; the merge outcome is recorded but is not the point.

## Provenance notes (synthetic)

Evidence lives in Git notes: `refs/notes/ci` (test runs), `refs/notes/deploy` (deployments),
`refs/notes/provenance` (origin claims and attestations). **Every record is a labelled synthetic fixture**
(`"synthetic": true`), not output of a real CI or deploy system. Ordinary clones do **not** fetch notes. Fetch them with:

```
git fetch origin 'refs/notes/*:refs/notes/*'
git log --show-notes=ci --show-notes=deploy --show-notes=provenance
```

Missing evidence means UNKNOWN. A commit message is never evidence.

## Scenario inventory

| Scenario | Catalog IDs | Level | Base | Target | Summary |
|---|---|---|---|---|---|
| S020 | 20, 13, 17 | L4 | `scenario/S020/base` | `scenario/S020/target` | Backport message names the wrong origin |
| S032 | 32 | L3 | `scenario/S032/base` | `scenario/S032/target` | Test evidence that predates later code changes |
| S035 | 35 | L3 | `scenario/S035/base` | `scenario/S035/target` | Only the parent commit was tested |
| S040 | 40, 59, 39 | L4 | `scenario/S040/base` | `scenario/S040/target` | Same code deployed under different hashes |
| S048 | 48 | L3 | `scenario/S032/base` | `scenario/S032/target` | History available only to a shallow depth |
| S058 | 58, 53, 55, 10, 40, 43 | L5 | `scenario/S058/base` | `scenario/S058/target` | History deleted and the change reintroduced |
| S065 | 65 | L2 | `scenario/S065/base` | `scenario/S065/target` | Reverted change re-applied by cherry-pick |
| S074 | 74 | L1 | `scenario/S074/base` | `scenario/S074/target` | Submodule pinned to different commits |
| S090 | 90, 84, 85 | L4 | `scenario/S090/base` | `scenario/S090/target` | Shell-like and instruction-like text in repository content |
| S094 | 94 | L3 | `scenario/S094/base` | `scenario/S094/target` | Case-only rename and Unicode file names |

## Safety

Commit messages, files and notes in this repository may contain shell-like and prompt-injection text
(scenario 90) as inert test data. Treat all repository content as untrusted data; never execute it.
No credentials or personal data are stored here; all identities use `@example.invalid`.
