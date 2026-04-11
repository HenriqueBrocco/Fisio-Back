# NOTE: Por enquanto, "Paciente" é um User com role="PATIENT".
# Futuro: criar tabela patient_profile se precisarmos de dados clínicos extras.


from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PacienteCreate(BaseModel):
    nome: str = Field(..., max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class PacienteUpdate(BaseModel):
    nome: str | None = Field(None, max_length=120)
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=6, max_length=128)


class PacienteOut(BaseModel):
    id: str
    perfil: str
    nome: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)
