def test_register_new_user_successfully(client):
    """
    Test de integración: Prueba que el endpoint /users/register
    registra un nuevo usuario correctamente.
    """
    # Hacemos una petición POST al endpoint de registro
    response = client.post(
        "/users/register",
        json={"username": "testuser", "password": "password123"}
    )
    data = response.json()
 
    # Verificamos que la respuesta sea la esperada
    assert response.status_code == 201 # 201 Created
    assert data["username"] == "testuser"
    assert data["is_active"] == True
    assert "id" in data # El usuario ahora tiene un ID de la base de datos


def test_register_existing_user_returns_conflict(client):
    """
    Test de integración: Prueba que el endpoint devuelve un error 409 Conflict
    si se intenta registrar un usuario que ya existe.
    """
    # 1. Creamos un usuario primero
    client.post(
        "/users/register",
        json={"username": "existinguser", "password": "password123"}
    )

    # 2. Intentamos crearlo de nuevo
    response = client.post(
        "/users/register",
        json={"username": "existinguser", "password": "anotherpassword"}
    )

    # Verificamos que la API responde con un error de conflicto
    assert response.status_code == 409 # 409 Conflict
    assert response.json() == {"detail": "Username already exists"}
