from tests.routers.users import *

def test_register_new_user_successfully(client):
    """
    Test de integración: Prueba que el endpoint /auth/register
    registra un nuevo usuario correctamente.
    """
    response = client.post(
        "/auth/register",  
        json=valid_user
    )
    data = response.json()
 
    assert response.status_code == 201 
    assert data["username"] == name_valid_user
    assert data["is_active"] == True
    assert "id" in data 


def test_register_existing_user_returns_conflict(client):
    """
    Test de integración: Prueba que el endpoint devuelve un error 409 Conflict
    si se intenta registrar un usuario que ya existe.
    """
    client.post(
        "/auth/register", 
        json=valid_user
    )

    response = client.post(
        "/auth/register", 
        json=invalid_user
    )

    assert response.status_code == 409 
    assert response.json()["message"] == "Username already exists"
    
def test_users_list_clean(client):
    response = client.post(
        "/auth/register", 
        json=valid_user
    )
    assert response.status_code == 201

    response_protected = client.get("/users")
    assert response_protected.status_code == 200
    

def test_login_without_register_first(client):
    # no hay register previo
    response = client.post(
        "/auth/login",
        json=invalid_user
    )
    data = response.json()
    
    assert response.status_code == 404
    assert data["message"] == "User not found"
    
def test_login_with_wrong_password(client):
    client.post(
        "/auth/register", 
        json=valid_user
    )

    response = client.post(
        "/auth/login",
        json=invalid_user
    )
    data = response.json()
    
    assert response.status_code == 401
    assert data["message"] == "Invalid password"
    
def test_logout_succesfully(client):
    response = client.post(
        "/auth/register", 
        json=valid_user
    )
    assert response.status_code == 201
    
    response = client.post(
        "/auth/logout",
        json=valid_user
    )
    
    assert response.status_code == 200
    
    response = client.post(
        "/users"
    )
    
    assert response.status_code == 401
    assert "Unauthorized" in response.json()["message"]
    