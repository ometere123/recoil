#!/usr/bin/env python3
"""Zero-dependency source/network/security preflight for Recoil."""
from __future__ import annotations
import ast, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RECOIL = ROOT / "contracts" / "recoil.py"
PARTICIPANT = ROOT / "contracts" / "demo_participant.py"
STABLE_DEP = "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6"
RPC = "https://studio.genlayer.com/api"
CHAIN = "61999"
DISALLOWED = ("619" + "97", "studio" + "-dev", "studionet" + "-dev")

class Fail(RuntimeError): pass

def check(ok: bool, message: str) -> None:
    if not ok: raise Fail(message)

def files():
    for p in ROOT.rglob("*"):
        if p.is_file() and not any(x in p.parts for x in (".git", ".venv", "venv", "__pycache__", ".pytest_cache")):
            yield p

def main() -> int:
    count = 0
    for p in files():
        if p.suffix.lower() in {".py", ".md", ".txt", ".yaml", ".yml", ".toml", ".example", ""}:
            text = p.read_text(encoding="utf-8", errors="strict")
            for bad in DISALLOWED:
                check(bad.lower() not in text.lower(), f"disallowed network marker in {p.relative_to(ROOT)}")
            count += 1
    for p in (RECOIL, PARTICIPANT):
        text = p.read_text(encoding="utf-8")
        ast.parse(text)
        check(STABLE_DEP in text, f"wrong dependency pin: {p.name}")
    source = RECOIL.read_text(encoding="utf-8")
    part = PARTICIPANT.read_text(encoding="utf-8")
    check(source.count("gl.vm.run_nondet_unsafe") == 1, "expected one custom consensus boundary")
    check(source.count('emit(on="finalized")') >= 2, "forward/compensation messages must finalize")
    check(part.count('emit(on="finalized")') >= 2, "participant callbacks must finalize")
    check("SAGA_STUCK" in source and "MAX_COMPENSATION_RETRIES" in source, "bounded failure recovery missing")
    check("callback sender is not the configured participant" in source, "participant authentication missing")
    check("local/private hosts are rejected" in source, "URL hardening missing")
    check("criteria must be passive descriptive conditions" in source, "criterion prompt-channel guard missing")
    check(RPC in (ROOT / "gltest.config.yaml").read_text() and RPC in (ROOT / "scripts" / "deploy_studionet.py").read_text(), "stable RPC not pinned")
    check(CHAIN in (ROOT / "README.md").read_text() and CHAIN in (ROOT / "scripts" / "deploy_studionet.py").read_text(), "chain id not pinned")
    forbidden = {"package.json", "index.html", "vite.config.ts", "next.config.js"}
    check(not any(p.name in forbidden for p in files()), "frontend artifact present")
    print(f"PASS: Recoil preflight ({count + 11} checks)")
    print("TARGET: Studionet chain 61999 at https://studio.genlayer.com/api")
    print("SURFACE: standalone Intelligent Contracts only; no frontend")
    return 0

if __name__ == "__main__":
    try: raise SystemExit(main())
    except Fail as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
