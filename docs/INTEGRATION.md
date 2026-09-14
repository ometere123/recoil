# Participant integration

A participant should expose:

```python
def execute_step(coordinator, saga_id, step_id, operation_id, action_payload, context): ...
def compensate_step(coordinator, saga_id, step_id, operation_id, compensation_payload, context): ...
```

After the attempted effect, callback using a finalized message:

```python
gl.get_contract_at(coordinator).emit(on="finalized").report_execution(
    saga_id, step_id, operation_id, evidence_ref
)
```

or `report_compensation` for rollback.

## Required invariants

- Pin and authenticate the Recoil coordinator.
- Persist `operation_id` as an idempotency key.
- Never apply the same economic side effect twice.
- On duplicate delivery, return the prior evidence instead of repeating the effect.
- Compensation must be safe after full, partial, or absent forward execution.
- Prefer immutable/public evidence for material external effects.

`contracts/demo_participant.py` is a minimal reference harness implementing those rules.
