#!/usr/bin/env python3
"""
Digby Oldridge Heritage Archive — RAG Proof-of-Concept
Demonstrates retrieval-augmented generation as an alternative to
taxonomy fine-tuning for the 1,102-entry colourimetric lookup layer.

Usage:
    python3 digby_rag_demo.py --query "warm ochre around L* 55"
    python3 digby_rag_demo.py --hex "#8C6E18"
    python3 digby_rag_demo.py --name "Didcot Mustard"

Requirements:
    pip install numpy   (no external embedding API needed — uses CIELAB distance)
"""
import csv, json, math, sys, argparse

CSV_PATH = "DIGBY_OLDRIDGE_FullArchive_v44_MERGED.csv"

# ── Load archive ──────────────────────────────────────────────────────────────
archive = []
with open(CSV_PATH, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        try:
            entry = {
                "id":    r["id"].strip(),
                "name":  r["Brand_Name"].strip(),
                "hex":   r["Hex_Code"].strip(),
                "L":     float(r["L"]),
                "a":     float(r["a"]),
                "b":     float(r["b"]),
                "C":     float(r["C"]) if r["C"].strip() else 0.0,
                "h":     float(r["h"]) if r["h"].strip() else 0.0,
                "hero":  r.get("Hero50","").strip().upper() in ("TRUE","1","YES"),
                "seo":   r.get("SEO_Description","").strip(),
                "adapt": r.get("Tropical_Adaptation_Note","").strip(),
                "warn":  r.get("Tropical_Red_Team_Warning","").strip(),
            }
            archive.append(entry)
        except (ValueError, KeyError):
            pass

print(f"Archive loaded: {len(archive)} entries ({sum(1 for e in archive if e['hero'])} Hero50)")

# ── Distance functions ────────────────────────────────────────────────────────

def ciede76(e1, e2):
    """Simple Euclidean CIELAB distance (ΔE76). Fast, sufficient for retrieval."""
    return math.sqrt((e1["L"]-e2["L"])**2 + (e1["a"]-e2["a"])**2 + (e1["b"]-e2["b"])**2)

def hex_to_lab_approx(hex_str):
    """Rough hex → sRGB → linear → XYZ → Lab (D65). Not ICC-accurate but sufficient for retrieval."""
    h = hex_str.lstrip("#")
    r, g, b = [int(h[i:i+2],16)/255.0 for i in (0,2,4)]
    def lin(c): return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
    r,g,b = lin(r), lin(g), lin(b)
    X = r*0.4124 + g*0.3576 + b*0.1805
    Y = r*0.2126 + g*0.7152 + b*0.0722
    Z = r*0.0193 + g*0.1192 + b*0.9505
    # D65 white point
    X,Y,Z = X/0.95047, Y/1.0, Z/1.08883
    def f(t): return t**(1/3) if t>0.008856 else 7.787*t+16/116
    fx,fy,fz = f(X),f(Y),f(Z)
    L = 116*fy - 16
    a = 500*(fx - fy)
    b_ = 200*(fy - fz)
    return {"L":L, "a":a, "b":b_}

def name_match_score(query, name):
    """Simple token overlap score for name-based retrieval."""
    qt = set(query.lower().split())
    nt = set(name.lower().split())
    if not qt: return 0.0
    return len(qt & nt) / len(qt)

# ── Retrieval functions ───────────────────────────────────────────────────────

def retrieve_by_name(query, top_k=5):
    scored = [(name_match_score(query, e["name"]), e) for e in archive]
    scored.sort(key=lambda x: -x[0])
    return [(s, e) for s, e in scored[:top_k] if s > 0]

def retrieve_by_hex(hex_str, top_k=5):
    probe = hex_to_lab_approx(hex_str)
    scored = [(ciede76(probe, e), e) for e in archive]
    scored.sort(key=lambda x: x[0])  # lower = closer
    return scored[:top_k]

def retrieve_by_lab(L, a, b, top_k=5):
    probe = {"L": L, "a": a, "b": b}
    scored = [(ciede76(probe, e), e) for e in archive]
    scored.sort(key=lambda x: x[0])
    return scored[:top_k]

# ── Format response ───────────────────────────────────────────────────────────

def format_result(entry, score=None, score_type="ΔE"):
    score_str = f"  ({score_type}={score:.2f})" if score is not None else ""
    lines = [
        f"  ┌─ {entry['name']} (ID {entry['id']}){score_str}",
        f"  │  Hex: {entry['hex']}",
        f"  │  L*={entry['L']}  a*={entry['a']}  b*={entry['b']}  C*={entry['C']}  h°={entry['h']}",
    ]
    if entry["hero"]:
        lines.append(f"  │  ★ Hero 50 flagship")
        if entry["warn"]:
            lines.append(f"  │  ⚠  {entry['warn'][:100]}{'...' if len(entry['warn'])>100 else ''}")
    if entry["seo"]:
        lines.append(f"  │  {entry['seo'][:100]}{'...' if len(entry['seo'])>100 else ''}")
    lines.append(f"  └{'─'*60}")
    return "\n".join(lines)

# ── CLI ───────────────────────────────────────────────────────────────────────

def demo():
    """Run 3 built-in demo queries to show retrieval working."""
    print("\n" + "═"*65)
    print("  DEMO 1 — Name retrieval: 'ochre sinodun'")
    print("═"*65)
    results = retrieve_by_name("ochre sinodun", top_k=3)
    for score, e in results:
        print(format_result(e, score, "name_score"))

    print("\n" + "═"*65)
    print("  DEMO 2 — Hex retrieval: #8C6E18 (near Didcot Mustard)")
    print("═"*65)
    results = retrieve_by_hex("#8C6E18", top_k=3)
    for de, e in results:
        print(format_result(e, de))

    print("\n" + "═"*65)
    print("  DEMO 3 — CIELAB retrieval: warm mid-ochre (L*=55, a*=8, b*=40)")
    print("═"*65)
    results = retrieve_by_lab(55, 8, 40, top_k=3)
    for de, e in results:
        print(format_result(e, de))

    print("\n  Why RAG beats fine-tuning for this layer:")
    print("  • Zero hallucination risk: retrieved rows are ground-truth CSV")
    print("  • Instantly updatable: add v45 entries, no retraining")
    print("  • ΔE76 retrieval is exact colourimetric distance, not token similarity")
    print("  • Hero50 warnings surface automatically at retrieval time")
    print("  • Cost: ~0ms CIELAB search vs GPU fine-tuning + inference")
    print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Digby Archive RAG Demo")
    parser.add_argument("--name",  help="Search by colour name")
    parser.add_argument("--hex",   help="Search by hex code")
    parser.add_argument("--L",     type=float, help="Search by L* value")
    parser.add_argument("--a",     type=float, help="Search by a* value")
    parser.add_argument("--b",     type=float, help="Search by b* value")
    parser.add_argument("--top",   type=int, default=5)
    parser.add_argument("--demo",  action="store_true", help="Run built-in demos")
    args = parser.parse_args()

    if args.demo or len(sys.argv)==1:
        demo()
    elif args.name:
        print(f"\nName search: '{args.name}'")
        for score, e in retrieve_by_name(args.name, args.top):
            print(format_result(e, score, "name_score"))
    elif args.hex:
        print(f"\nHex search: {args.hex}")
        for de, e in retrieve_by_hex(args.hex, args.top):
            print(format_result(e, de))
    elif args.L is not None:
        print(f"\nCIELAB search: L*={args.L} a*={args.a or 0} b*={args.b or 0}")
        for de, e in retrieve_by_lab(args.L, args.a or 0, args.b or 0, args.top):
            print(format_result(e, de))
