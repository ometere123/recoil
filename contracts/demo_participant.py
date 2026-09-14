# v0.1.0
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
from dataclasses import dataclass

ERR_EXPECTED = "EXPECTED"
MAX_EVIDENCE_REF_LEN = 12000


@allow_storage
@dataclass
class Scenario:
    execution_evidence: str
    compensation_evidence: str
    sealed: bool


@allow_storage
@dataclass
class OperationRecord:
    saga_id: u256
    step_id: u256
    scenario_id: u256
    kind: u8
    evidence_ref: str
    calls: u8


class ScenarioConfigured(gl.Event):
    def __init__(self, scenario_id: u256, /, **blob): ...


class ScenarioSealed(gl.Event):
    def __init__(self, scenario_id: u256, /, **blob): ...


class DemoExecution(gl.Event):
    def __init__(self, operation_id: str, saga_id: u256, step_id: u256, /, **blob): ...


class DemoCompensation(gl.Event):
    def __init__(self, operation_id: str, saga_id: u256, step_id: u256, /, **blob): ...


def scenario_id(payload: str) -> u256:
    text = str(payload).strip()
    if text == "" or not text.isdigit() or int(text) <= 0:
        raise gl.vm.UserError(f"{ERR_EXPECTED}: demo payload must be a positive scenario id")
    return u256(int(text))


class DemoParticipant(gl.Contract):
    """Minimal idempotent participant used to prove Recoil's IC-to-IC Saga flow."""

    owner: Address
    coordinator: Address
    coordinator_locked: bool
    scenarios: TreeMap[u256, Scenario]
    operations: TreeMap[str, OperationRecord]
    execution_effect_count: u256
    compensation_effect_count: u256

    def __init__(self):
        self.owner = gl.message.sender_address
        self.coordinator_locked = False
        self.execution_effect_count = u256(0)
        self.compensation_effect_count = u256(0)

    def _owner(self) -> None:
        if gl.message.sender_address != self.owner:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: owner only")

    def _coordinator(self, coordinator: Address) -> None:
        if not self.coordinator_locked or coordinator != self.coordinator or gl.message.sender_address != self.coordinator:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: caller is not trusted Recoil coordinator")

    def _scenario(self, sid: u256) -> Scenario:
        item = self.scenarios.get(sid)
        if item is None or not item.sealed:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: unknown or unsealed scenario")
        return item

    @gl.public.write
    def set_coordinator(self, coordinator: Address) -> None:
        self._owner()
        if self.coordinator_locked:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: coordinator already locked")
        if str(coordinator).lower() == "0x0000000000000000000000000000000000000000":
            raise gl.vm.UserError(f"{ERR_EXPECTED}: zero coordinator")
        self.coordinator = coordinator
        self.coordinator_locked = True

    @gl.public.write
    def configure_scenario(self, sid: u256, execution_evidence: str, compensation_evidence: str) -> None:
        self._owner()
        execution_evidence = str(execution_evidence).strip()[:MAX_EVIDENCE_REF_LEN]
        compensation_evidence = str(compensation_evidence).strip()[:MAX_EVIDENCE_REF_LEN]
        if int(sid) <= 0 or not execution_evidence or not compensation_evidence:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: invalid scenario")
        item = self.scenarios.get_or_insert_default(sid)
        if item.sealed:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: scenario already sealed")
        item.execution_evidence = execution_evidence
        item.compensation_evidence = compensation_evidence
        ScenarioConfigured(sid).emit()

    @gl.public.write
    def seal_scenario(self, sid: u256) -> None:
        self._owner()
        item = self.scenarios.get(sid)
        if item is None or item.sealed or not item.execution_evidence or not item.compensation_evidence:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: scenario cannot be sealed")
        item.sealed = True
        ScenarioSealed(sid).emit()

    def _record(self, operation_id: str, saga_id: u256, step_id: u256, sid: u256, kind: int, evidence: str) -> OperationRecord:
        operation_id = str(operation_id).strip()
        if len(operation_id) != 64:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: operation id must be 32-byte hex digest")
        record = self.operations.get(operation_id)
        if record is None:
            record = self.operations.get_or_insert_default(operation_id)
            record.saga_id, record.step_id, record.scenario_id, record.kind = saga_id, step_id, sid, u8(kind)
            record.evidence_ref, record.calls = evidence, u8(1)
            if kind == 1:
                self.execution_effect_count = u256(int(self.execution_effect_count) + 1)
            else:
                self.compensation_effect_count = u256(int(self.compensation_effect_count) + 1)
        else:
            if record.saga_id != saga_id or record.step_id != step_id or int(record.kind) != kind:
                raise gl.vm.UserError(f"{ERR_EXPECTED}: operation id collision")
            record.calls = u8(int(record.calls) + 1)
        return record

    @gl.public.write
    def execute_step(self, coordinator: Address, saga_id: u256, step_id: u256, operation_id: str, action_payload: str, context: str) -> None:
        self._coordinator(coordinator)
        sid = scenario_id(action_payload)
        scenario = self._scenario(sid)
        record = self._record(operation_id, saga_id, step_id, sid, 1, str(scenario.execution_evidence))
        gl.get_contract_at(coordinator).emit(on="finalized").report_execution(saga_id, step_id, operation_id, str(record.evidence_ref))
        DemoExecution(operation_id, saga_id, step_id, context_hash=Keccak256(str(context).encode("utf-8")).hexdigest()).emit()

    @gl.public.write
    def compensate_step(self, coordinator: Address, saga_id: u256, step_id: u256, operation_id: str, compensation_payload: str, context: str) -> None:
        self._coordinator(coordinator)
        sid = scenario_id(compensation_payload)
        scenario = self._scenario(sid)
        record = self._record(operation_id, saga_id, step_id, sid, 2, str(scenario.compensation_evidence))
        gl.get_contract_at(coordinator).emit(on="finalized").report_compensation(saga_id, step_id, operation_id, str(record.evidence_ref))
        DemoCompensation(operation_id, saga_id, step_id, context_hash=Keccak256(str(context).encode("utf-8")).hexdigest()).emit()

    @gl.public.view
    def get_scenario(self, sid: u256) -> dict:
        item = self.scenarios.get(sid)
        if item is None:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: unknown scenario")
        return {"execution_evidence":str(item.execution_evidence), "compensation_evidence":str(item.compensation_evidence), "sealed":bool(item.sealed)}

    @gl.public.view
    def get_operation(self, operation_id: str) -> dict:
        item = self.operations.get(str(operation_id))
        if item is None:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: unknown operation")
        return {"saga_id":int(item.saga_id), "step_id":int(item.step_id), "scenario_id":int(item.scenario_id), "kind":int(item.kind), "evidence_ref":str(item.evidence_ref), "calls":int(item.calls)}

    @gl.public.view
    def get_counts(self) -> dict:
        return {"execution_effect_count":int(self.execution_effect_count), "compensation_effect_count":int(self.compensation_effect_count)}
