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