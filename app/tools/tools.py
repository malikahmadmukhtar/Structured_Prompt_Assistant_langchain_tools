from langchain_core.tools import tool


# --- TOOL DEFINITION ---
@tool
def get_weather(city: str) -> str:
    """Returns the weather and name of a given city and can call the get_city_from_area tool to get city"""
    print(f"called Getting weather for {city}")
    return f"The weather in {city} is sunny and 25°C."
@tool
def get_city_from_area(area: str) -> str:
    """Returns the city based on area given and can be used by other tools that need city as input"""
    print(f"called Getting city for {area}")
    return f"Your city in {area} is okara"