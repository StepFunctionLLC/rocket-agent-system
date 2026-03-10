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
    draft = state.get("draft_design", {})
    payload = state.get("payload_mass", 0)
    
    # Initialize the errors list correctly
    errors = []
    
    # 1. Check for missing required parameters
    required_keys = ["wet_mass_kg", "dry_mass_kg", "propellant_mass_kg"]
    for key in required_keys:
        if key not in draft:
            errors.append(f"Missing required design parameter: {key}")
            
    # 2. Physical boundary constraint: Wet mass must be greater than the payload
    wet_mass = draft.get("wet_mass_kg", 0)
    if wet_mass <= payload:
        errors.append(f"Physical violation: Wet mass ({wet_mass} kg) must be strictly greater than payload mass ({payload} kg).")
        
    # 3. Mass conservation constraint: Wet Mass = Dry Mass + Propellant
    if all(k in draft for k in required_keys):
        calculated_wet = draft["dry_mass_kg"] + draft["propellant_mass_kg"]
        # Allow a small tolerance for floating point rounding
        if abs(calculated_wet - draft["wet_mass_kg"]) > 1.0: 
            errors.append("Mass conservation violation: dry_mass_kg + propellant_mass_kg does not equal wet_mass_kg.")
            
    # Update the explicit state with any caught errors
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
