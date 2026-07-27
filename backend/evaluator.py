import json
from pathlib import Path
from openai import OpenAI

from backend.config import settings
from backend.models import EvaluationReport


client = OpenAI(api_key=settings.OPENAI_API_KEY)


SYSTEM_PROMPT = """
You are a mentor feedback assistant.

Compare the project brief with the learner submission.

VERY IMPORTANT:
You must check the learner submission fairly and semantically.
Do NOT depend only on exact headings such as "Task 1", "Activity 1", "LO1", "P1", etc.

The learner may:
- use "Activity" instead of "Task"
- use different headings
- answer in a different order
- combine two task answers under one heading
- answer the question without mentioning the task number
- write the answer directly without a clear heading

This must NOT automatically affect the learner negatively.

Your main job:
1. Identify every main task / question / requirement in the project brief.
2. For each task, search the WHOLE learner submission for relevant content.
3. Decide whether the learner has answered the requirement based on meaning, not heading match.
4. Give task-by-task feedback.
5. Mention missing or weak areas.
6. Suggest topics the learner should study more.
7. Give a score out of 10 for each task based on answer quality, not heading accuracy.

Coverage rules:
- If the learner clearly answers the requirement, mark it as addressed.
- If the learner attempts the requirement but the answer is incomplete, still mark it as addressed, but explain that it is partly or weakly covered.
- Do NOT say "not addressed" if there is any relevant answer in the submission.
- Use "not addressed" only when there is no relevant answer anywhere in the submission.
- If the answer is under a different heading, still count it as evidence.
- If the answer is in a different order, still count it as evidence.
- If the learner answers the question but does not use the task title, still count it as evidence.

When writing evidence:
- Do not say "No evidence" only because the heading is missing.
- Look for meaning across the whole submission.
- Evidence can be a short paraphrase.
- If the answer was found under another heading, mention that it was considered.

Scoring rules:
- Score should reflect how well the task requirement is answered.
- Do not reduce marks only because the learner used a different heading.
- Reduce marks only if the answer is incomplete, unclear, weak, missing evidence, lacks examples, lacks analysis, or does not fully meet the task.
- If the task is attempted but weak, give a low or moderate score, but do not mark it as not addressed.

Use simple, professional, mentor-friendly English.
Do not invent evidence.
If something is truly missing, clearly say it is missing.
Return only valid JSON.
"""


def limit_text(text: str, max_chars: int) -> str:
    """
    Limits very large text to avoid API token limit errors.
    Keeps the beginning and ending parts because both may contain useful details.
    """
    if len(text) <= max_chars:
        return text

    half = max_chars // 2

    return (
        text[:half]
        + "\n\n[TEXT SHORTENED BECAUSE FILE WAS TOO LARGE]\n\n"
        + text[-half:]
    )


def read_text_if_file_path(value: str) -> str:
    """
    Supports both direct text and file paths.
    If the value is a valid file path, read the file content.
    Otherwise, treat the value as normal text.
    """
    possible_path = Path(value)

    if possible_path.exists() and possible_path.is_file():
        suffix = possible_path.suffix.lower()

        if suffix == ".txt":
            return possible_path.read_text(encoding="utf-8", errors="ignore")

        if suffix in [".pdf", ".docx"]:
            from backend.file_reader import read_file_text
            return read_file_text(str(possible_path))

    return value


def evaluate_submission(project_brief: str, learner_submission: str) -> EvaluationReport:
    project_brief = read_text_if_file_path(project_brief)
    learner_submission = read_text_if_file_path(learner_submission)

    project_brief = limit_text(project_brief, settings.MAX_BRIEF_CHARS)
    learner_submission = limit_text(learner_submission, settings.MAX_SUBMISSION_CHARS)

    prompt = f"""
PROJECT BRIEF:
{project_brief}

LEARNER SUBMISSION:
{learner_submission}

Now complete the task-by-task evaluation.

Important:
- First detect the main tasks from the project brief.
- Then check the full learner submission for each task.
- Do not rely only on matching headings.
- If the learner uses "Activity" instead of "Task", still count it.
- If the learner answers under a different topic, still count it.
- If the learner answers in a different order, still count it.
- If the learner answers the question without a heading, still count it.
- Only mark is_addressed as false when there is no relevant answer anywhere in the submission.

For each task:
- task_number: use the task number or requirement number from the brief.
- task_title: use the task title or short requirement summary from the brief.
- is_addressed: true if the learner attempted or answered the requirement in any relevant way.
- evidence_from_submission: explain where/how the learner addressed it. If under a different heading, mention that.
- feedback: explain the quality of the answer fairly.
- improvement_suggestions: give practical ways to improve.
- topics_to_refer: list useful study topics.
- score_out_of_10: score based on answer quality, not heading match.

Return the result in this JSON structure only:

{{
  "learner_name": "Unknown",
  "overall_summary": "string",
  "total_tasks_detected": 0,
  "completed_tasks": 0,
  "missing_or_weak_tasks": 0,
  "task_feedback": [
    {{
      "task_number": "Task 1",
      "task_title": "string",
      "is_addressed": true,
      "evidence_from_submission": "string",
      "feedback": "string",
      "improvement_suggestions": ["string"],
      "topics_to_refer": ["string"],
      "score_out_of_10": 0
    }}
  ],
  "final_recommendations": ["string"]
}}
"""

    response = client.responses.create(
        model=settings.OPENAI_MODEL,
        instructions=SYSTEM_PROMPT,
        input=prompt,
        max_output_tokens=2500
    )

    raw_output = response.output_text

    try:
        parsed_json = json.loads(raw_output)
    except json.JSONDecodeError:
        parsed_json = extract_json_from_text(raw_output)

    return EvaluationReport(**parsed_json)


def extract_json_from_text(text: str) -> dict:
    """
    Backup method in case the model returns extra text around JSON.
    """
    start = text.find("{")
    end = text.rfind("}") + 1

    if start == -1 or end == 0:
        raise ValueError("Could not find valid JSON in model output.")

    json_text = text[start:end]
    return json.loads(json_text)