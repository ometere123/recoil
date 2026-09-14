# Deployment

## Fixed target

```text
Environment: Studionet
Chain ID:    61999
RPC:         https://studio.genlayer.com/api
```

The deployment helper never accepts or stores a private key. Configure and unlock the desired GenLayer CLI account first.

## Checks

```bash
python scripts/preflight.py
python -m compileall contracts scripts tests
pip install -r requirements-test.txt
pytest tests/direct -q
```

## Deploy

```bash
python scripts/deploy_studionet.py recoil
python scripts/deploy_studionet.py participant
```

For the reviewer demo deploy three participant harnesses, lock each to the Recoil address, configure and seal one scenario each, create a three-step Recoil blueprint, then seal and start it.

Do not add a live address to the submission until the deployment transaction is actually finalized and the read surface has been checked. This repository does not fabricate deployment evidence.
