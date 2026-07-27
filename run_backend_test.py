from backend.pipeline import run_feedback_pipeline


brief_path = "data/briefs/project_brief.txt"
submission_path = "data/submissions/learner_submission.txt"

report_path = run_feedback_pipeline(
    brief_file_path=brief_path,
    submission_file_path=submission_path
)

print(f"Feedback report generated successfully: {report_path}")