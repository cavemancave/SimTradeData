"""Smart cooldown with tiered error handling for data source throttling."""

import logging
import threading
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CooldownConfig:
    """Configuration for cooldown durations by error type.

    Each field represents the base cooldown duration in seconds for the
    corresponding error category. The actual cooldown may be longer due
    to the escalation multiplier applied on consecutive failures.

    Attributes:
        timeout: Base cooldown for timeout errors.
        connection_error: Base cooldown for connection errors.
        rate_limit: Base cooldown for rate-limiting responses.
        forbidden: Base cooldown for forbidden/authentication errors.
        default: Base cooldown for unclassified errors.
        max_multiplier: Upper bound for the escalation multiplier.
    """

    timeout: float = 30.0
    connection_error: float = 60.0
    rate_limit: float = 300.0
    forbidden: float = 600.0
    default: float = 120.0
    max_multiplier: float = 5.0


@dataclass
class SourceState:
    """Tracks the health and cooldown state of a single data source.

    Attributes:
        cooldown_until: Epoch timestamp when cooldown expires.
        consecutive_failures: Number of failures in a row without success.
        total_requests: Lifetime count of recorded events (success + failure).
        total_failures: Lifetime count of recorded failures.
        last_failure_time: Epoch timestamp of the most recent failure.
        last_success_time: Epoch timestamp of the most recent success.
    """

    cooldown_until: float = 0.0
    consecutive_failures: int = 0
    total_requests: int = 0
    total_failures: int = 0
    last_failure_time: float = 0.0
    last_success_time: float = 0.0


class SmartCooldown:
    """Thread-safe cooldown manager with tiered error handling.

    Maintains per-source state and applies escalating cooldown periods
    based on error type and consecutive failure count. Each source is
    tracked independently.
    """

    def __init__(self, config: CooldownConfig | None = None) -> None:
        self._config = config or CooldownConfig()
        self._lock = threading.RLock()
        self._sources: dict[str, SourceState] = {}

    def _get_state(self, source: str) -> SourceState:
        """Return the state for a source, creating it if needed.

        Must be called while holding self._lock.
        """
        if source not in self._sources:
            self._sources[source] = SourceState()
        return self._sources[source]

    def _base_duration(self, error_type: str) -> float:
        """Look up the base cooldown duration for an error type."""
        durations = {
            "timeout": self._config.timeout,
            "connection_error": self._config.connection_error,
            "rate_limit": self._config.rate_limit,
            "forbidden": self._config.forbidden,
        }
        return durations.get(error_type, self._config.default)

    def _calculate_multiplier(self, consecutive_failures: int) -> float:
        """Calculate the escalation multiplier for consecutive failures.

        Formula: min(1 + (consecutive_failures - 1) * 0.5, max_multiplier)
        At least 1.0 (first failure has multiplier 1.0).
        """
        raw = 1.0 + (consecutive_failures - 1) * 0.5
        return min(max(raw, 1.0), self._config.max_multiplier)

    def is_in_cooldown(self, source: str) -> bool:
        """Check whether a source is currently in cooldown.

        Args:
            source: Identifier of the data source.

        Returns:
            True if the source is in cooldown and should not be contacted.
        """
        with self._lock:
            state = self._get_state(source)
            return time.monotonic() < state.cooldown_until

    def record_failure(self, source: str, error_type: str) -> None:
        """Record a failure and enter cooldown for the source.

        The cooldown duration is calculated as:
            base_duration(error_type) * multiplier(consecutive_failures)

        Args:
            source: Identifier of the data source.
            error_type: Category of the error (e.g. "timeout", "rate_limit").
        """
        with self._lock:
            state = self._get_state(source)
            state.consecutive_failures += 1
            state.total_requests += 1
            state.total_failures += 1
            state.last_failure_time = time.monotonic()

            base = self._base_duration(error_type)
            multiplier = self._calculate_multiplier(state.consecutive_failures)
            duration = base * multiplier

            state.cooldown_until = time.monotonic() + duration

            logger.info(
                "Source '%s' entering cooldown for %.1fs "
                "(error_type=%s, consecutive_failures=%d, multiplier=%.1f)",
                source,
                duration,
                error_type,
                state.consecutive_failures,
                multiplier,
            )

    def record_success(self, source: str) -> None:
        """Record a successful request, resetting consecutive failures.

        Args:
            source: Identifier of the data source.
        """
        with self._lock:
            state = self._get_state(source)
            state.consecutive_failures = 0
            state.total_requests += 1
            state.last_success_time = time.monotonic()

    def get_status(self, source: str) -> dict:
        """Return a snapshot of the source's current status.

        Args:
            source: Identifier of the data source.

        Returns:
            Dictionary with keys: is_in_cooldown, cooldown_remaining,
            consecutive_failures, total_requests, total_failures.
        """
        with self._lock:
            state = self._get_state(source)
            now = time.monotonic()
            remaining = max(0.0, state.cooldown_until - now)

            return {
                "is_in_cooldown": now < state.cooldown_until,
                "cooldown_remaining": remaining,
                "consecutive_failures": state.consecutive_failures,
                "total_requests": state.total_requests,
                "total_failures": state.total_failures,
            }


# Global singleton for convenient access across the application.
cooldown_manager = SmartCooldown()
