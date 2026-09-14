# Consensus design

## Question

Recoil asks validators one bounded question:

> Does the observed evidence materially establish the frozen postcondition for this exact execution or compensation phase?

Semantic results are `SATISFIED`, `NOT_SATISFIED`, `AMBIGUOUS`, or `UNAVAILABLE`. `TIMEOUT` is deterministic protocol state.

## Leader

For public evidence the leader validates the HTTPS URL, renders the page, frames context/criterion/source as untrusted data, and produces a bounded JSON verdict. `SATISFIED` requires a short verbatim supporting excerpt.

For participant-text evidence, the same judgement is performed over a frozen attestation without claiming independent source discovery.

## Validators

A validator repeats the observation and semantic judgement. Acceptance requires:

- valid bounded result shape;
- the same independent verdict;
- for `SATISFIED`, the leader excerpt must exist in the validator's own observed source.

The custom `gl.vm.run_nondet_unsafe` boundary makes this substantive verification part of consensus rather than a format check.

## Fail closed

Only `SATISFIED` advances execution. Every other execution outcome begins compensation. Every non-satisfied compensation outcome becomes `STUCK`.

Malformed model output becomes `AMBIGUOUS`, never success.
