# Threat model

Recoil aims to ensure sealed blueprints cannot be rewritten mid-Saga, only the configured participant can callback for a step, only independently reproduced `SATISFIED` advances execution, rollback order is deterministic, compensation failure remains visible, and retries retain stable operation IDs.

## Malicious leader

Validators independently repeat observation and judgement. A proposed `SATISFIED` excerpt must also exist in the validator's independently observed source.

## Hostile public evidence

Public content is untrusted data. Recoil admits bounded HTTPS URLs, rejects obvious local/private host shapes, and frames source content as data. Criteria reject common active prompt-control phrases.

## Malicious participant

A participant cannot impersonate another step because callback sender is checked against the address sealed into the definition. Participant-text mode remains an attestation boundary; public evidence should be required for material external effects.

## Partial side effects

A failed postcondition does not establish that nothing happened. Therefore the current dispatched step is included in rollback.

## Duplicate delivery

Stable operation IDs let participant contracts enforce exactly-once modeled effects. The reference harness does this.

## Compensation failure

A non-satisfied compensation or callback timeout becomes `STUCK`. Controller retries are bounded and reuse the same operation ID.

## Out of scope

Recoil does not make irreversible effects reversible, discover a correct compensation automatically, guarantee arbitrary external services are honest, or turn participant text into independent external proof.
