#!/usr/bin/env python3
"""
Digby Oldridge Heritage Archive — Chromatic Lock Validator v44
Randomly samples 20 colours from the merged archive CSV and verifies that
the Taxonomy SFT completion contains exact Hex_Code, L*, a*, and b* strings.

Checks:
  - Exact hex string match (e.g. #141820, not #14182 or #1418200)
  - Exact L*=<value> string (e.g. L*=8.2, not L*=8.20 or L*=8)
  - Exact a*=<value> string
  - Exact b*=<value> string

Run:  python3 chromatic_lock_validator_v44.py
Exit: 0 = all pass | 1 = one or more failures
"""
import csv, json, random, sys

CSV_PATH   = "DIGBY_OLDRIDGE_FullArchive_v44_MERGED.csv"
JSONL_PATH = "Digby_Taxonomy_SFT.jsonl"
SAMPLE_N   = 20
RANDOM_SEED = None  # set an int for reproducibility, e.g. 42

# ── Load CSV as ground truth ──────────────────────────────────────────────────
with open(CSV_PATH, newline="", encoding="utf-8") as f:
    archive = {r["Brand_Name"].strip(): r for r in csv.DictReader(f)}

print(f"  Archive loaded: {len(archive)} entries")

# ── Load JSONL — index Pair 1 completions by brand name ───────────────────────
# Sort names longest-first to prevent prefix shadowing
# (e.g. "Sparsholt Sloe Ink" must match before "Sparsholt Sloe")
sorted_names = sorted(archive.keys(), key=len, reverse=True)

sft_index = {}
with open(JSONL_PATH, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        completion = obj.get("completion", "")
        for name in sorted_names:
            if completion.startswith(name):
                sft_index.setdefault(name, []).append(completion)
                break

print(f"  JSONL indexed: {len(sft_index)} unique brand names found")

# ── Sample ────────────────────────────────────────────────────────────────────
if RANDOM_SEED is not None:
    random.seed(RANDOM_SEED)

sample = random.sample(sorted_names, min(SAMPLE_N, len(sorted_names)))
passed = 0
failed = 0

print(f"\n{'═'*72}")
print(f"  DIGBY OLDRIDGE — CHROMATIC LOCK VALIDATION ({SAMPLE_N} samples, v44)")
print(f"{'═'*72}\n")

for name in sample:
    truth = archive[name]
    hx  = truth["Hex_Code"].strip()
    L   = truth["L"].strip()
    a   = truth["a"].strip()
    b   = truth["b"].strip()
    is_hero = truth.get("Hero50","").strip().upper() == "TRUE"

    completions = sft_index.get(name, [])
    if not completions:
        print(f"  ✗ MISSING  {name}")
        print(f"    No Pair 1 completion found in JSONL\n")
        failed += 1
        continue

    comp = completions[0]   # Pair 1 completion

    # Exact string checks — no float re-parsing, no rounding tolerance
    hex_ok = hx in comp
    L_ok   = f"L*={L}" in comp
    a_ok   = f"a*={a}" in comp
    b_ok   = f"b*={b}" in comp
    ok     = hex_ok and L_ok and a_ok and b_ok

    hero_tag = " ★Hero50" if is_hero else ""
    print(f"  {'✓ PASS' if ok else '✗ FAIL'}  {name}{hero_tag}")
    print(f"    Expected  Hex={hx}  L*={L}  a*={a}  b*={b}")

    if not ok:
        missing = []
        if not hex_ok: missing.append(f"Hex={hx}")
        if not L_ok:   missing.append(f"L*={L}")
        if not a_ok:   missing.append(f"a*={a}")
        if not b_ok:   missing.append(f"b*={b}")
        print(f"    ✗ NOT FOUND IN COMPLETION: {', '.join(missing)}")
        failed += 1
    else:
        passed += 1
    print()

print(f"{'─'*72}")
print(f"  Result: {passed}/{SAMPLE_N} passed  |  {failed}/{SAMPLE_N} failed")
print(f"{'═'*72}\n")
sys.exit(0 if failed == 0 else 1)
