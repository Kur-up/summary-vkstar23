from pydantic import BaseModel


class UserModel(BaseModel):
    user_id: int
    onboarding: bool
    is_test_passed: bool
    attempts: int
    first_name: str
    last_name: str

    class Config:
        orm_mode = True
