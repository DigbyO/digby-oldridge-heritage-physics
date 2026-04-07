#!/usr/bin/env python3
"""
Digby Oldridge Heritage Archive — Chromatic Lock Validator v45
Randomly samples 20 colours from the archive CSV and verifies that
the Taxonomy SFT completion contains exact Hex_Code, L*, a*, and b* strings.
Run:  python3 chromatic_lock_validator_v45.py
Exit: 0 = all pass | 1 = one or more failures
"""
import csv, json, random, sys

CSV_PATH   = "DIGBY_OLDRIDGE_FullArchive_v45.csv"
JSONL_PATH = "Digby_Taxonomy_SFT_v45.jsonl"
SAMPLE_N   = 20

with open(CSV_PATH, newline="", encoding="utf-8") as f:
    archive = {r["Brand_Name"].strip().split("—")[0].strip(): r
               for r in csv.DictReader(f)}

print(f"  Archive loaded: {len(archive)} entries")

# Longest-name-first to prevent prefix shadowing
sorted_names = sorted(archive.keys(), key=len, reverse=True)

sft_index = {}
with open(JSONL_PATH, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line: continue
        obj  = json.loads(line)
        comp = obj.get("completion", "")
        for name in sorted_names:
            if comp.startswith(name) or f"{name} (" in comp[:80]:
                sft_index.setdefault(name, []).append(comp)
                break

print(f"  JSONL indexed: {len(sft_index)} brand names")

sample = random.sample(sorted_names, min(SAMPLE_N, len(sorted_names)))
passed = failed = 0

print(f"\n{'═'*72}")
print(f"  DIGBY OLDRIDGE — CHROMATIC LOCK VALIDATION v45 ({SAMPLE_N} samples)")
print(f"{'═'*72}\n")

for name in sample:
    truth   = archive[name]
    hx      = truth["Hex_Code"].strip()
    L       = truth["L"].strip()
    a       = truth["a"].strip()
    b       = truth["b"].strip()
    is_hero = truth.get("Hero50","").strip().upper() == "TRUE"

    completions = sft_index.get(name, [])
    if not completions:
        print(f"  ✗ MISSING  {name}\n"); failed += 1; continue

    comp   = completions[0]
    hex_ok = hx in comp
    L_ok   = f"L*={L}" in comp
    a_ok   = f"a*={a}" in comp
    b_ok   = f"b*={b}" in comp
    ok     = hex_ok and L_ok and a_ok and b_ok

    hero_tag = " ★Hero50" if is_hero else ""
    print(f"  {'✓ PASS' if ok else '✗ FAIL'}  {name}{hero_tag}")
    print(f"    Hex={hx}  L*={L}  a*={a}  b*={b}")
    if not ok:
        missing = ([f"Hex={hx}"] if not hex_ok else []) + \
                  ([f"L*={L}"]   if not L_ok   else []) + \
                  ([f"a*={a}"]   if not a_ok   else []) + \
                  ([f"b*={b}"]   if not b_ok   else [])
        print(f"    ✗ NOT FOUND: {', '.join(missing)}")
        failed += 1
    else:
        passed += 1
    print()

print(f"{'─'*72}")
print(f"  Result: {passed}/{SAMPLE_N} passed  |  {failed}/{SAMPLE_N} failed")
print(f"{'═'*72}\n")
sys.exit(0 if failed == 0 else 1)
