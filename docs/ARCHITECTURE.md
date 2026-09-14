# Architecture

Recoil is a distributed Saga coordinator whose semantic boundary is deliberately narrow. Consensus determines whether evidence establishes a frozen postcondition. Deterministic code owns every workflow transition around that judgement.

## Durable layers

1. **Blueprints** — immutable ordered workflow definitions.
2. **Saga instances** — executions pinned to a sealed blueprint hash.
3. **Step state** — execution/compensation dispatch state and operation IDs.
4. **Verification receipts** — consensus outcomes for semantic postconditions.

## State machines

```text
Blueprint: DRAFT -> SEALED

Saga: ACTIVE -> COMPLETED
        |
        +-> COMPENSATING -> COMPENSATED
                          -> STUCK

Step: PENDING -> EXECUTION_DISPATCHED -> CONFIRMED
                          |                 |
                          +-> EXECUTION_FAILED
                                  |
                                  v
                         COMPENSATION_DISPATCHED
                          |                 |
                          +-> COMPENSATED   +-> COMPENSATION_FAILED
```

## Asynchronous semantics

Recoil persists a dispatch state before emitting a finalized internal message. The participant effect is a later transaction. The participant then emits a later finalized callback carrying evidence. Recoil verifies that evidence in a separate consensus transaction.

## Operation IDs

Operation IDs commit to the protocol version, phase, Saga ID, blueprint hash, step ordinal/definition hash, and Saga context hash. A compensation retry therefore reuses the exact same ID.

## Conservative rollback

A failed or timed-out postcondition does not prove zero side effect. Recoil compensates the current dispatched step first, then prior confirmed steps in reverse order.

## Terminal commitment

A terminal hash commits to Saga ID, blueprint hash, final status, and all execution/compensation verification IDs.
