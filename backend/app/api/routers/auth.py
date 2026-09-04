from __future__ import annotations
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field

try:
    from app.services.auth_service import auth_service
except ImportError:
    from backend.app.services.auth_service import auth_service

router = APIRouter(prefix="/api/auth", tags=["Authentication & User Management"])


class RegisterRequest(BaseModel):
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", description="Correo electrónico del usuario")
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario")
    password: str = Field(..., min_length=6, description="Contraseña (mínimo 6 caracteres)")
    full_name: str = Field(..., min_length=2, max_length=100, description="Nombre completo")
    role: Optional[str] = Field("viewer", description="Rol del usuario (admin, viewer)")


class LoginRequest(BaseModel):
    username_or_email: str = Field(..., description="Nombre de usuario o correo electrónico")
    password: str = Field(..., description="Contraseña")


def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Dependency that extracts and validates Bearer token from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Autenticación requerida. Token no proporcionado o formato inválido (use Bearer <token>)."
        )

    token = authorization.split(" ", 1)[1].strip()
    payload = auth_service.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Token inválido o expirado. Por favor inicie sesión nuevamente."
        )

    user = auth_service.get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado.")

    return user


def get_optional_current_user(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """Dependency that extracts user if valid token provided, but doesn't fail if missing."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        token = authorization.split(" ", 1)[1].strip()
        payload = auth_service.verify_token(token)
        if payload:
            return auth_service.get_user_by_id(payload["sub"])
    except Exception:
        pass
    return None


@router.post("/register")
async def register(req: RegisterRequest) -> Dict[str, Any]:
    """Registers a new user account."""
    try:
        result = auth_service.register(
            email=req.email,
            username=req.username,
            password=req.password,
            full_name=req.full_name,
            role=req.role or "viewer"
        )
        return {
            "status": "success",
            "message": "Usuario registrado exitosamente.",
            "user": result["user"],
            "token": result["token"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el servidor al registrar: {str(e)}")


@router.post("/login")
async def login(req: LoginRequest) -> Dict[str, Any]:
    """Authenticates a user and returns an access token."""
    result = auth_service.authenticate(req.username_or_email, req.password)
    if not result:
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas. Verifique su usuario o contraseña."
        )

    return {
        "status": "success",
        "message": "Inicio de sesión exitoso.",
        "user": result["user"],
        "token": result["token"]
    }


@router.get("/me")
async def get_me(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Returns the profile of the currently authenticated user."""
    return {
        "status": "success",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"],
            "created_at": user["created_at"]
        }
    }
