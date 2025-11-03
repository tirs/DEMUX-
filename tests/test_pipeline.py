import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import json

from core.pipeline import AudioPipeline, ProcessingManifest, ProcessingStage
from core.separator import SeparatorFactory, SeparatorModel
from core.processors import SeparationStage


class MockSeparator(SeparatorModel):
    def __init__(self, model_name: str = "mock"):
        super().__init__(model_name)

    def separate(self, input_path: str, output_dir: str):
        output_path = Path(output_dir) / "mock_output"
        output_path.mkdir(parents=True, exist_ok=True)

        mock_files = {}
        for track in self.get_supported_tracks():
            track_path = output_path / f"{track}.wav"
            track_path.touch()
            mock_files[track] = str(track_path)

        return mock_files

    def validate(self) -> bool:
        return True

    def get_supported_tracks(self):
        return ["vocals", "drums", "bass", "other"]


class TestAudioPipeline(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.pipeline = AudioPipeline(output_base_dir=self.temp_dir)
        self.test_input = Path(self.temp_dir) / "test_input.wav"
        self.test_input.touch()

    def tearDown(self):
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_pipeline_initialization(self):
        self.assertEqual(len(self.pipeline.stages), 0)
        self.assertTrue(Path(self.temp_dir).exists())

    def test_add_stage(self):
        stage = Mock()
        stage.name = "test_stage"
        stage.processor_type = "test"

        self.pipeline.add_stage(stage)
        self.assertEqual(len(self.pipeline.stages), 1)

    def test_get_job_status_not_found(self):
        status = self.pipeline.get_job_status("nonexistent")
        self.assertIsNone(status)

    def test_manifest_creation(self):
        @patch("core.processors.SeparationStage.validate_input")
        @patch("core.processors.SeparationStage.execute")
        def run_test(mock_execute, mock_validate):
            mock_validate.return_value = True
            mock_execute.return_value = {"test": str(self.test_input)}

            stage = Mock()
            stage.name = "test_stage"
            stage.processor_type = "test"
            stage.validate_input = Mock(return_value=True)
            stage.execute = Mock(return_value={"output": str(self.test_input)})

            self.pipeline.add_stage(stage)

            manifest = self.pipeline.process(str(self.test_input))

            self.assertEqual(manifest.status, "completed")
            self.assertEqual(len(manifest.stages), 1)
            self.assertIn("output", manifest.outputs)

            manifest_path = Path(self.temp_dir) / manifest.job_id / "manifest.json"
            self.assertTrue(manifest_path.exists())

            with open(manifest_path, "r") as f:
                saved_manifest = json.load(f)
                self.assertEqual(saved_manifest["job_id"], manifest.job_id)

        run_test()

    def test_manifest_persistence(self):
        @patch("core.processors.SeparationStage.validate_input")
        @patch("core.processors.SeparationStage.execute")
        def run_test(mock_execute, mock_validate):
            mock_validate.return_value = True
            mock_execute.return_value = {"test": str(self.test_input)}

            stage = Mock()
            stage.name = "test_stage"
            stage.processor_type = "test"
            stage.validate_input = Mock(return_value=True)
            stage.execute = Mock(return_value={"output": str(self.test_input)})

            self.pipeline.add_stage(stage)

            manifest1 = self.pipeline.process(str(self.test_input))
            manifest2 = self.pipeline.get_job_status(manifest1.job_id)

            self.assertIsNotNone(manifest2)
            self.assertEqual(manifest1.job_id, manifest2.job_id)
            self.assertEqual(manifest1.status, manifest2.status)

        run_test()

    def test_stage_failure_handling(self):
        @patch("core.processors.SeparationStage.validate_input")
        @patch("core.processors.SeparationStage.execute")
        def run_test(mock_execute, mock_validate):
            mock_validate.return_value = True
            mock_execute.side_effect = Exception("Test error")

            stage = Mock()
            stage.name = "failing_stage"
            stage.processor_type = "test"
            stage.validate_input = Mock(return_value=True)
            stage.execute = Mock(side_effect=Exception("Test error"))

            self.pipeline.add_stage(stage)

            with self.assertRaises(Exception):
                self.pipeline.process(str(self.test_input))

            manifest = self.pipeline.get_job_status(
                list((Path(self.temp_dir) / "outputs").iterdir())[0].name
                if (Path(self.temp_dir) / "outputs").exists()
                else None
            )

        run_test()

    def test_stage_validation(self):
        stage = Mock()
        stage.name = "test_stage"
        stage.processor_type = "test"
        stage.validate_input = Mock(return_value=False)

        self.pipeline.add_stage(stage)

        with self.assertRaises(ValueError):
            self.pipeline.process(str(self.test_input))


class TestSeparatorFactory(unittest.TestCase):
    def test_register_separator(self):
        SeparatorFactory.register_separator("mock", MockSeparator)

        separators = SeparatorFactory.get_available_separators()
        self.assertIn("mock", separators)

    def test_create_separator(self):
        SeparatorFactory.register_separator("mock", MockSeparator)

        separator = SeparatorFactory.create_separator("mock")
        self.assertIsInstance(separator, MockSeparator)

    def test_unknown_separator(self):
        with self.assertRaises(ValueError):
            SeparatorFactory.create_separator("unknown_separator")


class TestProcessingManifest(unittest.TestCase):
    def test_manifest_to_dict(self):
        stage = ProcessingStage(
            name="test",
            processor_type="test",
            status="completed"
        )

        manifest = ProcessingManifest(
            job_id="test-id",
            input_file="test.wav",
            created_at="2024-01-15T10:00:00",
            version="1.0",
            stages=[stage],
            outputs={"test": "/path/to/output"},
            metadata={"test": "value"},
            status="completed"
        )

        manifest_dict = manifest.to_dict()

        self.assertEqual(manifest_dict["job_id"], "test-id")
        self.assertEqual(manifest_dict["status"], "completed")
        self.assertEqual(len(manifest_dict["stages"]), 1)

    def test_manifest_to_json(self):
        stage = ProcessingStage(
            name="test",
            processor_type="test",
            status="completed"
        )

        manifest = ProcessingManifest(
            job_id="test-id",
            input_file="test.wav",
            created_at="2024-01-15T10:00:00",
            version="1.0",
            stages=[stage],
            outputs={"test": "/path/to/output"},
            metadata={"test": "value"},
            status="completed"
        )

        json_str = manifest.to_json()

        self.assertIn("test-id", json_str)
        self.assertIn("completed", json_str)

        import json
        parsed = json.loads(json_str)
        self.assertEqual(parsed["job_id"], "test-id")


if __name__ == "__main__":
    unittest.main()