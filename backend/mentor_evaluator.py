from openai import OpenAI
import json
import re


client = OpenAI()


def classify_grade(score_out_of_100):
    """
    Deterministic grade classification.

    Requested grading rule:
    WHEN score <= 49 THEN 'FAIL'
    WHEN score < 60 THEN 'PASS'
    WHEN score < 75 THEN 'MERIT'
    ELSE 'DISTINCTION'
    """

    if score_out_of_100 is None:
        return "Not enough evidence available"

    try:
        score = float(score_out_of_100)
    except (TypeError, ValueError):
        return "Not enough evidence available"

    if score <= 49:
        return "Fail"

    if score < 60:
        return "Pass"

    if score < 75:
        return "Merit"

    return "Distinction"


def next_grade_target(current_grade: str) -> str:
    if current_grade == "Fail":
        return "Pass"
    if current_grade == "Pass":
        return "Merit"
    if current_grade == "Merit":
        return "Distinction"
    if current_grade == "Distinction":
        return "stronger Distinction-level quality"
    return "Not enough evidence available"


def extract_json_from_text(text: str) -> dict:
    start = text.find("{")
    end = text.rfind("}") + 1

    if start == -1 or end == 0:
        raise ValueError("Could not find valid JSON in model output.")

    return json.loads(text[start:end])


def estimate_report_score_from_feedback(written_feedback: str) -> dict:
    """
    Uses the written feedback only to estimate the report score out of 100.
    The grade itself is NOT decided by the model.
    The grade is calculated later by classify_grade().
    """

    prompt = f"""
You are an academic mentor.

Estimate the written report score out of 100 using ONLY the written feedback report.

Important:
- Do not use presentation feedback.
- Do not decide Fail, Pass, Merit, or Distinction.
- Only estimate the report score out of 100.
- Consider task coverage, answer depth, evidence, analysis, clarity, structure, references, and recommendations.
- If the learner attempted a task, do not treat it as missing.
- If exact evidence is limited, give a cautious score.

Return only valid JSON in this exact structure:

{{
  "report_score_out_of_100": 0,
  "score_explanation": "string",
  "caution_note": "string"
}}

Written Feedback Report:
{written_feedback}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    raw_output = response.output_text

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        parsed = extract_json_from_text(raw_output)

    score = parsed.get("report_score_out_of_100")

    try:
        score = float(score)
        score = max(0, min(100, score))
    except (TypeError, ValueError):
        score = None

    return {
        "report_score_out_of_100": score,
        "score_explanation": parsed.get("score_explanation", "Not enough evidence available."),
        "caution_note": parsed.get("caution_note", "This score is an estimated mentor judgement based on the written feedback.")
    }


def remove_duplicate_overall_grade_section(text: str) -> str:
    """
    Safety cleanup:
    If the model accidentally creates its own Overall Grade section,
    remove it because section 2 is created deterministically in Python.
    """

    pattern = r"\n?##\s*2\.\s*Overall Grade.*?(?=\n##\s*3\.|\Z)"
    return re.sub(pattern, "\n", text, flags=re.DOTALL | re.IGNORECASE).strip()


def generate_mentor_feedback_pack(
    written_feedback: str,
    presentation_feedback: str,
    mentor_name: str = "Unknown"
) -> str:
    """
    Generates the final mentor pack.

    Important:
    - Overall grade is based on the written report only.
    - Report score is estimated out of 100 from the written feedback.
    - Grade classification is deterministic Python logic, not model judgement.
    - Therefore, 62/100 will always be Merit, not Pass.
    """

    if not written_feedback:
        return """
# Full Mentor Feedback Pack

The written feedback report is required before generating this pack.
"""

    if not presentation_feedback:
        presentation_feedback = "Presentation feedback was not provided."

    score_data = estimate_report_score_from_feedback(written_feedback)
    report_score = score_data["report_score_out_of_100"]
    report_grade = classify_grade(report_score)
    target_grade = next_grade_target(report_grade)

    if mentor_name and mentor_name != "Unknown":
        sign_off_name = mentor_name
    else:
        sign_off_name = "[Your Mentor]"

    if report_score is None:
        score_display = "Not enough evidence available"
    else:
        score_display = f"{report_score:.0f}/100"

    overall_grade_section = f"""
## 2. Overall Grade

- Report score: {score_display}
- Overall grade: {report_grade}
- Grade band used:
  - 0–49 = Fail
  - 50–59 = Pass
  - 60–74 = Merit
  - 75–100 = Distinction
- Score explanation: {score_data["score_explanation"]}
- Caution note: {score_data["caution_note"]}
"""

    prompt = f"""
You are an academic mentor assistant.

Create the Full Mentor Feedback Pack using the written report feedback and presentation feedback.

VERY IMPORTANT:
- Do NOT create section 2. Overall Grade.
- Section 2 will be inserted separately by the system.
- Do NOT change the report score or grade.
- Overall grade is based on the written report only.
- Presentation feedback can be used only for presentation notes and suggested marking comments.
- Do not say a task is not covered if the learner attempted it.
- Use simple professional English.
- Do not invent evidence.

Known report score and grade:
Report score: {score_display}
Overall grade: {report_grade}
Next grade target: {target_grade}

Grade bands:
0-49 = Fail
50-59 = Pass
60-74 = Merit
75-100 = Distinction

Create these sections only:

# Full Mentor Feedback Pack

## 1. Mentor Summary
Write 5 to 7 bullet points for the mentor.
Focus mainly on the written report.
Mention presentation only if it affects communication or delivery.

## 3. How to Improve
Base this section mainly on the written report.
If the grade is Fail, explain how to reach Pass.
If the grade is Pass, explain how to reach Merit.
If the grade is Merit, explain how to reach Distinction.
If the grade is Distinction, explain how to make the work even stronger.

Give 5 to 7 practical improvement actions.

## 4. Overall Performance Decision
Choose one:
- Needs Improvement
- Satisfactory
- Good
- Very Good
- Excellent

Explain briefly based mainly on the written report.

## 5. Missing or Weak Requirements Checklist
Create a checklist:
- [ ] Weak / missing requirement - explanation

Do not mark a task as missing if it was attempted.

## 6. Brief vs Submission Coverage Table
Create a task-by-task table based on the written report.

Use this exact table:
| Main Task / Requirement | Coverage Status | Evidence From Report Feedback | Mentor Note |
|---|---|---|---|

Coverage Status must be:
Fully covered / Mostly covered / Partly covered / Weakly covered / Not covered / Not enough evidence available

## 7. Suggested Marking Table
Use both written report and presentation feedback.

Use this exact table:
| Area | Evidence Considered | Suggested Judgement | Mentor Note |
|---|---|---|---|

Put report areas first and presentation areas after.

## 8. Learner Action Plan
Base this mainly on the written report.

Use this exact table:
| Priority | Action Required | Why This Matters |
|---|---|---|

## 9. Learner-Friendly Feedback Message
Write a ready-to-send message.
Base it mainly on the written report.
Mention:
- Report score: {score_display}
- Overall grade: {report_grade}
- Main improvements needed to reach {target_grade}

End exactly with:

Best regards,
{sign_off_name}

## 10. Mentor Follow-Up Questions
List 5 useful mentor questions.

Written Feedback Report:
{written_feedback}

Presentation Feedback Report:
{presentation_feedback}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    generated_pack = remove_duplicate_overall_grade_section(response.output_text)

    # Insert deterministic section 2 after section 1, before section 3.
    if "## 3. How to Improve" in generated_pack:
        final_pack = generated_pack.replace(
            "## 3. How to Improve",
            overall_grade_section.strip() + "\n\n## 3. How to Improve",
            1
        )
    else:
        final_pack = generated_pack + "\n\n" + overall_grade_section.strip()

    return final_pack
