import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.models.user import User
from src.main import app
from src.database.base import Base
from src.database.session import get_db_session as app_get_db_session

# --- Configuración de la Base de Datos de Prueba ---
SQLALCHEMY_DATABASE_URL = "sqlite+pysqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # Usar la misma conexión en memoria para todos los tests
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    # Creamos las tablas UNA sola vez
    Base.metadata.create_all(bind=engine)
    # No es necesario drop_all en este caso, ya que la memoria se libera al final de la sesión

@pytest.fixture(scope="function")
def client():
    # 1. Crear la conexión y la sesión de prueba
    connection = engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)
    
    # 2. Reemplazar la dependencia de la aplicación
    def override_get_db():
        try:
            yield db
        finally:
            # NO CERRAR db.close() aquí, ya que el rollback debe ocurrir después
            pass
            
    app.dependency_overrides[app_get_db_session] = override_get_db

    # 3. Inicializar el cliente de prueba
    with TestClient(app) as test_client:
        yield test_client # ◀ Aquí se ejecutan los tests

    # 4. LIMPIEZA (AFTEREACH): Esto se ejecuta DESPUÉS de cada test
    
    # Hacer rollback para deshacer todos los cambios de la prueba actual.
    # Esto es el equivalente a 'borrar todo' para una DB en memoria.
    transaction.rollback() 
    connection.close() 

    app.dependency_overrides.clear()
    
# conftest.py

# ... Tu código de 'client' ...

# -------------------------------------------------------------
# 2. FIXTURE DE SERVICIO (USANDO LA SESIÓN DE PRUEBA)
# -------------------------------------------------------------

# Importamos las funciones de inyección necesarias
from src.dependencies.repositories_di import get_user_repository
from src.dependencies.services_di import get_user_service, get_cookie_service 

@pytest.fixture(scope="function")
def user_service_test_instance(client):
    """
    Fixture que provee una instancia de UserService inyectada con la 
    sesión de prueba activa. Las operaciones son reversibles.
    """
    
    # 1. ACCESO A LA SESIÓN DE PRUEBA: 
    # Cuando se sobrescriben dependencias, podemos obtener el objeto 
    # que FastAPI está usando para la sesión de prueba.
    # Accedemos a la función override y la ejecutamos para obtener la sesión:
    override_func = app.dependency_overrides.get(app_get_db_session)
    
    if not override_func:
        raise Exception("La dependencia de DB no fue sobrescrita en el fixture 'client'.")
        
    # El override_get_db devuelve un generador, debemos extraer el objeto
    db_generator = override_func()
    db = next(db_generator) # Obtenemos la sesión activa de la transacción

    # 2. CONSTRUCCIÓN MANUAL DEL SERVICIO:
    
    # A. Repository: Le pasamos la sesión de prueba
    user_repo = get_user_repository(db=db) 

    # B. CookieService: (Asumimos que no requiere dependencias)
    cookie_service = get_cookie_service()
    
    # C. UserService: Le pasamos sus dependencias resueltas
    service = get_user_service(
        user_repository=user_repo, 
        cookie_service=cookie_service
    )
    
    # 3. Yield: Proveemos el servicio al test
    yield service
    
    # 4. Cleanup: El cleanup (rollback/close) ocurre en el fixture 'client', 
    # pero debemos asegurarnos de consumir el generador de DB si es necesario.
    try:
        next(db_generator) 
    except StopIteration:
        pass # El generador está bien si ya se detuvo

# NOTA: Asegúrate de tener 'from src.dependencies.repositories_di import get_user_repository'
# y 'from src.dependencies.services_di import get_user_service, get_cookie_service' en tu conftest.py
