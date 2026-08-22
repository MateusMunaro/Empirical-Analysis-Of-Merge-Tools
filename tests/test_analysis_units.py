import unittest

from scripts.core.analysis_units import (
    AnalysisMatrix,
    AnalysisUnit,
    DEFAULT_SCENARIO_IDS,
    DEFAULT_TOOLS,
    MatrixValidationError,
    ObservationStatus,
    ScenarioObservation,
    expected_analysis_units,
)


class AnalysisUnitTests(unittest.TestCase):
    def test_default_design_contains_117_unique_units(self):
        units = expected_analysis_units()

        self.assertEqual(117, len(units))
        self.assertEqual(117, len(set(units)))
        self.assertEqual(set(DEFAULT_TOOLS), {unit.tool_name for unit in units})
        self.assertEqual(
            set(DEFAULT_SCENARIO_IDS), {unit.scenario_id for unit in units}
        )

    def test_scenario_id_must_be_canonical(self):
        invalid_ids = ("1", "scenario_0", "scenario_01", "Scenario_1", "scenario_x")

        for scenario_id in invalid_ids:
            with self.subTest(scenario_id=scenario_id):
                with self.assertRaises(ValueError):
                    AnalysisUnit("FSTMerge", scenario_id)

    def test_tool_name_must_not_be_blank_or_padded(self):
        for tool_name in ("", " ", " FSTMerge", "FSTMerge "):
            with self.subTest(tool_name=tool_name):
                with self.assertRaises(ValueError):
                    AnalysisUnit(tool_name, "scenario_1")

    def test_observation_requires_runtime_domain_types(self):
        unit = AnalysisUnit("FSTMerge", "scenario_1")

        with self.assertRaises(TypeError):
            ScenarioObservation(unit, "crash")  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            ScenarioObservation(  # type: ignore[arg-type]
                "FSTMerge/scenario_1", ObservationStatus.CRASH
            )

    def test_status_detail_must_be_nonblank_and_trimmed(self):
        unit = AnalysisUnit("FSTMerge", "scenario_1")

        for detail in ("", " ", " padded"):
            with self.subTest(detail=detail):
                with self.assertRaises(ValueError):
                    ScenarioObservation(unit, ObservationStatus.CRASH, detail)


class AnalysisMatrixTests(unittest.TestCase):
    def test_duplicate_observation_is_rejected(self):
        matrix = AnalysisMatrix()
        observation = ScenarioObservation(
            AnalysisUnit("FSTMerge", "scenario_1"),
            ObservationStatus.COMPLETED_CLEAN,
        )

        matrix.add(observation)

        with self.assertRaisesRegex(MatrixValidationError, "Duplicate"):
            matrix.add(observation)

    def test_undeclared_unit_is_rejected(self):
        matrix = AnalysisMatrix()
        observation = ScenarioObservation(
            AnalysisUnit("UnknownTool", "scenario_1"),
            ObservationStatus.SETUP_ERROR,
        )

        with self.assertRaisesRegex(MatrixValidationError, "Unexpected"):
            matrix.add(observation)

    def test_incomplete_matrix_reports_missing_units(self):
        matrix = AnalysisMatrix()
        matrix.add(
            ScenarioObservation(
                AnalysisUnit("FSTMerge", "scenario_1"),
                ObservationStatus.CRASH,
                "process returned a non-zero exit code",
            )
        )

        self.assertEqual(116, len(matrix.missing_units()))
        with self.assertRaisesRegex(
            MatrixValidationError, "116 of 117 observations are missing"
        ):
            matrix.validate_complete()

    def test_complete_matrix_accepts_all_terminal_statuses(self):
        matrix = AnalysisMatrix()
        statuses = tuple(ObservationStatus)
        for index, unit in enumerate(expected_analysis_units()):
            matrix.add(
                ScenarioObservation(
                    unit=unit,
                    status=statuses[index % len(statuses)],
                )
            )

        matrix.validate_complete()

        self.assertEqual(117, matrix.observed_count)
        self.assertEqual(117, sum(matrix.status_counts().values()))
        self.assertEqual(
            list(expected_analysis_units()),
            [observation.unit for observation in matrix.observations()],
        )

    def test_flat_record_uses_stable_public_field_names(self):
        observation = ScenarioObservation(
            AnalysisUnit("JDime", "scenario_39"),
            ObservationStatus.TIMEOUT,
            "exceeded 30 seconds",
        )

        self.assertEqual(
            {
                "tool_name": "JDime",
                "scenario_id": "scenario_39",
                "execution_status": "timeout",
                "status_detail": "exceeded 30 seconds",
            },
            observation.as_record(),
        )


if __name__ == "__main__":
    unittest.main()
