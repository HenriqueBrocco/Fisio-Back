# NOTE: Por enquanto, "Paciente" é um User com role="PATIENT".
# Futuro: criar tabela patient_profile se precisarmos de dados clínicos extras.

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from pydantic import ConfigDict

class PatientCreate(BaseModel):
    name: str = Field(..., max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)

class PatientUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=120)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=128)

class PatientOut(BaseModel):
    id: str
    role: str
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)
