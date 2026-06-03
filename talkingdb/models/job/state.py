from enum import Enum


class JobState(str, Enum):
    """Lifecycle state of an ingestion job.

    ``state`` represents the overall lifecycle position of a job,
    while ``stage`` represents the currently executing processing step.
    The two concepts are intentionally independent.
    """

    QUEUED = "QUEUED"
    ONGOING = "ONGOING"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

    @classmethod
    def terminal(cls) -> set["JobState"]:
        """States from which no further transition is allowed."""
        return {cls.CANCELLED, cls.COMPLETED, cls.FAILED}

    def is_terminal(self) -> bool:
        return self in self.terminal()
