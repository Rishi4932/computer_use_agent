import pytest

from core.state_machine import (
    AgentState,
    AgentStateMachine,
)


def test_initial_state():
    machine = AgentStateMachine()

    assert machine.get_state() == AgentState.IDLE


def test_valid_transitions():
    machine = AgentStateMachine()

    machine.transition(
        AgentState.PLANNING
    )

    assert machine.get_state() == AgentState.PLANNING

    machine.transition(
        AgentState.EXECUTING
    )

    assert machine.get_state() == AgentState.EXECUTING

    machine.transition(
        AgentState.VERIFYING
    )

    assert machine.get_state() == AgentState.VERIFYING

    machine.transition(
        AgentState.COMPLETED
    )

    assert machine.get_state() == AgentState.COMPLETED


def test_invalid_transition():
    machine = AgentStateMachine()

    with pytest.raises(ValueError):
        machine.transition(
            AgentState.COMPLETED
        )


def test_recovery_transition():
    machine = AgentStateMachine()

    machine.transition(
        AgentState.PLANNING
    )

    machine.transition(
        AgentState.EXECUTING
    )

    machine.transition(
        AgentState.VERIFYING
    )

    machine.transition(
        AgentState.RECOVERING
    )

    assert machine.get_state() == AgentState.RECOVERING

    machine.transition(
        AgentState.EXECUTING
    )

    assert machine.get_state() == AgentState.EXECUTING


def test_reset():
    machine = AgentStateMachine()

    machine.transition(
        AgentState.PLANNING
    )

    machine.transition(
        AgentState.EXECUTING
    )

    machine.transition(
        AgentState.VERIFYING
    )

    machine.transition(
        AgentState.COMPLETED
    )

    machine.reset()

    assert machine.get_state() == AgentState.IDLE