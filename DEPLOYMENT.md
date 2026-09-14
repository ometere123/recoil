# Deployment and live evidence

## Fixed target

```text
Environment: Studionet
Chain ID:    61999
RPC:         https://studio.genlayer.com/api
```

The deployment helper never accepts or stores a private key. Configure and unlock the desired GenLayer CLI account first.

## Canonical live deployment

Observed on Studionet, chain `61999`, using `https://studio.genlayer.com/api` and CLI `0.39.2` (the pinned contracts use the v0.1 runner).

| Contract | Address | Deployment transaction | Final result |
|---|---|---|---|
| Recoil | `0x5825cCD3dcBC713291c291e86c978444e0408a50` | `0x209f84d6fdc41456625e3ad5012799891013344df1266c006eac6edd575ca6d7` | FINALIZED / MAJORITY_AGREE / SUCCESS |
| Demo participant 1 | `0xaD864b8EDb28721dAFACc96419e84aD392B9841B` | `0xdac0663cac79ec5523503490a5b76bd16f09416cdcc2be544630bfce2e2c4158` | FINALIZED / MAJORITY_AGREE / SUCCESS |
| Demo participant 2 | `0x763eDd04372F7BC5C5F69Fb280C47D5768494007` | `0x1111179b1df42c9a14e5fda6de672ef9009006fbb0eb952aa6200a6eacd08665` | FINALIZED / MAJORITY_AGREE / SUCCESS |
| Demo participant 3 | `0x4ecD6FEc84a567b0E177B963C848Dc23bCb2D3BC` | `0xca122ddec0ec22747fcf4edd29646a300156819550477e831e44d9443fb36875` | FINALIZED / MAJORITY_AGREE / SUCCESS |

Source hashes observed locally: Recoil `39379` bytes, SHA-256 `fd4a92ab116ea0576b4d0f9596265017ac397aaf7b4adc0de526c4456e9d3d93`; demo participant `7611` bytes, SHA-256 `cdf5212a7e5ddfd2060b6fedb3fb8fe3950527ec65af44e86bf006b090b578f8`.

## Reviewer lifecycle evidence

The final blueprint was created by `0x5b9355d5deba48bf6441c7f80037e4c04774ed294571401fcc698f99f430aed2`, steps were added by `0x008dae7f3247016a3694856c6b2896fc9f443cfd78850b5bb954aa7836b8fdec`, `0x157c4bae5291884d533b8b41777dff1f1c0bc69534917e65016a19767c7f0a54`, and `0xd8306afb9cef2c0203fd19fff7bf591991c6959a46b795420421cd34416c033a`; sealing was `0x82fdd3d3293ce9bc27bfff6ff181813e090ecc51dc9d0302589f73f121885724`.

Success Saga (blueprint 2) started with `0x282b641631f0db5969498c1b45c79cf3aab990209edab72d7ea66cbfd5e88fed`. The three participant execution transactions were `0xb461d0b02ec9ad98b9a5c420910487bf9b89e353f44445d7e560fcd25d917fe8`, `0x74319d5c8f11c50c4a2ff3c554d82e6208613a65e48353c0b7ad202e1c4fa315`, and `0x781c5c8a0b081acc224e9024f761fb9e361b4ee01d11d116cd6a592421ef309a`; their finalized Recoil callbacks were `0x07939010a2df5040ed27ebed4343dc2b69fd571818e14995a23636977997b86a`, `0x8335eada72acc6dcba3bb7fb278ce4c201466a7f1eaf8774267c921df5cae7fe`, and `0xe7ae38b7f6ce54030ba4f852550aaf7fa2bbd941d187523a0886af239706ba3b`. Readback reached `COMPLETED`.

Failure Saga (blueprint 1) started with `0x6aab8ab375d002798125e8601c8d884d48191e94d027490d98b17a3d32e88c16`. Step 1 and 2 dispatches were `0x0d872bd3729401f9b02df5416b4731887674583dec06360cc9d71134b0550852` and `0x43861ce37f691ed27e4ce84e478e7b562c001755128c3642e079b741d3ba4edc`; step 3 deliberately returned `NOT_SATISFIED` in `0x614bf88a6941a6444031a4e945fbe7cb908cadc92eb0337d747424eedcd27ff8`. Finalized callbacks were `0xb586132c8d8e7ccd2e4a402c396149b8d041abc92f3d4aa788f6890c90bfb26f`, `0x34c60725e73bf988024a3036f7c5738754d45a719b593be55850e60ab48a467d`, and `0xaba7b48602562a37841b691269f2283ad3f346a4886106d075048db844b06439`. Reverse compensation participant calls were `0xe535903a8c41e6ee1ceb5c6afa83c9426fa9c1fa8f4ceb2336b609f3ec8c69b1`, `0xdd6084acd277210a599fe8df704da0d3843d97523735f5bd7d5b0111d764eee9`, and `0xe7a9c5fb1a5ad8ded88971dbe6242bf4ad7969aaee181288db079c88f8eacacc`, with callbacks `0x182a5b3630bf3b1937f8ad57304f7e2d03b71e827f1c81fd63c7ff028a2b6164`, `0x117370e0fe6cd099f107a8fa6afba23d47d4ffbccdb448276ea4b6462a344e97`, and `0xf0387baeb0d868d86bf1d4dd5467c7e90d521ed8d2570f4e2eac25c8a4a496fb`. Readback reached `COMPENSATED`, proving reverse order `3 -> 2 -> 1`.

The first 0.40 RC Recoil deployment `0xe7f75d6295e3d9e13742fb3901929d64561060eab8d27ed34dfd084a7ea9069a` is retained as a diagnostic only: it finalized `NO_MAJORITY` with zero votes and no address. The later callback failure `0xcc807563aa1f1c0c376dcbb8daff4e7331312a3bcc010fcdbda491d4468787e2` exposed the v0.1 GenVM event topic limit at `StepVerified.emit()`; the final source keeps the verdict in the event blob and indexes only three fields.

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
