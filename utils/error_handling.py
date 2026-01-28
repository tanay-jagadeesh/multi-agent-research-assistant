import logging
from functools import wraps

logger = logging.getLogger(__name__)


def retry_on_failure(max_retries=3):
    """Decorator to retry failed operations."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"{func.__name__} failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                    if attempt < max_retries - 1:
                        continue
            logger.error(f"{func.__name__} failed after {max_retries} attempts")
            raise last_exception
        return wrapper
    return decorator


def safe_agent_invoke(agent, inputs, config, agent_name="Agent"):
    """Safely invoke an agent with error handling."""
    try:
        result = agent.invoke(inputs, config)
        if not result or 'messages' not in result or not result['messages']:
            logger.error(f"{agent_name}: No valid response received")
            return None
        return result
    except Exception as e:
        logger.error(f"{agent_name} invocation failed: {str(e)}")
        return None


def validate_state_field(state, field_name, default=""):
    """Validate and return state field with default fallback."""
    value = state.get(field_name)
    if value is None or (isinstance(value, str) and not value.strip()):
        logger.warning(f"State field '{field_name}' is empty, using default")
        return default
    return value
