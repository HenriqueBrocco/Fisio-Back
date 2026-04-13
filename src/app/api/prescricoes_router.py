from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.api.dependencias import get_usuario_atual, exigir_permissao
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.prescricao import (
    PrescricaoCreate,
    PrescricaoOut,
    PrescricaoUpdate,
    ConfigParametrosUpdate,
    ExercicioConfigCreate,
    ExercicioConfigOut,
)
from app.schemas.sessao import SessaoOut
from app.services.prescricoes_service import (
    BadRequestError,
    NotFoundError,
    create_assignment,
    get_assignment,
    list_assignments,
    update_assignment,
    create_exercise_config,
    get_config,
    list_configs,
    update_config_params
    
)
from app.services.sessoes_paciente_service import create_session_from_assignment

prescricoes_router = APIRouter(prefix="/prescricoes", tags=["Prescrições"])


# -------- Configs Exercícios --------


@prescricoes_router.post("/configs", response_model=ExercicioConfigOut, status_code=status.HTTP_201_CREATED)
def create_config_endpoint(
    payload: ExercicioConfigCreate,
    db: DBSession = Depends(get_db),
    _=Depends(exigir_permissao("PRO")),
    user: Usuario = Depends(get_usuario_atual),
):
    try:
        return create_exercise_config(db, payload.exercicio_id, payload.paciente_usuario_id, payload.parametros, user)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))


@prescricoes_router.get("/configs", response_model=list[ExercicioConfigOut])
def list_configs_endpoint(
    db: DBSession = Depends(get_db),
    user: Usuario = Depends(get_usuario_atual),
    patient_user_id: str | None = None,
    exercise_id: int | None = None,
):
    if user.perfil == "PATIENT":
        patient_user_id = user.id

    return list_configs(db, patient_user_id, exercise_id)


@prescricoes_router.get("/configs/{config_id}", response_model=ExercicioConfigOut)
def get_config_endpoint(config_id: int, db: DBSession = Depends(get_db)):
    try:
        return get_config(db, config_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    

@prescricoes_router.put("/configs/{config_id}/params", response_model=ExercicioConfigOut)
def update_config_params_endpoint(
    config_id: int,
    payload: ConfigParametrosUpdate,
    db: DBSession = Depends(get_db),
    _=Depends(exigir_permissao("PRO")),
    user: Usuario = Depends(get_usuario_atual),
):
    try:
        return update_config_params(db, user, config_id, payload.parametros)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))



# -------- Prescrições --------


@prescricoes_router.post("", response_model=PrescricaoOut, status_code=status.HTTP_201_CREATED)
def create_assignment_endpoint(
    payload: PrescricaoCreate,
    db: DBSession = Depends(get_db),
    _=Depends(exigir_permissao("PRO")),
    user: Usuario = Depends(get_usuario_atual),
):
    try:
        return create_assignment(
            db=db,
            patient_user_id=payload.paciente_usuario_id,
            exercise_id=payload.exercicio_id,
            config_id=payload.config_id,
            schedule=payload.frequencia,
            active=payload.ativo,
            pro_user=user,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))


@prescricoes_router.get("", response_model=list[PrescricaoOut])
def list_assignments_endpoint(
    db: DBSession = Depends(get_db),
    user: Usuario = Depends(get_usuario_atual),
    patient_user_id: str | None = None,
):
    return list_assignments(db, user, patient_user_id)


@prescricoes_router.get("/{assignment_id}", response_model=PrescricaoOut)
def get_assignment_endpoint(
    assignment_id: int,
    db: DBSession = Depends(get_db),
    user: Usuario = Depends(get_usuario_atual),
):
    try:
        a = get_assignment(db, user, assignment_id)
        return a
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        # aqui usamos 403 para permissão
        if str(e) == "Sem permissão":
            raise HTTPException(status_code=403, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@prescricoes_router.put("/{assignment_id}", response_model=PrescricaoOut)
def update_assignment_endpoint(
    assignment_id: int,
    payload: PrescricaoUpdate,
    db: DBSession = Depends(get_db),
    _=Depends(exigir_permissao("PRO")),
):
    try:
        return update_assignment(
            db=db,
            assignment_id=assignment_id,
            schedule=payload.frequencia,
            active=payload.ativo,
            config_id=payload.config_id,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))


@prescricoes_router.post("/{assignment_id}/sessions", response_model=SessaoOut, status_code=status.HTTP_201_CREATED)
def create_session_from_assignment_endpoint(assignment_id: int, db: DBSession = Depends(get_db), user: Usuario = Depends(get_usuario_atual),):
    try:
        return create_session_from_assignment(db, user, assignment_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        # permissão
        if str(e) == "Sem permissão":
            raise HTTPException(status_code=403, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
