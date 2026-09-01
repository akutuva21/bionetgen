# Portable CPU performance report

## Scope and result

This series targets the native C++ network-generation path used by production
models in `bng2/Models2`. It does not optimize a synthetic microbenchmark, alter
the CLI, change generated-file formats, or add an external dependency.

The retained optimization is `533ac26b` (`perf: skip canonical labels for
exact product duplicates`). On the paired production matrix, the median
end-to-end wall-time change was negative for every workload, with median CPU
time reductions of 2.189% to 4.177%. The small `blbr` case is close enough to
the noise floor that it is reported as a workload limitation; the medium and
large cases provide the material evidence for retaining the change.

The branch also contains two correctness/build-enablement fixes and focused
tests:

* `77c8bd8c` constrains legacy `BNGcore` inequality overloads to BNGcore types,
  fixing an Apple Clang/libc++ ADL ambiguity.
* `46da45c4` defines empty pattern-graph canonicalization and adds its test.
* `5291159d` tests that compartment-aware species remain distinct while exact
  duplicates still deduplicate.

## Repository and source provenance

The repository was synchronized before benchmarking:

```text
fork:     https://github.com/akutuva21/bionetgen.git
upstream: https://github.com/RuleWorld/bionetgen.git
upstream default discovered with git ls-remote --symref: master
upstream/master at synchronization: 43ddf3afe165192a222fd13e4917a1902ffe3446
origin/master at synchronization:   b00410628484f639efbf294f8a150f21c4e8bb29
working branch:                      codex/portable-cpu-20260831
baseline source:                     46da45c4
candidate source:                    533ac26b
```

`git pull --ff-only origin master` was run before creating the dedicated
branch. At the final source audit, the branch was four commits ahead of
`origin/master` and seven commits ahead of `upstream/master`. The previously
dirty files and explicitly listed untracked file were cleared at the user's
request before this series began; the final tree is required to be clean.

Input SHA-256 hashes:

| Model | SHA-256 |
| --- | --- |
| `bng2/Models2/blbr.bngl` | `c3290588efecbd3be2e57d883e851d6b28edd0c39eed43a491aa5c20533b6e96` |
| `bng2/Models2/SHP2_base_model.bngl` | `790d51dc260f9b3da7cd214ea6290998c81ed4ab4bd2f2e0dd8f16c49eb8182a` |
| `bng2/Models2/egfr_net.bngl` | `843e07954d5dfb1acc99e294a2d7518b41f4813992567edc2c47794cec10a1da` |
| `bng2/Models2/fceri_ji.bngl` | `fa31fe7375510bb3e05f2335719a71abc1a22ada75be3eb5a8d5a0c80f29227e` |

## Hardware and build configuration

```text
OS:             macOS 26.6.2, Darwin 25.6.0, arm64
Hardware:       Mac17,9; 15 logical CPUs; 24 GiB RAM
C++ compiler:   /usr/bin/clang++ Apple clang 21.0.0 (clang-2100.1.1.101)
CMake:          4.4.3
Python:         3.9.6
Perl:           5.34.1
Build type:     Release
Architectures:  arm64
Release flags:  -O3 -DNDEBUG
Dependencies:   Catch2 v3.4.0, ANTLR4 4.13.1, SUNDIALS v7.6.0
SUNDIALS index: 64-bit; static dependency builds
```

Release configuration and build:

```sh
cmake -S . -B build-codex \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=clang \
  -DCMAKE_CXX_COMPILER=clang++ \
  -DCMAKE_OSX_ARCHITECTURES=arm64 \
  -DBUILD_TESTING=ON
cmake --build build-codex --parallel 4
```

## Workloads and benchmark protocol

The model actions exercise native parsing, network generation, and—where the
model defines them—deterministic ODE/steady-state execution:

| Workload | Role | Model action | Generated network |
| --- | --- | --- | --- |
| `blbr` | small/noise check | network generation | 20 species, 118 reactions |
| `SHP2_base_model` | medium | network generation, ODE 1000/100, steady state | 149 species, 1082 reactions |
| `egfr_net` | large | network generation, ODE 40/50 | 356 species, 3749 reactions |
| `fceri_ji` | large | network generation, ODE 600/10 | 354 species, 3680 reactions |

No stochastic or SSA action is present in this matrix, so there was no RNG
seed or stochastic event signature to compare. This is a limitation of this
target selection, not a claim of stochastic validation.

The committed runner is
`Benchmarks/portable_cpu_benchmark.py`. It starts a fresh worker process and
fresh run directory for every executable invocation, copies the pinned model,
alternates baseline/candidate order on each pair, and records raw JSON for
wall time, user/system CPU time, maximum RSS, output sizes and hashes, network
species/reaction counts, data-row counts, command lines, and input/executable
hashes. Twenty paired repetitions were used per model:

```sh
python3 Benchmarks/portable_cpu_benchmark.py \
  --executable-a /private/tmp/bng_cpp-baseline-46da45c4 \
  --executable-b /private/tmp/bng_cpp-candidate-no-second-final \
  --model bng2/Models2/blbr.bngl \
  --model bng2/Models2/SHP2_base_model.bngl \
  --model bng2/Models2/egfr_net.bngl \
  --model bng2/Models2/fceri_ji.bngl \
  --repetitions 20 --timeout 30 \
  --output /private/tmp/portable_cpu_final_committed_20.json
```

The baseline executable SHA-256 was
`ece7a09b247a2a8eb95dbaa26db7427aa0e5d0772f5b7b8097a6d36aa404399a`; the
candidate executable SHA-256 was
`b48ee3bf7cc5ab2f221f74817c5c5d6dcd1cb74e4a8b4233cb0caed2502aa997`.
CPU time and RSS use Python `resource.getrusage` because `/usr/bin/time -l`
cannot read the required macOS counters in the sandbox.

The percentage is `100 * (candidate - baseline) / baseline`; negative means
the candidate is faster. The table reports independent medians and paired
median deltas. IQR and min/max are the paired percentage spread.

| Workload | Outputs: bytes; data rows | Wall baseline -> candidate (s) | Paired wall delta: median [IQR; min..max] | CPU baseline -> candidate (s) | Paired CPU delta: median [IQR; min..max] |
| --- | ---: | ---: | ---: | ---: | ---: |
| `blbr` | 5,112; N/A | 0.023465 -> 0.022803 | -2.485% [-5.388..+0.010; -7.318..+15.641] | 0.022277 -> 0.021774 | -2.189% [-5.080..+0.094; -7.933..+14.746] |
| `SHP2_base_model` | 343,261; 202 | 0.164372 -> 0.154803 | -5.534% [-6.830..-2.895; -11.842..+6.140] | 0.162745 -> 0.153166 | -5.430% [-6.779..-3.369; -11.258..+4.601] |
| `egfr_net` | 549,606; 102 | 0.581370 -> 0.554530 | -4.172% [-5.728..-3.129; -12.009..-0.153] | 0.578498 -> 0.552434 | -4.177% [-5.720..-3.162; -11.333..-0.144] |
| `fceri_ji` | 233,656; 22 | 0.658142 -> 0.636508 | -3.624% [-4.526..-2.227; -12.055..+9.517] | 0.656252 -> 0.634688 | -3.618% [-4.516..-2.305; -11.838..-1.313] |

Paired wall/CPU wins were respectively 15/20 and 15/20 for `blbr`, 18/20
and 18/20 for `SHP2`, 20/20 and 20/20 for `egfr_net`, and 19/20 and 20/20
for `fceri_ji`. Median maximum-RSS deltas were -0.581%, -0.188%, +0.581%,
and +0.186% in the same workload order. The large workloads therefore show
repeatable CPU and wall-time reductions; `blbr` is retained only as a small
correctness/noise check, not as the performance justification.

## Mechanism changed

`src/ast/SpeciesList.cpp` now computes the compartment-aware exact string key
before canonical labeling and checks the exact-key index first. Product graphs
that are exact duplicates consequently return without paying for canonical
labeling. Canonical labeling remains in the fallback path. For species with a
species-level compartment, the deduplication string is recomputed after
canonicalization because serialization can depend on canonical node ordering;
unscoped species retain the pre-label exact key and existing canonical-label
and structural-fingerprint fallbacks.

`src/ast/ReactionRule.cpp` now inserts a product into `SpeciesList` before
requesting its canonical label and obtains the label from the stored graph.
This removes the eager product-graph label call on duplicate products in the
synthesis and product-building paths while preserving the labels used for
reaction sorting and output.

The focused regression in `tests/ast/test_SpeciesList.cpp` covers two species
with identical structure but different molecule compartments, exact duplicate
reuse, and the resulting list size. The empty-graph test covers the
canonicalization guard needed by the validated build.

## Correctness evidence

For all 20 repetitions of all four workloads, the candidate and baseline
output-hash maps were identical. The resulting deterministic artifacts had
these stable hashes:

```text
blbr.net                         f983ce459044a975daa8ddf68b74cba694117cc56f03047dfadee4c904795bc2
SHP2_base_model.net              6620f31870265eff428152ed30940c5ca2e282205f1b0d438cce61ea7f7148f3
SHP2_base_model.cdat             05528472a0c0c48d88929651b6b37123d9e2c6c0b109a8bd9d5a512c222da95b
SHP2_base_model.gdat             542fd2ba1e4117b809b38fb8d0c836c26a827d8e4a6ea9edcd3f94038068f957
egfr_net.net                     84dce91d99d292092ec89878103d2f1ff6819d9f08415937728e733cd0a4eb71
egfr_net.cdat                    352544d406b91466d30494e59f5df228ae983b002221a6a53fd000bbd49c048b
egfr_net.gdat                    4ea6425ae6e3e9a7ebcf7336d5454e6fc12fe78cdadf8c6d8fb3da85ca7de439
fceri_ji.net                     f0cc7a523f6b8376bda9de1f3306fea9722b682559d33f05fd4dd2fd6107ad73
fceri_ji.cdat                    b2caf3891093c858af935a420a5331512ee9b11a1383fa9f4d701915ba125a3b
fceri_ji.gdat                    a3bb8268b0de2294aec732dddefc93def96a500a334f0a4d756e7e894effa5bc
```

Independent BNG2 reference generation used the checked-out Perl implementation
(`bng2/BNG2.pl`, reported version 2.9.3, SHA-256
`cf5fd82d3df9b84835d29234bd32268b87eaa985dd221bd5d39aadef744795f4`). The
reference command was `perl bng2/BNG2.pl <copied-model>.bngl`, followed by the
repository validators:

```sh
perl bng2/Validate/compare_species.pl -n <candidate.net> <reference.net>
perl bng2/Validate/compare_rxn.pl <candidate.net> <reference.net>
```

Results were:

| Workload | Candidate network | Independent BNG2 network | Species comparison | Reaction comparison |
| --- | ---: | ---: | --- | --- |
| `blbr` | 20 / 118 | 20 / 92 | pass | fail: pre-existing reaction-count mismatch |
| `SHP2_base_model` | 149 / 1082 | 149 / 1032 | pass | fail: pre-existing reaction-count mismatch |
| `egfr_net` | 356 / 3749 | 356 / 3749 | pass | pass |
| `fceri_ji` | 354 / 3680 | 354 / 3680 | pass | pass |

Counts are species/reactions. The two small/reference mismatches were present
in the baseline C++ behavior before this optimization and are not introduced
by the candidate; candidate-vs-baseline artifacts remain byte-identical. The
repository `compare_rxn.pl` also emits a pre-existing missing-argument warning
and prints a misleading `0 versus 0` count in its failure message; the counts
above were independently parsed from both `.net` files.

## Profiles and rejected alternatives

The baseline macOS `sample` profile for an EGFR network-generation run
captured 5 seconds and 5,648 samples. The dominant stack was
`ActionDispatch::execute` (3,295), `NetworkGenerator::generate` (3,015),
`NetworkGenerator::generateNative` (3,013), and
`ReactionRule::expandRule` (1,175). `SpeciesList::add`, canonical labeling,
`find_canonical_order`, and BNG2-string serialization were visible below that
stack. A final-candidate profile captured 5 seconds and 3,615 samples, with
the same dominant stack: `NetworkGenerator::generateNative` (2,980),
`ReactionRule::expandRule` (1,104), `SpeciesList::add` (173), and canonical
label calls nested in the species-add path. The FcERI profile likewise showed
network generation as the relevant generation hotspot, while its full run was
also dominated by the ODE solver.

Measured alternatives were not retained:

| Experiment | Paired wall-time deltas by `SHP2`, `blbr`, `egfr_net`, `fceri_ji` | Decision |
| --- | --- | --- |
| `std::map<Node*, int>` -> unordered map in canonicalization | +1.009%, -1.365%, +0.232%, -0.281% | reject: inconsistent and slower on two larger cases |
| Exact-first without the compartment-safe follow-up | -4.611%, +5.299%, +1.444%, -1.441% | reject: regressions on `blbr` and EGFR |
| Fingerprint-gated serialization | -1.982%, +9.640%, +3.199%, +0.407% | reject: broad regressions |
| Fingerprint plus isomorphism precheck | +10.907%, +30.282%, +22.450%, +9.928% | reject: decisively slower |

The remaining profile-dominant CPU work is canonical labeling/Nauty and related
graph/string operations inside rule expansion and species deduplication. ODE
integration is another dominant cost for ODE-heavy models such as FcERI. A
further material gain in those areas would require a broader canonicalization
and deduplication data-structure redesign, parallel/GPU execution, or a
different-language implementation; those are outside this portable,
semantics-preserving scope.

## Validation commands and status

Targeted tests and the full Release CTest suite were run on the candidate:

```sh
build-codex/tests/test_SpeciesList
build-codex/tests/test_pattern_graph
ctest --test-dir build-codex --output-on-failure --parallel 4
```

The targeted tests passed repeatedly, and the full suite passed 80/80. The
ASan/UBSan build used the same source and pinned local dependency trees:

```sh
cmake -S . -B /private/tmp/bng-build-asan \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang \
  -DCMAKE_OSX_ARCHITECTURES=arm64 -DBUILD_TESTING=ON \
  -DCMAKE_C_FLAGS='-fsanitize=address,undefined -fno-omit-frame-pointer' \
  -DCMAKE_CXX_FLAGS='-fsanitize=address,undefined -fno-omit-frame-pointer' \
  -DCMAKE_EXE_LINKER_FLAGS='-fsanitize=address,undefined' \
  -DCMAKE_SHARED_LINKER_FLAGS='-fsanitize=address,undefined' \
  -DFETCHCONTENT_SOURCE_DIR_CATCH2="$PWD/build/_deps/catch2-src" \
  -DFETCHCONTENT_SOURCE_DIR_ANTLR4_RUNTIME="$PWD/build/_deps/antlr4_runtime-src" \
  -DFETCHCONTENT_SOURCE_DIR_SUNDIALS="$PWD/build/_deps/sundials-src"
cmake --build /private/tmp/bng-build-asan --parallel 4
ctest --test-dir /private/tmp/bng-build-asan --output-on-failure --parallel 4
```

The sanitizer suite passed 80/80, and separate ASan/UBSan production runs of
all four models exited successfully without sanitizer diagnostics. GitHub CI
must still be checked against the exact pushed final branch SHA; that external
result is intentionally not inferred from local test results.
