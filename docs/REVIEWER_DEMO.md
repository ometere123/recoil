# Reviewer demo

Target: **Studionet, chain 61999, `https://studio.genlayer.com/api`**.

Deploy one `Recoil` and three `DemoParticipant` contracts representing hotel, flight, and ticket systems. Lock each participant's coordinator to the Recoil address.

Use raw GitHub fixture URLs from `fixtures/` and evidence mode `2` (`PUBLIC_URL`).

## Frozen steps

1. Hotel success: reservation H-100 is confirmed and active. Compensation: H-100 is cancelled and no active reservation remains.
2. Flight success: booking F-200 is confirmed, ticketed, and active. Compensation: F-200 is cancelled and no active booking remains.
3. Ticket success: T-300 is issued and valid. Compensation: no T-300 remains and any partial reservation is released.

For the rollback demo, configure ticket execution evidence to `ticket_declined.txt`.

Expected path:

```text
hotel execute       -> SATISFIED
flight execute      -> SATISFIED
ticket execute      -> NOT_SATISFIED

ticket compensate   -> SATISFIED
flight compensate   -> SATISFIED
hotel compensate    -> SATISFIED

Saga -> COMPENSATED
```

Show the reviewer the sealed blueprint hash, unique operation IDs, consensus receipts, automatic direction change, reverse rollback order, terminal hash, and participant effect counters. Replay a used participant operation and show the modeled effect count does not increase.

For the success path, use `ticket_issued.txt` in a fresh scenario and show terminal `COMPLETED` with no compensation effects.
