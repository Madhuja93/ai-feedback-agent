from backend.models import EvaluationReport


def generate_markdown_report(report: EvaluationReport) -> str:
    """
    Converts the evaluation result into a readable mentor feedback report.
    """

    lines = []

    lines.append("# Learner Submission Feedback Report")
    lines.append("")
    lines.append(f"**Learner Name:** {report.learner_name}")
    lines.append("")
    lines.append("## Overall Summary")
    lines.append(report.overall_summary)
    lines.append("")
    lines.append("## Task Completion Summary")
    lines.append(f"- Total tasks detected: {report.total_tasks_detected}")
    lines.append(f"- Completed tasks: {report.completed_tasks}")
    lines.append(f"- Missing or weak tasks: {report.missing_or_weak_tasks}")
    lines.append("")

    lines.append("## Task-by-Task Feedback")
    lines.append("")

    for task in report.task_feedback:
        lines.append(f"### {task.task_number}: {task.task_title}")
        lines.append("")
        lines.append(f"**Addressed:** {'Yes' if task.is_addressed else 'No'}")
        lines.append("")
        lines.append(f"**Evidence from submission:** {task.evidence_from_submission}")
        lines.append("")
        lines.append(f"**Feedback:** {task.feedback}")
        lines.append("")
        lines.append("**Improvement Suggestions:**")

        for suggestion in task.improvement_suggestions:
            lines.append(f"- {suggestion}")

        lines.append("")
        lines.append("**Topics to Refer More:**")

        for topic in task.topics_to_refer:
            lines.append(f"- {topic}")

        lines.append("")
        lines.append(f"**Score:** {task.score_out_of_10}/10")
        lines.append("")

    lines.append("## Final Recommendations")

    for recommendation in report.final_recommendations:
        lines.append(f"- {recommendation}")

    return "\n".join(lines)