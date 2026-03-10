import math
from mcp.server.fastmcp import FastMCP
from physics_models import TsiolkovskyInput

# Initialize the MCP Server
server = FastMCP("RocketPropulsionPhysicsServer")

@server.tool(name="calculate_tsiolkovsky_mass", description="Calculates the initial wet mass and propellant mass using the Tsiolkovsky rocket equation.")
def calculate_tsiolkovsky_mass(inputs: TsiolkovskyInput) -> dict:
    """
    Solves the rocket equation: delta_v = v_e * ln(m_0 / m_f)
    """
    # Mass ratio (R) = m_0 / m_f = e^(delta_v / v_e)
    mass_ratio = math.exp(inputs.delta_v / inputs.exhaust_velocity)
    
    # Algebraic resolution for dry and wet mass incorporating structural ratio
    propellant_factor = (mass_ratio - 1)
    propellant_mass = inputs.payload_mass * propellant_factor / (1 - inputs.structural_ratio * propellant_factor)
    
    dry_mass = inputs.payload_mass + (inputs.structural_ratio * propellant_mass)
    wet_mass = dry_mass + propellant_mass
    
    return {
        "wet_mass_kg": round(wet_mass, 2),
        "dry_mass_kg": round(dry_mass, 2),
        "propellant_mass_kg": round(propellant_mass, 2),
        "mass_ratio": round(mass_ratio, 4)
    }

if __name__ == "__main__":
    server.run()
