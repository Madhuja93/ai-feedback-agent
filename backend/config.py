import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    OPENAI_API_KEY = os.getenv("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")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Keep text small to avoid rate limit errors
    MAX_BRIEF_CHARS = int(os.getenv("MAX_BRIEF_CHARS", "6000"))
    MAX_SUBMISSION_CHARS = int(os.getenv("MAX_SUBMISSION_CHARS", "12000"))


settings = Settings()