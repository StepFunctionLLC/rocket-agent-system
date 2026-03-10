from typing import TypedDict
from langgraph.graph import StateGraph, END

# 1. Define the Explicit State
class DesignState(TypedDict):
    payload_mass: float
    target_altitude: float
    current_phase: str
    draft_design: dict
    validation_errors: list[str]
    retry_count: int

# 2. Define Nodes (Worker Functions)
def generator_node(state: DesignState):
    # LLM reads SKILL.md, formats inputs, and calls the FastMCP server
    # Implementation of LLM invocation goes here...
    return {"current_phase": "validation", "draft_design": {"wet_mass_kg": 15000, "engine_type": "bipropellant"}}

def validator_node(state: DesignState):
    # Independent LLM or deterministic check verifies the draft design against physics limits
    errors =
    # If the generator hallucinated numbers that don't match the Tsiolkovsky output, flag an error
    return {"validation_errors": errors}

# 3. Define Conditional Edges (Routing Logic)
def route_validation(state: DesignState):
    if state.get("retry_count", 0) > 3:
        return "human_escalation" # Circuit breaker for infinite loops
    if len(state.get("validation_errors",)) > 0:
        return "generator" # Force generator to self-correct based on Pydantic/Validator errors
    return END

# 4. Build the State Machine
workflow = StateGraph(DesignState)
workflow.add_node("generator", generator_node)
workflow.add_node("validator", validator_node)

workflow.set_entry_point("generator")
workflow.add_edge("generator", "validator")
workflow.add_conditional_edges("validator", route_validation)

app = workflow.compile()
