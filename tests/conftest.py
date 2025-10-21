import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importa el modelo User para que SQLAlchemy lo reconozca y pueda crear la tabla
from src.database.models.user import User

from src.main import app
from src.database.base import Base
from src.dependencies.repositories_di import get_db_session

# --- Configuración de la Base de Datos de Prueba ---
# Usaremos SQLite en memoria para los tests. Es rápido y se aísla de tu DB de desarrollo.
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} # Requerido para SQLite
)

# Creamos una sesión de base de datos de prueba
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Fixture para la Base de Datos ---
@pytest.fixture()
def db_session():
    # Crea todas las tablas en la base de datos en memoria
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Elimina todas las tablas después de que el test termine
        Base.metadata.drop_all(bind=engine)

# --- Fixture para el Cliente de API ---
@pytest.fixture()
def client(db_session):
    # Sobrescribimos la dependencia `get_db_session` para que use la sesión de prueba
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db_session] = override_get_db
    
    yield TestClient(app)

    # Limpiamos la sobrescritura después del test
    app.dependency_overrides.clear()
