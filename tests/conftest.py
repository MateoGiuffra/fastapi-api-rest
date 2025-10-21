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
