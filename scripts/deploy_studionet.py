#!/usr/bin/env python3
"""Deploy one Recoil contract to stable Studionet using the active CLI account."""
from __future__ import annotations
import pathlib, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "scripts" / "preflight.py"
STUDIONET_RPC = "https://studio.genlayer.com/api"
STUDIONET_CHAIN_ID = 61999
TARGETS = {
    "recoil": ROOT / "contracts" / "recoil.py",
    "participant": ROOT / "contracts" / "demo_participant.py",
}

def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    result = subprocess.run(command, cwd=ROOT, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)

def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in TARGETS:
        print("Usage: python scripts/deploy_studionet.py recoil|participant", file=sys.stderr)
        return 2
    cli = shutil.which("genlayer")
    if cli is None:
        print("ERROR: genlayer CLI is not installed or not on PATH.", file=sys.stderr)
        return 2
    contract = TARGETS[sys.argv[1]]
    run([sys.executable, str(PREFLIGHT)])
    print(f"TARGET: Studionet chain {STUDIONET_CHAIN_ID} via {STUDIONET_RPC}")
    run([cli, "account", "show"])
    run([cli, "deploy", "--contract", str(contract), "--rpc", STUDIONET_RPC])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
