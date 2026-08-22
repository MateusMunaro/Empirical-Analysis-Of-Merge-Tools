"""Domain model for the study's unit of analysis.

The experimental unit is one merge tool applied to one controlled scenario.
This module deliberately does not calculate metrics or inspect tool outputs. It
defines the 39 x 3 analysis matrix and validates that every observation appears
exactly once.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Iterable, Iterator, Mapping, Sequence


DEFAULT_TOOLS: tuple[str, ...] = ("FSTMerge", "IntelliMerge", "JDime")
DEFAULT_SCENARIO_IDS: tuple[str, ...] = tuple(
    f"scenario_{scenario_number}" for scenario_number in range(1, 40)
)

_SCENARIO_ID_PATTERN = re.compile(r"^scenario_([1-9][0-9]*)$")


class ObservationStatus(str, Enum):
    """Mutually exclusive terminal states for a tool-scenario execution."""

    COMPLETED_CLEAN = "completed_clean"
    COMPLETED_CONFLICTED = "completed_conflicted"
    INVALID_OUTPUT = "invalid_output"
    CRASH = "crash"
    TIMEOUT = "timeout"
    SETUP_ERROR = "setup_error"


class MatrixValidationError(ValueError):
    """Raised when observations do not form the declared analysis matrix."""


@dataclass(frozen=True, order=True)
class AnalysisUnit:
    """Unique key for one observation in the experiment."""

    tool_name: str
    scenario_id: str

    def __post_init__(self) -> None:
        normalized_tool_name = self.tool_name.strip()
        if not normalized_tool_name:
            raise ValueError("tool_name must not be empty")
        if normalized_tool_name != self.tool_name:
            raise ValueError("tool_name must not contain leading or trailing whitespace")
        if not _SCENARIO_ID_PATTERN.fullmatch(self.scenario_id):
            raise ValueError(
                "scenario_id must use the canonical form 'scenario_<positive integer>'"
            )


@dataclass(frozen=True)
class ScenarioObservation:
    """Terminal outcome associated with exactly one analysis unit."""

    unit: AnalysisUnit
    status: ObservationStatus
    status_detail: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.unit, AnalysisUnit):
            raise TypeError("unit must be an AnalysisUnit")
        if not isinstance(self.status, ObservationStatus):
            raise TypeError("status must be an ObservationStatus")
        if self.status_detail is not None:
            if not isinstance(self.status_detail, str):
                raise TypeError("status_detail must be a string or None")
            if not self.status_detail.strip():
                raise ValueError("status_detail must not be blank")
            if self.status_detail != self.status_detail.strip():
                raise ValueError(
                    "status_detail must not contain leading or trailing whitespace"
                )

    def as_record(self) -> dict[str, str | None]:
        """Return a flat record suitable for CSV or JSON serialization."""

        return {
            "tool_name": self.unit.tool_name,
            "scenario_id": self.unit.scenario_id,
            "execution_status": self.status.value,
            "status_detail": self.status_detail,
        }


def expected_analysis_units(
    tools: Sequence[str] = DEFAULT_TOOLS,
    scenario_ids: Sequence[str] = DEFAULT_SCENARIO_IDS,
) -> tuple[AnalysisUnit, ...]:
    """Build the declared tool x scenario matrix in deterministic order."""

    _validate_declared_axis("tools", tools)
    _validate_declared_axis("scenario_ids", scenario_ids)
    return tuple(
        AnalysisUnit(tool_name=tool_name, scenario_id=scenario_id)
        for tool_name in tools
        for scenario_id in scenario_ids
    )


class AnalysisMatrix:
    """Validated collection of one observation per expected analysis unit."""

    def __init__(
        self,
        tools: Sequence[str] = DEFAULT_TOOLS,
        scenario_ids: Sequence[str] = DEFAULT_SCENARIO_IDS,
    ) -> None:
        self._expected_units = expected_analysis_units(tools, scenario_ids)
        self._expected_set = frozenset(self._expected_units)
        self._observations: dict[AnalysisUnit, ScenarioObservation] = {}

    @property
    def expected_count(self) -> int:
        return len(self._expected_units)

    @property
    def observed_count(self) -> int:
        return len(self._observations)

    def add(self, observation: ScenarioObservation) -> None:
        """Add one observation, rejecting duplicates and undeclared units."""

        unit = observation.unit
        if unit not in self._expected_set:
            raise MatrixValidationError(
                f"Unexpected analysis unit: {unit.tool_name}/{unit.scenario_id}"
            )
        if unit in self._observations:
            raise MatrixValidationError(
                f"Duplicate analysis unit: {unit.tool_name}/{unit.scenario_id}"
            )
        self._observations[unit] = observation

    def extend(self, observations: Iterable[ScenarioObservation]) -> None:
        for observation in observations:
            self.add(observation)

    def missing_units(self) -> tuple[AnalysisUnit, ...]:
        """Return missing units in the deterministic declared order."""

        return tuple(
            unit for unit in self._expected_units if unit not in self._observations
        )

    def validate_complete(self) -> None:
        """Require exactly one observation for every declared matrix cell."""

        missing = self.missing_units()
        if missing:
            preview = ", ".join(
                f"{unit.tool_name}/{unit.scenario_id}" for unit in missing[:5]
            )
            suffix = "" if len(missing) <= 5 else f", ... (+{len(missing) - 5})"
            raise MatrixValidationError(
                f"Incomplete analysis matrix: {len(missing)} of "
                f"{self.expected_count} observations are missing: {preview}{suffix}"
            )

    def observations(self) -> Iterator[ScenarioObservation]:
        """Yield observations in tool/scenario declaration order."""

        for unit in self._expected_units:
            observation = self._observations.get(unit)
            if observation is not None:
                yield observation

    def status_counts(self) -> Mapping[ObservationStatus, int]:
        counts = {status: 0 for status in ObservationStatus}
        for observation in self._observations.values():
            counts[observation.status] += 1
        return counts


def _validate_declared_axis(axis_name: str, values: Sequence[str]) -> None:
    if not values:
        raise ValueError(f"{axis_name} must not be empty")
    if len(set(values)) != len(values):
        raise ValueError(f"{axis_name} must not contain duplicates")
