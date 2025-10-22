import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status, Response, Request
from src.database.models.user import User
from src.repositories.user_repository import UserRepository
from src.services.cookie_service import CookieService
from src.services.user_service import UserService
from src.schemas.user import RegisterUserDTO, LoginUserDTO
from src.schemas.pagination import PaginationParams, PaginationResponse
import bcrypt

# --- Fixtures ---

@pytest.fixture
def user_repository_mock():
    """Mock para UserRepository."""
    return MagicMock(spec=UserRepository)

@pytest.fixture
def cookie_service_mock():
    """Mock para CookieService."""
    return MagicMock(spec=CookieService)

@pytest.fixture
def user_service(user_repository_mock: UserRepository, cookie_service_mock: CookieService):
    """Fixture para obtener una instancia de UserService con mocks."""
    return UserService(user_repository_mock, cookie_service_mock)

@pytest.fixture
def sample_user():
    """Fixture para crear un usuario de ejemplo."""
    return User(id="a1b2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6", username="testuser", password="hashed_password")

@pytest.fixture
def register_user_dto():
    """Fixture para un DTO de registro de usuario."""
    return RegisterUserDTO(username="newuser", password="password123")

@pytest.fixture
def login_user_dto():
    """Fixture para un DTO de login de usuario."""
    return LoginUserDTO(username="testuser", password="password")

@pytest.fixture
def mock_response():
    """Mock para fastapi.Response."""
    return MagicMock(spec=Response)

@pytest.fixture
def mock_request():
    """Mock para fastapi.Request."""
    return MagicMock(spec=Request)

# --- Tests for register method ---

def test_register_success(user_service: UserService, user_repository_mock: UserRepository, cookie_service_mock: CookieService, register_user_dto: RegisterUserDTO, mock_response: Response, sample_user: User):
    """Prueba el registro exitoso de un usuario."""
    user_repository_mock.user_does_exist.return_value = False
    
    # Mock bcrypt.gensalt and bcrypt.hashpw to control password hashing
    with patch('bcrypt.gensalt', return_value=b'mock_salt'), \
         patch('bcrypt.hashpw', return_value=b'mock_hashed_password'):
        
        user_repository_mock.save.return_value = sample_user
        
        registered_user = user_service.register(register_user_dto, mock_response)
        
        user_repository_mock.user_does_exist.assert_called_once_with(register_user_dto.username)
        user_repository_mock.save.assert_called_once()
        
        # Verify save was called with a User object containing the mocked hashed password
        saved_user_arg = user_repository_mock.save.call_args[0][0]
        assert isinstance(saved_user_arg, User)
        assert saved_user_arg.username == register_user_dto.username
        assert saved_user_arg.password == 'mock_hashed_password'
        
        cookie_service_mock.set_cookie.assert_called_once_with(mock_response, sample_user)
        assert registered_user == sample_user

def test_register_username_exists(user_service: UserService, user_repository_mock: UserRepository, register_user_dto: RegisterUserDTO, mock_response: Response):
    """Prueba el registro cuando el nombre de usuario ya existe."""
    user_repository_mock.user_does_exist.return_value = True
    
    with pytest.raises(HTTPException) as exc_info:
        user_service.register(register_user_dto, mock_response)
    
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert exc_info.value.detail == "Username already exists"
    user_repository_mock.user_does_exist.assert_called_once_with(register_user_dto.username)
    user_repository_mock.save.assert_not_called()
    
# --- Tests for login method ---
 
def test_login_success(user_service: UserService, user_repository_mock: UserRepository, cookie_service_mock: CookieService, login_user_dto: LoginUserDTO, mock_response: Response, sample_user: User):
    """Prueba el login exitoso de un usuario."""
    user_repository_mock.get_by_username.return_value = sample_user
    
    with patch('bcrypt.checkpw', return_value=True): # Mock checkpw to simulate correct password
        logged_in_user = user_service.login(login_user_dto, mock_response)
        
        user_repository_mock.get_by_username.assert_called_once_with(login_user_dto.username)
        cookie_service_mock.set_cookie.assert_called_once_with(mock_response, sample_user)
        assert logged_in_user == sample_user
 
def test_login_user_not_found(user_service: UserService, user_repository_mock: UserRepository, cookie_service_mock: CookieService, login_user_dto: LoginUserDTO, mock_response: Response):
    """Prueba el login cuando el usuario no existe."""
    user_repository_mock.get_by_username.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        user_service.login(login_user_dto, mock_response)
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "User not found"
    user_repository_mock.get_by_username.assert_called_once_with(login_user_dto.username)
    cookie_service_mock.set_cookie.assert_not_called()
 
def test_login_invalid_password(user_service: UserService, user_repository_mock: UserRepository, cookie_service_mock: CookieService, login_user_dto: LoginUserDTO, mock_response: Response, sample_user: User):
    """Prueba el login con una contraseña inválida."""
    user_repository_mock.get_by_username.return_value = sample_user
    
    with patch('bcrypt.checkpw', return_value=False): # Mock checkpw to simulate incorrect password
        with pytest.raises(HTTPException) as exc_info:
            user_service.login(login_user_dto, mock_response)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Invalid password"
        user_repository_mock.get_by_username.assert_called_once_with(login_user_dto.username)
        cookie_service_mock.set_cookie.assert_not_called()

# --- Tests for delete_all method ---

def test_delete_all(user_service: UserService, user_repository_mock: UserRepository):
    """Prueba que el método delete_all llama al repositorio."""
    user_service.delete_all()
    user_repository_mock.delete_all.assert_called_once()

# --- Tests for logout method ---

def test_logout(user_service: UserService, cookie_service_mock: CookieService, mock_response: Response):
    """Prueba que el método logout llama al servicio de cookies."""
    user_service.logout(mock_response)
    cookie_service_mock.clean_cookies.assert_called_once_with(mock_response)

# --- Tests for get_current_user method ---

def test_get_current_user_success(user_service: UserService, cookie_service_mock: CookieService, user_repository_mock: UserRepository, mock_request: Request, sample_user: User):
    """Prueba la obtención del usuario actual exitosamente."""
    cookie_service_mock.get_user_id_from_token.return_value = sample_user.id
    user_repository_mock.get_by_id.return_value = sample_user
    
    current_user = user_service.get_current_user(mock_request)
    
    cookie_service_mock.get_user_id_from_token.assert_called_once_with(mock_request)
    user_repository_mock.get_by_id.assert_called_once_with(sample_user.id)
    assert current_user == sample_user

def test_get_current_user_no_token_or_user_not_found(user_service: UserService, cookie_service_mock: CookieService, user_repository_mock: UserRepository, mock_request: Request):
    """Prueba la obtención del usuario actual cuando no hay token o el usuario no se encuentra."""
    cookie_service_mock.get_user_id_from_token.return_value = None # Simulate no token or invalid token
    user_repository_mock.get_by_id.return_value = None # Simulate user not found when get_by_id is called with None
    
    with pytest.raises(HTTPException) as exc_info:
        user_service.get_current_user(mock_request)
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "User with id None not found" # get_user_by_id is called with None
    cookie_service_mock.get_user_id_from_token.assert_called_once_with(mock_request)
    user_repository_mock.get_by_id.assert_called_once_with(None) # Ensure get_by_id was called with None

# --- Tests for get_user_by_id method ---

def test_get_user_by_id_success(user_service: UserService, user_repository_mock: UserRepository, sample_user: User):
    """Prueba la obtención de un usuario por ID exitosamente."""
    user_repository_mock.get_by_id.return_value = sample_user
    
    found_user = user_service.get_user_by_id(sample_user.id)
    
    user_repository_mock.get_by_id.assert_called_once_with(sample_user.id)
    assert found_user == sample_user

def test_get_user_by_id_not_found(user_service: UserService, user_repository_mock: UserRepository):
    """Prueba la obtención de un usuario por ID cuando no se encuentra."""
    user_repository_mock.get_by_id.return_value = None
    non_existent_id = "non-existent-id"
    
    with pytest.raises(HTTPException) as exc_info:
        user_service.get_user_by_id(non_existent_id)
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == f"User with id {non_existent_id} not found"
    user_repository_mock.get_by_id.assert_called_once_with(non_existent_id)

# --- Tests for list_users method ---

def test_list_users_default_pagination(user_service: UserService, user_repository_mock: UserRepository, sample_user: User):
    """Prueba la lista de usuarios con paginación por defecto."""
    user_repository_mock.get_users.return_value = [sample_user]
    user_repository_mock.get_count.return_value = 1
    
    params = PaginationParams()
    response = user_service.list_users(params)
    
    user_repository_mock.get_users.assert_called_once_with(0, 10) # offset = (page-1)*limit
    user_repository_mock.get_count.assert_called_once()
    
    assert isinstance(response, PaginationResponse)
    assert response.results == [sample_user]
    assert response.page == 1
    assert response.limit == 10
    assert response.total_results == 1
    assert response.total_pages == 1 # (1 + 10 - 1) // 10 = 1

def test_list_users_custom_pagination(user_service: UserService, user_repository_mock: UserRepository, sample_user: User):
    """Prueba la lista de usuarios con paginación personalizada."""
    user_repository_mock.get_users.return_value = [sample_user]
    user_repository_mock.get_count.return_value = 10
    
    params = PaginationParams(page=2, limit=5)
    response = user_service.list_users(params)
    
    user_repository_mock.get_users.assert_called_once_with(5, 5) # offset = (2-1)*5 = 5
    user_repository_mock.get_count.assert_called_once()
    
    assert isinstance(response, PaginationResponse)
    assert response.results == [sample_user]
    assert response.page == 2
    assert response.limit == 5
    assert response.total_results == 10
    assert response.total_pages == 2 # (10 + 5 - 1) // 5 = 2

def test_list_users_empty_results(user_service: UserService, user_repository_mock: UserRepository):
    """Prueba la lista de usuarios cuando no hay resultados."""
    user_repository_mock.get_users.return_value = []
    user_repository_mock.get_count.return_value = 0
    
    params = PaginationParams()
    response = user_service.list_users(params)
    
    user_repository_mock.get_users.assert_called_once_with(0, 10)
    user_repository_mock.get_count.assert_called_once()
    
    assert isinstance(response, PaginationResponse)
    assert response.results == []
    assert response.page == 1
    assert response.limit == 10
    assert response.total_results == 0
    assert response.total_pages == 0 # (0 + 10 - 1) // 10 = 0