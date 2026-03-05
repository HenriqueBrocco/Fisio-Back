# NOTE: Por enquanto, "Paciente" é um User com role="PATIENT".
# Futuro: criar tabela patient_profile se precisarmos de dados clínicos extras.


from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PatientCreate(BaseModel):
    name: str = Field(..., max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class PatientUpdate(BaseModel):
    name: str | None = Field(None, max_length=120)
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=6, max_length=128)


class PatientOut(BaseModel):
    id: str
    role: str
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)
