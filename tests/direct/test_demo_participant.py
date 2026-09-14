"""Direct-mode hardening tests for the idempotent participant harness."""
CONTRACT = "contracts/demo_participant.py"
SDK_VERSION = "v0.2.12"


def deploy(direct_deploy):
    return direct_deploy(CONTRACT, sdk_version=SDK_VERSION)


def address(name):
    from gltest.direct import create_address
    return create_address(name)


def test_scenario_can_be_sealed_once(direct_vm, direct_deploy):
    contract = deploy(direct_deploy)
    contract.configure_scenario(1, "execution receipt", "compensation receipt")
    contract.seal_scenario(1)
    assert contract.get_scenario(1)["sealed"] is True
    with direct_vm.expect_revert("already sealed"):
        contract.configure_scenario(1, "other", "other")


def test_coordinator_can_be_locked_once(direct_vm, direct_deploy):
    contract = deploy(direct_deploy)
    contract.set_coordinator(address("recoil"))
    with direct_vm.expect_revert("already locked"):
        contract.set_coordinator(address("other"))


def test_unsealed_scenario_cannot_be_used_as_valid_reference(direct_vm, direct_deploy):
    contract = deploy(direct_deploy)
    contract.configure_scenario(1, "execution receipt", "compensation receipt")
    assert contract.get_scenario(1)["sealed"] is False
