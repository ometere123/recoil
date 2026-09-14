"""Manual stable Studionet lifecycle template. Excluded from ordinary CI."""
import os, time, pytest
from gltest import get_contract_factory, get_default_account
from gltest.assertions import tx_execution_succeeded

RECOIL = "recoil.py"
PARTICIPANT = "demo_participant.py"
RAW = "https://raw.githubusercontent.com/ometere123/recoil/main/fixtures/"
TX = {"consensus_max_rotations": 3, "wait_interval": 10000, "wait_retries": 30}
pytestmark = pytest.mark.skipif(os.getenv("RECOIL_LIVE_STUDIONET") != "1", reason="manual funded Studionet lifecycle")


def deploy(file):
    contract = get_contract_factory(contract_file_path=file).deploy(account=get_default_account(), **TX)
    assert contract.address
    return contract


def transact(method, args):
    receipt = method(args).transact(**TX)
    assert tx_execution_succeeded(receipt), receipt


def wait_terminal(recoil, wanted, timeout=1800):
    end = time.time() + timeout
    while time.time() < end:
        item = recoil.get_saga([1]).call()
        if item["status_name"] == wanted:
            return item
        if item["status_name"] == "STUCK":
            raise AssertionError(item)
        time.sleep(20)
    raise AssertionError("Saga did not reach expected terminal state")


def configure(participant, coordinator, execution_file, compensation_file):
    transact(participant.set_coordinator, [coordinator])
    transact(participant.configure_scenario, [1, RAW + execution_file, RAW + compensation_file])
    transact(participant.seal_scenario, [1])


def add_step(recoil, blueprint, participant, label, success, compensation):
    transact(recoil.add_step, [blueprint, participant.address, label, "1", success, 2, "1", compensation, 2, 900])


def test_third_step_failure_compensates_in_reverse():
    recoil = deploy(RECOIL)
    hotel, flight, ticket = deploy(PARTICIPANT), deploy(PARTICIPANT), deploy(PARTICIPANT)
    configure(hotel, recoil.address, "hotel_confirmed.txt", "hotel_cancelled.txt")
    configure(flight, recoil.address, "flight_confirmed.txt", "flight_cancelled.txt")
    configure(ticket, recoil.address, "ticket_declined.txt", "ticket_compensated.txt")
    transact(recoil.create_blueprint, ["Travel Saga", "Coordinate dependent reservations and compensate confirmed work after failure."])
    add_step(recoil, 1, hotel, "Hotel", "Reservation H-100 is confirmed and active.", "Reservation H-100 is cancelled and no active reservation remains.")
    add_step(recoil, 1, flight, "Flight", "Flight booking F-200 is confirmed, ticketed, and active.", "Flight booking F-200 is cancelled and no active booking remains.")
    add_step(recoil, 1, ticket, "Ticket", "Event ticket T-300 was issued and is valid for admission.", "No event ticket T-300 remains and any partial reservation was released.")
    transact(recoil.seal_blueprint, [1])
    transact(recoil.start_saga, [1, "Travel booking TRIP-7 for one traveller"])
    final = wait_terminal(recoil, "COMPENSATED")
    assert len(final["terminal_hash"]) == 64
    assert [recoil.get_saga_step([1, i]).call()["status_name"] for i in range(3)] == ["COMPENSATED", "COMPENSATED", "COMPENSATED"]
    for participant in (hotel, flight, ticket):
        counts = participant.get_counts().call()
        assert counts["execution_effect_count"] == 1
        assert counts["compensation_effect_count"] == 1
