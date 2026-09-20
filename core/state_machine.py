from enum import Enum


class AgentState(str, Enum):
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    RECOVERING = "recovering"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentStateMachine:
    def __init__(self):
        self.state = AgentState.IDLE

        self.allowed_transitions = {
            AgentState.IDLE: {
                AgentState.PLANNING,
            },

            AgentState.PLANNING: {
                AgentState.EXECUTING,
                AgentState.FAILED,
                AgentState.PAUSED,
            },

            AgentState.EXECUTING: {
                AgentState.VERIFYING,
                AgentState.FAILED,
                AgentState.PAUSED,
            },

            AgentState.VERIFYING: {
                AgentState.EXECUTING,
                AgentState.RECOVERING,
                AgentState.COMPLETED,
                AgentState.FAILED,
            },

            AgentState.RECOVERING: {
                AgentState.EXECUTING,
                AgentState.FAILED,
                AgentState.PAUSED,
            },

            AgentState.PAUSED: {
                AgentState.EXECUTING,
                AgentState.PLANNING,
                AgentState.FAILED,
            },

            AgentState.COMPLETED: {
                AgentState.IDLE,
            },

            AgentState.FAILED: {
                AgentState.IDLE,
                AgentState.RECOVERING,
            },
        }

    def transition(self, new_state: AgentState):

        if new_state not in self.allowed_transitions[
            self.state
        ]:
            raise ValueError(
                f"Invalid state transition: "
                f"{self.state.value} -> "
                f"{new_state.value}"
            )

        self.state = new_state

        return self.state

    def get_state(self) -> AgentState:
        return self.state

    def is_terminal(self) -> bool:
        return self.state in {
            AgentState.COMPLETED,
            AgentState.FAILED,
        }

    def reset(self):
        self.state = AgentState.IDLE