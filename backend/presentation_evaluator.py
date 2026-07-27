from openai import OpenAI


client = OpenAI()


PRESENTATION_CRITERIA = [
    "Use of Visuals",
    "Clarity & Structure",
    "Key Points Coverage",
    "Understanding",
    "Language & Communication",
    "Time Management",
    "Original Thinking",
    "Q&A Handling"
]


def evaluate_presentation(transcript_text: str) -> str:
    """
    Evaluates learner presentation based on transcript text.
    This version does NOT grade the presentation.
    It gives qualitative feedback only.
    """

    if not transcript_text or len(transcript_text.strip()) < 50:
        return """
## Presentation Feedback

Presentation transcript was not provided or did not contain enough text for evaluation.

**Presentation Review:** Not enough evidence available
"""

    criteria_text = "\n".join([f"- {criterion}" for criterion in PRESENTATION_CRITERIA])

    prompt = f"""
You are an academic assessor reviewing a learner presentation transcript.

Assess the learner's presentation based on the following criteria:

{criteria_text}

IMPORTANT RULES:
- Do not give a score.
- Do not give a grade.
- Do not write "Overall Presentation Score".
- Use only evidence visible in the transcript.
- If something cannot be judged from the transcript, say it clearly.
- Use simple professional English.
- Be fair and not too harsh.
- Format the answer in markdown.

For each criterion, provide:
1. Coverage status:
   - Strong
   - Satisfactory
   - Needs improvement
   - Not enough evidence available
2. Brief feedback
3. One improvement point

Then provide:
- Strengths
- Areas for Improvement
- Final Presentation Feedback

Presentation Transcript:
{transcript_text}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text
