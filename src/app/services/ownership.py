from app.models.user import User


class OwnershipError(Exception):
    pass


def ensure_pro_owns_patient(pro: User, patient: User) -> None:
    if pro.role != "PRO":
        raise OwnershipError("Sem permissão")
    if patient.pro_owner_id != pro.id:
        raise OwnershipError("Sem permissão para este paciente")
