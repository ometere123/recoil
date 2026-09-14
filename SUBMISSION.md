# Recoil — standalone Intelligent Contract submission

## One sentence

Recoil is a semantic Saga coordinator that drives finalized IC-to-IC workflow execution and automatically runs verified compensating actions in reverse when a later semantic postcondition fails.

## Why this is a primitive

Recoil is not travel software, escrow, procurement, or a UI. Those are possible consumers. The reusable capability is distributed transaction coordination when success and compensation require semantic judgement.

Builders supply ordered participants, action payloads, execution/compensation postconditions, evidence modes, and timeouts. Recoil supplies immutable definitions, finalized dispatch, stable idempotency keys, semantic consensus, automatic progression, conservative reverse compensation, timeout crystallization, bounded retry, and immutable verification history.

## Consensus

The leader observes evidence and proposes `SATISFIED`, `NOT_SATISFIED`, `AMBIGUOUS`, or `UNAVAILABLE`. Validators independently repeat the observation and judgement. `SATISFIED` requires a grounded source excerpt that the validator can independently locate.

Only `SATISFIED` advances execution.

## Deterministic mechanics

The model does not choose the next step, create compensations, authorize participants, generate retry policy, reorder rollback, or decide terminal status. Contract state does.

## Network

Recoil targets **Studionet chain 61999** via `https://studio.genlayer.com/api`.

## Frontend

None. Recoil is intentionally submitted as a standalone Intelligent Contract primitive.

## Live proof (Studionet 61999)

Canonical Recoil: `0x5825cCD3dcBC713291c291e86c978444e0408a50`.
Three participant harnesses:

- `0xaD864b8EDb28721dAFACc96419e84aD392B9841B`
- `0x763eDd04372F7BC5C5F69Fb280C47D5768494007`
- `0x4ecD6FEc84a567b0E177B963C848Dc23bCb2D3BC`

The deployment and lifecycle transaction records are in `DEPLOYMENT.md`. The all-success Saga reached `COMPLETED` after three finalized participant callbacks. A separate Saga intentionally failed semantic verification on step 3 and reached `COMPENSATED`; finalized compensation callbacks prove reverse order 3 → 2 → 1.

The live callback initially exposed a GenVM v0.1 event ABI limit: `StepVerified` had four indexed fields plus its signature. The final source indexes `saga_id`, `step_id`, and `phase`, and stores `verdict` in the event blob. No lifecycle semantics changed.

Recoil has no frontend. It is a reusable Saga coordinator and reference participant harness, targeting only Studionet chain 61999 at `https://studio.genlayer.com/api`.
