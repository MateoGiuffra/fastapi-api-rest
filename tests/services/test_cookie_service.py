import pytest
from fastapi import Response, Request
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from src.services.cookie_service import CookieService
from src.database.models.user import User
from src.core.config import settings

@pytest.fixture
def cookie_service():
    """Fixture para obtener una instancia de CookieService."""
    return CookieService()

@pytest.fixture
def sample_user():
    """Fixture para crear un usuario de ejemplo."""
    return User(id="a1b2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6", username="testuser", password="testpassword")

def test_create_token(cookie_service: CookieService, sample_user: User):
    """Prueba que el token JWT se crea correctamente."""
    token = cookie_service.create_token(sample_user)
    
    assert isinstance(token, str)
    
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    
    assert payload["sub"] == sample_user.username
    assert payload["id"] == sample_user.id
    
    # Verifica que la expiración está dentro de un rango razonable
    exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    expected_exp = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    assert abs((expected_exp - exp_time).total_seconds()) < 5 # Tolerancia de 5 segundos

def test_set_cookie(cookie_service: CookieService, sample_user: User):
    """Prueba que la cookie se establece correctamente en la respuesta."""
    mock_response = MagicMock(spec=Response)
    
    cookie_service.set_cookie(mock_response, sample_user)
    
    mock_response.set_cookie.assert_called_once()
    call_args = mock_response.set_cookie.call_args
    
    assert call_args.kwargs["key"] == "token"
    assert call_args.kwargs["httponly"] is True
    assert call_args.kwargs["samesite"] == "lax"
    assert call_args.kwargs["secure"] == settings.COOKIE_SECURE
    
    # Verifica que el valor de la cookie es un token válido
    token = call_args.kwargs["value"]
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["id"] == sample_user.id

def test_clean_cookies(cookie_service: CookieService):
    """Prueba que la cookie se elimina correctamente."""
    mock_response = MagicMock(spec=Response)
    
    cookie_service.clean_cookies(mock_response)
    
    mock_response.delete_cookie.assert_called_once_with(key="token", path="/")

def test_get_user_id_from_token_valid(cookie_service: CookieService, sample_user: User):
    """Prueba que se obtiene el ID de usuario desde un token válido en la request."""
    token = cookie_service.create_token(sample_user)
    mock_request = MagicMock(spec=Request)
    mock_request.cookies.get.return_value = token
    
    user_id = cookie_service.get_user_id_from_token(mock_request)
    
    assert user_id == sample_user.id

def test_get_user_id_from_token_invalid(cookie_service: CookieService):
    """Prueba que devuelve None si el token es inválido."""
    mock_request = MagicMock(spec=Request)
    mock_request.cookies.get.return_value = "invalid.token.string"
    
    user_id = cookie_service.get_user_id_from_token(mock_request)
    
    assert user_id is None

def test_get_user_id_from_token_expired(cookie_service: CookieService, sample_user: User):
    """Prueba que devuelve None si el token ha expirado."""
    # Creamos un token que expiró en el pasado
    cookie_service.expiration_time = -1 
    expired_token = cookie_service.create_token(sample_user)
    
    mock_request = MagicMock(spec=Request)
    mock_request.cookies.get.return_value = expired_token
    
    user_id = cookie_service.get_user_id_from_token(mock_request)
    
    assert user_id is None

def test_validate_token_invalid(cookie_service: CookieService):
    """Prueba que validate_token lanza una excepción para un token inválido."""
    with pytest.raises(JWTError):
        cookie_service.validate_token("invalid.token")

def test_validate_token_none(cookie_service: CookieService):
    """Prueba que validate_token lanza una excepción para un token nulo."""
    with pytest.raises(JWTError):
        cookie_service.validate_token(None)