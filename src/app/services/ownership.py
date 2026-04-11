from app.models.usuario import Usuario


class OwnershipError(Exception):
    pass


def ensure_pro_owns_patient(pro: Usuario, patient: Usuario) -> None:
    if pro.perfil != "PRO":
        raise OwnershipError("Sem permissão")
    if patient.usuario_pro_id != pro.id:
        raise OwnershipError("Sem permissão para este paciente")
