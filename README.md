# Recoil

**A semantic Saga coordinator for GenLayer Intelligent Contracts.**

Recoil coordinates multi-contract workflows whose success cannot always be reduced to a deterministic return code. It dispatches each step to a participant Intelligent Contract, uses GenLayer consensus to verify the participant's frozen postcondition, and automatically runs compensating actions in reverse order when a later step fails.

Recoil is intentionally **frontend-free**. It is a standalone Intelligent Contract primitive, not a product application. The repository includes a minimal participant harness only to prove IC-to-IC execution, callback idempotency, and compensation mechanics.

## Fixed network target

| Setting | Value |
|---|---|
| Environment | **Studionet** |
| Chain ID | **61999** |
| RPC | `https://studio.genlayer.com/api` |
| Currency | GEN |

The deployment and preflight tooling in this repository are locked to that target.

## The problem

A traditional transaction is atomic inside one execution context. Autonomous workflows increasingly span independent systems:

```text
reserve hotel
    ↓
reserve flight
    ↓
buy event ticket
```

The hotel and flight may already be finalized before the ticket fails. Earlier side effects cannot be magically reverted.

Distributed systems solve this with a **Saga**: every forward action has a compensating action. Recoil adds the semantic layer needed when “success” cannot be established by byte equality or a local return code.

```text
step 0 EXECUTE ── verified ──► CONFIRMED
                                  │
step 1 EXECUTE ── verified ──► CONFIRMED
                                  │
step 2 EXECUTE ── fails ─────► EXECUTION_FAILED
                                  │
                                  ▼
step 2 COMPENSATE
          │
step 1 COMPENSATE
          │
step 0 COMPENSATE
          │
          ▼
      COMPENSATED
```

If compensation itself cannot be verified, the Saga becomes `STUCK` rather than pretending rollback succeeded.

## Consensus boundary

Recoil deliberately separates semantic judgement from protocol mechanics.

**GenLayer consensus decides only:**

> Does this independently observed evidence materially establish the frozen execution or compensation postcondition?

The leader proposes a bounded result. Validators independently repeat the evidence observation and judgement. A forged `SATISFIED` result is rejected when the validator does not independently reach the same verdict.

**Deterministic contract code decides:**

- immutable blueprint hashes;
- ordered step progression;
- participant authentication;
- stable operation IDs;
- timeout rules;
- reverse compensation order;
- bounded compensation retries;
- replay handling;
- terminal state and terminal commitment.

The LLM never invents a compensation, reorders a Saga, chooses a participant, or decides whether a retry is allowed.

## Verdict model

Execution evidence is reduced to:

```text
SATISFIED
NOT_SATISFIED
AMBIGUOUS
UNAVAILABLE
TIMEOUT
```

Only `SATISFIED` advances the Saga.

Every other execution outcome starts compensation. Recoil starts rollback from the failed dispatched step itself because a partial external side effect may exist even when the success criterion was not established.

For compensation, anything except `SATISFIED` moves the Saga to `STUCK`.

## Evidence modes

Each step freezes separate evidence policies for execution and compensation.

### `PUBLIC_URL` (`2`)

The participant returns an HTTPS URL. Each validator independently renders the page and judges the frozen criterion. A `SATISFIED` result must carry a short verbatim excerpt grounded in the validator's own observation.

This is the preferred mode for externally visible effects.

### `PARTICIPANT_TEXT` (`1`)

The participant returns text from its own integration. Validators independently judge that same frozen text.

This is an attestation boundary, not independently discovered external truth, and the documentation says so explicitly.

## Finalized IC messages

Forward execution, compensation, and participant callbacks are emitted with `on="finalized"`.

Each child message is a later transaction, so participants must be idempotent. Recoil derives stable 32-byte operation IDs from the Saga, sealed blueprint, frozen step, context, and phase. Compensation retries reuse the same ID.

`contracts/demo_participant.py` is the reference harness: it stores operation IDs and does not apply the modeled effect twice.

## Blueprint lifecycle

```python
blueprint_id = recoil.create_blueprint(title, purpose)
recoil.add_step(...)
recoil.add_step(...)
recoil.seal_blueprint(blueprint_id)
```

A sealed step commits to:

- participant address;
- action payload;
- execution criterion;
- execution evidence mode;
- compensation payload;
- compensation criterion;
- compensation evidence mode;
- timeout.

A sealed blueprint receives a `definition_hash`. A Saga pins that hash for its entire lifetime.

## Starting a Saga

```python
saga_id = recoil.start_saga(blueprint_id, context)
```

Starting immediately persists `EXECUTION_DISPATCHED` and emits the first finalized participant message.

Participants later callback with:

```python
report_execution(saga_id, step_id, operation_id, evidence_ref)
report_compensation(saga_id, step_id, operation_id, evidence_ref)
```

A callback is accepted only from the participant address frozen into that exact step.

## Recovery surface

```python
timeout_current_execution(saga_id)
timeout_current_compensation(saga_id)
retry_stuck_compensation(saga_id)
```

Timeout crystallization is permissionless. Retrying a stuck compensation is controller-only, bounded, and reuses the same deterministic operation ID.

## Read surface

```python
get_blueprint(...)
get_step(...)
get_saga(...)
get_saga_step(...)
get_verification(...)
is_completed(...)
is_compensated(...)
get_protocol_constants()
```

## Reference participant interface

A participant contract should expose:

```python
def execute_step(
    coordinator: Address,
    saga_id: u256,
    step_id: u256,
    operation_id: str,
    action_payload: str,
    context: str,
) -> None: ...


def compensate_step(
    coordinator: Address,
    saga_id: u256,
    step_id: u256,
    operation_id: str,
    compensation_payload: str,
    context: str,
) -> None: ...
```

Integration requirements:

1. authenticate the trusted Recoil coordinator;
2. treat `operation_id` as an idempotency key;
3. never apply the same economic side effect twice;
4. make compensation safe after full, partial, or absent forward execution;
5. callback with evidence using a finalized message;
6. prefer public or immutable evidence for high-value external effects.

## Reviewer demo

The high-signal demo is deliberately frontend-free:

1. hotel reservation confirms;
2. flight booking confirms;
3. ticket purchase is declined;
4. validators independently establish that the ticket criterion failed;
5. Recoil changes direction automatically;
6. ticket compensation is verified;
7. flight cancellation is verified;
8. hotel cancellation is verified;
9. terminal state becomes `COMPENSATED` with an immutable terminal hash.

The repository includes public text fixtures for this flow and a manual Studionet lifecycle test template.

## Local checks

```bash
python scripts/preflight.py
python -m compileall contracts scripts tests
pip install -r requirements-test.txt
pytest tests/direct -q
```

Optional linter:

```bash
pip install -r requirements.txt
genvm-lint validate contracts/recoil.py
genvm-lint validate contracts/demo_participant.py
```

## Deployment

Configure and unlock the desired GenLayer CLI account, then:

```bash
python scripts/deploy_studionet.py recoil
python scripts/deploy_studionet.py participant
```

The helper targets **Studionet chain 61999** through `https://studio.genlayer.com/api` and never accepts or stores a private key.

## Repository structure

```text
contracts/
  recoil.py
  demo_participant.py
fixtures/
scripts/
tests/
docs/
DEPLOYMENT.md
SUBMISSION.md
```

## Security boundary

Recoil proves only what its frozen evidence policy can establish. It does not make irreversible effects reversible, discover correct compensations automatically, or convert participant-provided text into independent external proof. Failed compensation remains visibly `STUCK`.

See `docs/THREAT_MODEL.md` for the full boundary.

## License

MIT.
