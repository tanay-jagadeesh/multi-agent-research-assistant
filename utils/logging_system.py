import logging
import time
from functools import wraps
from typing import Dict, List

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """Track performance metrics for agents."""

    def __init__(self):
        self.metrics = {
            "agent_times": {},
            "total_tokens": 0,
            "total_cost": 0.0,
            "agent_calls": {}
        }

    def track_agent(self, agent_name: str, duration: float, tokens: int = 0):
        """Record agent execution metrics."""
        if agent_name not in self.metrics["agent_times"]:
            self.metrics["agent_times"][agent_name] = []
            self.metrics["agent_calls"][agent_name] = 0

        self.metrics["agent_times"][agent_name].append(duration)
        self.metrics["agent_calls"][agent_name] += 1
        self.metrics["total_tokens"] += tokens
        self.metrics["total_cost"] += tokens * 0.000002

    def get_summary(self) -> Dict:
        """Get performance summary."""
        summary = {
            "total_time": sum(sum(times) for times in self.metrics["agent_times"].values()),
            "total_calls": sum(self.metrics["agent_calls"].values()),
            "total_tokens": self.metrics["total_tokens"],
            "total_cost": self.metrics["total_cost"],
            "agent_breakdown": {}
        }

        for agent, times in self.metrics["agent_times"].items():
            summary["agent_breakdown"][agent] = {
                "calls": self.metrics["agent_calls"][agent],
                "total_time": sum(times),
                "avg_time": sum(times) / len(times),
                "min_time": min(times),
                "max_time": max(times)
            }

        return summary

    def print_dashboard(self):
        """Print performance dashboard."""
        summary = self.get_summary()

        print("\n" + "="*60)
        print("PERFORMANCE DASHBOARD")
        print("="*60)
        print(f"\nTotal Execution Time: {summary['total_time']:.2f}s")
        print(f"Total Agent Calls: {summary['total_calls']}")
        print(f"Total Tokens: {summary['total_tokens']}")
        print(f"Estimated Cost: ${summary['total_cost']:.4f}")

        print("\n" + "-"*60)
        print("AGENT BREAKDOWN")
        print("-"*60)

        for agent, metrics in summary["agent_breakdown"].items():
            print(f"\n{agent}:")
            print(f"  Calls: {metrics['calls']}")
            print(f"  Total Time: {metrics['total_time']:.2f}s")
            print(f"  Avg Time: {metrics['avg_time']:.2f}s")
            print(f"  Range: {metrics['min_time']:.2f}s - {metrics['max_time']:.2f}s")

        print("\n" + "="*60)


performance_tracker = PerformanceTracker()


def log_agent_action(agent_name: str):
    """Decorator to log agent actions and track performance."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"[{agent_name}] Starting execution")
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                performance_tracker.track_agent(agent_name, duration)
                logger.info(f"[{agent_name}] Completed in {duration:.2f}s")

                if isinstance(result, dict):
                    for key, value in result.items():
                        if value:
                            logger.debug(f"[{agent_name}] State update: {key} = {str(value)[:100]}...")

                return result

            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"[{agent_name}] Failed after {duration:.2f}s: {str(e)}")
                raise

        return wrapper
    return decorator


def log_state_change(state_before: Dict, state_after: Dict, node_name: str):
    """Log state changes between nodes."""
    changes = []
    for key in state_after:
        if key in state_before:
            if state_before[key] != state_after.get(key):
                changes.append(key)
        elif state_after.get(key) is not None:
            changes.append(key)

    if changes:
        logger.info(f"[{node_name}] State changes: {', '.join(changes)}")
