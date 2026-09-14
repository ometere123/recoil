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

## Live deployment

Addresses and finalized transaction evidence should be added only after a real deployment and verification. No live proof is claimed until that occurs.
