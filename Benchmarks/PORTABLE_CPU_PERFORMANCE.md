# Portable CPU performance report

## Scope and result

This series targets the native C++ network-generation path used by production
models in `bng2/Models2`. It does not optimize a synthetic microbenchmark, alter
the CLI, change generated-file formats, or add an external dependency.

The first retained optimization is the two-commit implementation in `533ac26b`
(`perf: skip canonical labels for exact product duplicates`) and `92ca4c03`
(`perf: preserve canonical product ordering in exact dedup fast path`). On the
paired production matrix, its median end-to-end wall-time changes ranged from
-0.172% to -6.903%, and median CPU-time changes ranged from +0.081% to
-7.288%. The small `blbr` case is close enough to the noise floor that it is
reported as a workload limitation; the medium and large cases provide the
material evidence for retaining that change.

The second retained optimization is `7ee2db11` (`perf: cache immutable
reaction pattern metadata`). Against the first retained candidate, its median
CPU-time change was negative on all four workloads, ranging from -0.856% to
-2.317%; the detailed second matrix and its spread are recorded below.

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
retained performance source:         92ca4c03, 7ee2db11
final source tree:                   7ee2db11
```

`git pull --ff-only origin master` was run before creating the dedicated
branch. At the pre-cache candidate-source audit, the branch was six commits
ahead of `origin/master` and nine commits ahead of `upstream/master`. A final
local/remote audit was performed after the source and documentation commits;
the delivered branch ref, divergence, and CI/PR query results are reported in
the delivery summary. The previously dirty files and explicitly listed
untracked file were cleared at the user's request before this series began;
the final tree is required to be clean.

The final performance source includes the rejected exact-key experiment
`70acc9e2` followed by `e08a9bd2`, which restores the retained implementation,
and the accepted immutable pattern-metadata cache `7ee2db11`. The rejected
experiment is documented below and is not present in the final source behavior.

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
  --executable-b /private/tmp/bng_cpp-candidate-exact-precheck-move \
  --model bng2/Models2/blbr.bngl \
  --model bng2/Models2/SHP2_base_model.bngl \
  --model bng2/Models2/egfr_net.bngl \
  --model bng2/Models2/fceri_ji.bngl \
  --repetitions 20 --timeout 30 \
  --output /private/tmp/portable_cpu_exact_precheck_move_20.json
```

The first retained Release executable had the same SHA-256 as the candidate
artifact used above. The baseline executable SHA-256 was
`ece7a09b247a2a8eb95dbaa26db7427aa0e5d0772f5b7b8097a6d36aa404399a`; the
first retained candidate executable SHA-256 was
`a59ed4dc4ff5becf347b95f1915c6ddaf60bc54d4bb84a0160ae60a737d2a9a2`.
The final Release executable, including the metadata cache, is
`build-codex/src/bng_cpp` with SHA-256
`c4eeb05df99869d34364671089df598c7ecfc5f700c70e957297e968cb9b4d15`.
CPU time and RSS use Python `resource.getrusage` because `/usr/bin/time -l`
cannot read the required macOS counters in the sandbox.

The percentage is `100 * (candidate - baseline) / baseline`; negative means
the candidate is faster. The table reports independent medians and paired
median deltas. IQR and min/max are the paired percentage spread.

| Workload | Outputs: bytes; data rows | Wall baseline -> candidate (s) | Paired wall delta: median [IQR; min..max] | CPU baseline -> candidate (s) | Paired CPU delta: median [IQR; min..max] |
| --- | ---: | ---: | ---: | ---: | ---: |
| `blbr` | 5,112; N/A | 0.024501 -> 0.024358 | -0.172% [-0.832..+0.522; -6.923..+1.550] | 0.021025 -> 0.020930 | +0.081% [-0.961..+0.636; -7.255..+1.262] |
| `SHP2_base_model` | 343,261; 202 | 0.164564 -> 0.153212 | -6.903% [-7.483..-6.295; -8.662..-5.533] | 0.158193 -> 0.147044 | -7.288% [-7.528..-6.808; -8.215..-5.269] |
| `egfr_net` | 549,606; 102 | 0.582642 -> 0.566102 | -2.985% [-3.502..-2.451; -5.289..-1.055] | 0.570982 -> 0.554018 | -3.210% [-3.531..-2.240; -5.084..-1.687] |
| `fceri_ji` | 233,656; 22 | 0.665730 -> 0.638934 | -3.938% [-4.338..-3.769; -5.251..-2.903] | 0.653576 -> 0.627741 | -3.956% [-4.284..-3.753; -5.625..-3.032] |

Paired wall/CPU wins were respectively 11/20 and 11/20 for `blbr`, 20/20
and 20/20 for `SHP2`, 20/20 and 20/20 for `egfr_net`, and 20/20 and 20/20
for `fceri_ji`. Median maximum-RSS deltas were -0.146%, -0.610%, +0.379%,
and +0.062% in the same workload order. The medium and large workloads
therefore show repeatable CPU and wall-time reductions; `blbr` is retained
only as a small correctness/noise check, not as the performance justification.

The second retained optimization was measured against the first retained safe
candidate (`a59ed4dc...`) with 40 paired repetitions per workload (320 raw
records). The candidate executable was
`c4eeb05df99869d34364671089df598c7ecfc5f700c70e957297e968cb9b4d15`. The raw
result is `/private/tmp/portable_cpu_pattern_metadata_cache_40.json`.

```sh
python3 Benchmarks/portable_cpu_benchmark.py \
  --executable-a /private/tmp/bng_cpp-candidate-exact-precheck-move \
  --executable-b build-codex/src/bng_cpp \
  --model bng2/Models2/blbr.bngl \
  --model bng2/Models2/SHP2_base_model.bngl \
  --model bng2/Models2/egfr_net.bngl \
  --model bng2/Models2/fceri_ji.bngl \
  --repetitions 40 --timeout 30 \
  --output /private/tmp/portable_cpu_pattern_metadata_cache_40.json
```

| Workload | Wall retained -> cache (s) | Paired wall delta: median [IQR; min..max] | CPU retained -> cache (s) | Paired CPU delta: median [IQR; min..max] |
| --- | ---: | ---: | ---: | ---: |
| `blbr` | 0.023026 -> 0.022553 | -2.197% [-3.642..+0.358; -8.767..+4.164] | 0.022000 -> 0.021540 | -2.317% [-3.590..+0.368; -8.756..+4.781] |
| `SHP2_base_model` | 0.151441 -> 0.150011 | -0.720% [-1.954..+0.503; -4.262..+2.893] | 0.149507 -> 0.148274 | -0.856% [-1.927..+0.131; -3.838..+2.036] |
| `egfr_net` | 0.568566 -> 0.566068 | -0.997% [-1.621..+0.010; -4.814..+4.013] | 0.565503 -> 0.562712 | -1.014% [-1.633..-0.076; -4.098..+4.055] |
| `fceri_ji` | 0.637187 -> 0.631220 | -1.108% [-1.396..-0.436; -5.827..+0.483] | 0.633409 -> 0.626914 | -1.116% [-1.435..-0.593; -5.985..+0.042] |

Paired wall/CPU wins in this second run were 29/40 and 29/40 for `blbr`,
27/40 and 29/40 for `SHP2`, 29/40 and 31/40 for `egfr_net`, and 38/40 and
39/40 for `fceri_ji`. Median maximum-RSS deltas were -0.438%, +0.989%,
0.000%, and +0.372%, respectively. All four CPU medians improved; the
medium workload's IQR crosses zero slightly, so this records the consistent
direction and artifact identity without claiming every individual pair wins.

## Mechanism changed

`src/ast/SpeciesList.cpp` now exposes an exact-key lookup that checks the
compartment-aware string index without canonicalizing the graph. The existing
`add` path also checks that exact key before canonical labeling. Canonical
labeling remains in the fallback path. For species with a species-level
compartment, the deduplication string is recomputed after canonicalization
because serialization can depend on canonical node ordering; unscoped species
retain the pre-label exact key and existing canonical-label and
structural-fingerprint fallbacks.

`src/ast/ReactionRule.cpp` moves each product graph into a temporary `Species`,
probes the exact key, and returns the existing cached label immediately for an
exact duplicate. Only an exact-key miss canonicalizes the owned graph before
insertion, preserving the original canonical product ordering for non-duplicate
products. Labels are then read from the stored graph, preserving reaction
sorting and output. This ordering is important: a follow-up that carried a
pre-canonical exact key into insertion timed out on `Motivating_example_cBNGL`
because canonical labeling can change serializer order; its safety-gated
variant was noise-level or slower and was not retained.

`src/ast/ReactionRule.hpp` and `src/ast/ReactionRule.cpp` add a per-rule cache
of the immutable `PatternInfo` descriptions for reactant and product graphs.
The cache is built during `initialize()` and reused by embedding searches,
reaction construction, and delete-molecule handling, eliminating repeated
metadata allocations without changing graph ownership, match ordering, or
operation data. The out-of-line destructor and move operations keep the
opaque cache type portable across translation units.

The focused regression in `tests/ast/test_SpeciesList.cpp` covers two species
with identical structure but different molecule compartments, exact duplicate
reuse, and the resulting list size. The empty-graph test covers the
canonicalization guard needed by the validated build. The existing
`tests/ast/test_network_generator.cpp` path also reinitializes and moves a
`ReactionRule` into a model before checking generated species/reaction counts,
covering the cached rule metadata's lifecycle.

## Correctness evidence

For all 20 repetitions of all four workloads in the first retained comparison,
the candidate and baseline output-hash maps were identical. For all 40
repetitions in the metadata-cache comparison, the cache candidate and the
retained executable also had identical output-hash maps, sizes, and network
counts. The resulting deterministic artifacts had these stable hashes:

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

The baseline macOS `sample` profile for repeated EGFR network-generation runs
captured 5 seconds and 5,648 samples. The dominant stack was
`ActionDispatch::execute` (3,295), `NetworkGenerator::generate` (3,015),
`NetworkGenerator::generateNative` (3,013), and
`ReactionRule::expandRule` (1,175). `SpeciesList::add`, canonical labeling,
`find_canonical_order`, and BNG2-string serialization were visible below that
stack. A direct final-candidate EGFR profile captured the same stack during
the run: `ActionDispatch::execute` (248 samples),
`NetworkGenerator::generateNative` (223), `ReactionRule::expandRule` (81),
`SpeciesList::add` (at least 9 samples in its top path), and canonical-label
calls nested in product construction. The FcERI profile likewise showed
network generation as the relevant generation hotspot, while its full run was
also dominated by the ODE solver.

Measured alternatives were not retained. The node-index edge-lookup experiment
used executable SHA-256
`de090c072b46654105f4a7b2bd4a2b62559b08f3cb5fd9ec41b8a14f942fd471`, and the
serializer-key experiment used executable SHA-256
`2f2bcd847bcb13ebb420fbf38fd386dfab78f5d9bace103cc6cd1eeb2dd2e930`. Both
were compared directly with the retained candidate:

| Experiment | Paired deltas by `SHP2`, `blbr`, `egfr_net`, `fceri_ji` | Decision |
| --- | --- | --- |
| `std::map<Node*, int>` -> unordered map in canonicalization | +1.009%, -1.365%, +0.232%, -0.281% | reject: inconsistent and slower on two larger cases |
| Exact-first without the compartment-safe follow-up | -4.611%, +5.299%, +1.444%, -1.441% | reject: regressions on `blbr` and EGFR |
| Fingerprint-gated serialization | -1.982%, +9.640%, +3.199%, +0.407% | reject: broad regressions |
| Fingerprint plus isomorphism precheck | +10.907%, +30.282%, +22.450%, +9.928% | reject: decisively slower |
| Temporary node-index edge lookup (wall / CPU) | +0.205% / +0.217%, -0.600% / -1.554%, -0.928% / -1.006%, -0.964% / -1.003% | reject: SHP2 CPU regression; only 9/20 CPU wins |
| Cached compartment-aware serializer keys (wall / CPU) | +0.066% / +0.061%, -0.071% / +0.118%, +0.529% / +0.509%, +0.748% / +0.719% | reject: EGFR and FcERI regressions; 7/20 and 4/20 CPU wins |
| Exact-key handoff after product canonicalization | -0.885% / -0.836%, -5.938% / -6.848%, -4.592% / -4.395%, -1.648% / -1.667% | reject: timed out on `Motivating_example_cBNGL` in the 41-model harness |
| Safety-gated exact-key handoff (canonical graphs only) | +0.625% / +0.513%, +0.078% / -0.031%, +0.548% / +0.637%, -0.188% / -0.193% | reject: noise-level/slower; no material matrix win |
| Fingerprint lookup before canonical labeling | -0.535% / -0.541%, +3.241% / +4.009%, +0.133% / +0.195%, -0.460% / -0.366% | reject: `blbr` CPU regression; no broad win |

The remaining profile-dominant CPU work after both retained changes is
canonical labeling/Nauty and related graph/string operations inside rule
expansion and species deduplication. ODE integration is another dominant cost
for ODE-heavy models such as FcERI. A further material gain in those areas
would require a broader canonicalization and deduplication data-structure
redesign, parallel/GPU execution, or a different-language implementation;
those are outside this portable, semantics-preserving scope.

## Validation commands and status

Targeted tests and the full Release CTest suite were run on the candidate:

```sh
build-codex/tests/test_SpeciesList
build-codex/tests/test_pattern_graph
build-codex/tests/test_network_generator
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
all four models exited successfully without sanitizer diagnostics. No GitHub
Actions run can be created for this branch under the current workflow triggers:
they run on `master` pushes or pull requests, and the user explicitly
requested no RuleWorld pull request and no fork-default-branch push.

The repository script `scripts/validate_cpp_against_perl.sh` was also run over
all 41 available reference models for the final source using a temporary
macOS-compatible `timeout` shim (GNU `timeout` is not installed here). It
produced 34 passes and 7 failures, with the same failure set documented above:
the SHP2/blbr reaction-count mismatches, missing NFsim for
`isingspin_localfcn`, missing companion `.net` for `michment_cont`, unsupported
XML `readFile` in two SBML cases, and the missing `f_correct` parameter in
`test_time`. The previously passing `Motivating_example_cBNGL` also passed;
the rejected exact-key experiment had timed out there. These are reported
rather than silently treated as green.

No GitHub Actions run was created for the final branch SHA. The checked-in
workflows trigger on `master` pushes or pull requests, while the user
explicitly directed that no pull request be opened against `RuleWorld` and no
fork default-branch push be made. The final branch was pushed only to the
fork; local Release, independent-reference, full-harness, and ASan/UBSan
evidence above are the available validation for this no-PR delivery.
