from pydantic import BaseModel, EmailStr, Field

from app.db.models.user import ROLES


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, description="Minimum 8 characters")
    role: str
    phone_number: str | None = None
    institute_id: str | None = None

    def validate_role(self):
        if self.role not in ROLES:
            raise ValueError(f"role must be one of {ROLES}")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str
    name: str
    institute_id: str | None = None
