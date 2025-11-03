import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


@dataclass
class ProcessingStage:
    name: str
    processor_type: str
    status: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    duration_seconds: Optional[float] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class ProcessingManifest:
    job_id: str
    input_file: str
    created_at: str
    version: str
    stages: List[ProcessingStage]
    outputs: Dict[str, str]
    metadata: Dict
    status: str

    def to_dict(self):
        return {
            **asdict(self),
            "stages": [s.to_dict() for s in self.stages]
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class PipelineStage(ABC):
    def __init__(self, name: str, processor_type: str):
        self.name = name
        self.processor_type = processor_type
        self.logger = logging.getLogger(f"stage.{name}")

    @abstractmethod
    def execute(self, input_path: str, output_dir: str) -> Dict[str, str]:
        pass

    @abstractmethod
    def validate_input(self, input_path: str) -> bool:
        pass


class AudioPipeline:
    def __init__(self, output_base_dir: str = "./outputs"):
        self.stages: List[PipelineStage] = []
        self.output_base_dir = Path(output_base_dir)
        self.output_base_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("pipeline")

    def add_stage(self, stage: PipelineStage) -> None:
        self.stages.append(stage)
        self.logger.info(f"Added stage: {stage.name}")

    def process(self, input_file: str) -> ProcessingManifest:
        job_id = str(uuid4())
        job_dir = self.output_base_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        manifest = ProcessingManifest(
            job_id=job_id,
            input_file=input_file,
            created_at=datetime.utcnow().isoformat(),
            version="1.0",
            stages=[],
            outputs={},
            metadata={"processor_count": len(self.stages)},
            status="processing"
        )

        for stage in self.stages:
            stage_record = ProcessingStage(
                name=stage.name,
                processor_type=stage.processor_type,
                status="pending"
            )

            try:
                if not stage.validate_input(input_file):
                    raise ValueError(f"Invalid input for stage {stage.name}")

                stage_record.status = "processing"
                stage_record.started_at = datetime.utcnow().isoformat()

                outputs = stage.execute(input_file, str(job_dir))
                manifest.outputs.update(outputs)

                stage_record.status = "completed"
                stage_record.completed_at = datetime.utcnow().isoformat()

                self.logger.info(f"Stage {stage.name} completed successfully")

            except Exception as e:
                stage_record.status = "failed"
                stage_record.error = str(e)
                stage_record.completed_at = datetime.utcnow().isoformat()
                manifest.status = "failed"
                self.logger.error(f"Stage {stage.name} failed: {str(e)}")
                raise

            finally:
                if stage_record.started_at and stage_record.completed_at:
                    from datetime import datetime as dt
                    start = dt.fromisoformat(stage_record.started_at)
                    end = dt.fromisoformat(stage_record.completed_at)
                    stage_record.duration_seconds = (end - start).total_seconds()

                manifest.stages.append(stage_record)

        manifest.status = "completed"

        manifest_path = job_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            f.write(manifest.to_json())

        self.logger.info(f"Pipeline completed. Job ID: {job_id}")
        return manifest

    def get_job_status(self, job_id: str) -> Optional[ProcessingManifest]:
        manifest_path = self.output_base_dir / job_id / "manifest.json"
        if manifest_path.exists():
            with open(manifest_path, "r") as f:
                data = json.load(f)
                return ProcessingManifest(
                    job_id=data["job_id"],
                    input_file=data["input_file"],
                    created_at=data["created_at"],
                    version=data["version"],
                    stages=[ProcessingStage(**s) for s in data["stages"]],
                    outputs=data["outputs"],
                    metadata=data["metadata"],
                    status=data["status"]
                )
        return None

    def get_outputs(self, job_id: str) -> Optional[Dict[str, str]]:
        manifest = self.get_job_status(job_id)
        if manifest:
            return manifest.outputs
        return None