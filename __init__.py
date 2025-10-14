"""NL2SQL package."""

# This allows the ADK web server to find the root_agent
try:
    from .agent.root_agent import root_agent
except ImportError:
    # If running directly, try alternative import
    try:
        from agent.root_agent import root_agent
    except ImportError:
        root_agent = None

__all__ = ['root_agent']
