from pathlib import Path
from backend.file_reader import read_file_text
from backend.evaluator import evaluate_submission
from backend.presentation_evaluator import evaluate_presentation

def evaluation_report_to_markdown(report):
    """
    Converts the output of evaluate_submission() into readable markdown.
    Works safely even if the report is an object or a string.
    """
    # If report is already a string, use as is
    if isinstance(report, str):
        return report

    lines = []

    learner_name = getattr(report, "learner_name", "Unknown")
    overall_summary = getattr(report, "overall_summary", "")
    tasks = getattr(report, "task_feedback", [])
    final_recs = getattr(report, "final_recommendations", [])

    # Header
    lines.append(f"# Written Feedback Report")
    lines.append("")
    lines.append(f"**Learner Name:** {learner_name}")
    lines.append(f"**Overall Summary:** {overall_summary}")
    lines.append("")

    # Task feedback
    if tasks:
        lines.append("## Task Feedback")
        for t in tasks:
            task_number = getattr(t, "task_number", "")
            task_title = getattr(t, "task_title", "")
            score = getattr(t, "score_out_of_10", "")
            addressed = getattr(t, "is_addressed", "")
            evidence = getattr(t, "evidence_from_submission", "")
            feedback = getattr(t, "feedback", "")
            improvements = getattr(t, "improvement_suggestions", [])
            topics = getattr(t, "topics_to_refer", [])

            lines.append(f"### {task_number} - {task_title}")
            lines.append(f"- Score: {score}/10")
            lines.append(f"- Addressed: {'Yes' if addressed else 'No'}")
            lines.append(f"- Evidence: {evidence}")
            lines.append(f"- Feedback: {feedback}")
            if improvements:
                lines.append(f"- Improvement Suggestions: {', '.join(improvements)}")
            if topics:
                lines.append(f"- Topics to Refer: {', '.join(topics)}")
            lines.append("")

    # Final recommendations
    if final_recs:
        lines.append("## Final Recommendations")
        for r in final_recs:
            lines.append(f"- {r}")

    return "\n".join(lines)


def run_feedback_pipeline(
    brief_file_path: str,
    submission_file_path: str,
    output_folder: str,
    output_file_name: str,
    presentation_transcript_file_path: str = None
) -> str:
    """
    Runs the feedback generation pipeline.
    Generates written submission feedback and optional presentation feedback.
    """

    Path(output_folder).mkdir(parents=True, exist_ok=True)

    # -----------------------------
    # Written submission evaluation
    # -----------------------------
    evaluation_report = evaluate_submission(brief_file_path, submission_file_path)
    evaluation_markdown = evaluation_report_to_markdown(evaluation_report)

    # -----------------------------
    # Optional presentation evaluation
    # -----------------------------
    presentation_feedback = ""
    if presentation_transcript_file_path:
        transcript_text = read_file_text(presentation_transcript_file_path)
        presentation_feedback = evaluate_presentation(transcript_text)

    # -----------------------------
    # Combine reports
    # -----------------------------
    final_report = evaluation_markdown
    if presentation_feedback:
        final_report += "\n\n---\n\n"
        final_report += presentation_feedback

    # -----------------------------
    # Save final report
    # -----------------------------
    output_path = Path(output_folder) / output_file_name
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(final_report)

    return str(output_path)