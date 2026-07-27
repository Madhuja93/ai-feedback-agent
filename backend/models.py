from pydantic import BaseModel, Field
from typing import List


class TaskFeedback(BaseModel):
    task_number: str = Field(description="Task number from the project brief")
    task_title: str = Field(description="Short title of the task")
    is_addressed: bool = Field(description="Whether the learner addressed this task")
    evidence_from_submission: str = Field(description="Evidence found in learner submission")
    feedback: str = Field(description="Task-specific feedback")
    improvement_suggestions: List[str] = Field(description="Suggestions to improve this task")
    topics_to_refer: List[str] = Field(description="Topics the learner should study more")
    score_out_of_10: int = Field(description="Score for this task out of 10")


class EvaluationReport(BaseModel):
    learner_name: str = Field(description="Learner name if available, otherwise Unknown")
    overall_summary: str = Field(description="Overall feedback summary")
    total_tasks_detected: int = Field(description="Number of tasks found in project brief")
    completed_tasks: int = Field(description="Number of tasks properly addressed")
    missing_or_weak_tasks: int = Field(description="Number of missing or weak tasks")
    task_feedback: List[TaskFeedback] = Field(description="Task-by-task feedback")
    final_recommendations: List[str] = Field(description="Overall improvement recommendations")