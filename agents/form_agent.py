from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class Contact(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    phone: Optional[str] = Field(None, pattern=r"^[0-9+\\-\\s]{7,}$")

SYSTEM_PROMPT = """You are the ESILV Form Agent. Your job is to collect name, email, and phone.
- Ask one question at a time.
- Confirm values back to the user.
- If phone is not provided, it's optional.
- Validate email format; ask to correct if invalid.
- When all fields collected, say 'FORM_COMPLETE' and present the summary as JSON with keys: name, email, phone."""

class FormAgent:
    def __init__(self, llm_client):
        self.llm = llm_client

    def next(self, transcript: str) -> str:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": transcript}
        ]
        return self.llm.chat(messages)