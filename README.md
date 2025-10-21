# FastAPI REST API with Clean Architecture

This project is a RESTful API built with Python using the FastAPI framework. It demonstrates a clean architecture approach, separating concerns into services, repositories, and models. It includes JWT-based authentication using secure HTTPOnly cookies, database management with SQLAlchemy and Alembic, and a comprehensive test suite with Pytest.

## ✨ Features

- **FastAPI**: High-performance, easy-to-use web framework for building APIs.
- **Clean Architecture**: Organized structure with distinct layers (handlers, services, repositories) for better maintainability and scalability.
- **SQLAlchemy ORM**: Powerful and pythonic SQL toolkit and Object Relational Mapper.
- **Alembic Migrations**: Handles database schema migrations smoothly.
- **JWT Authentication**: Secure, stateless authentication using JSON Web Tokens stored in HTTPOnly cookies.
- **Pydantic**: Data validation and settings management.
- **Dependency Injection**: FastAPI's built-in DI system to manage dependencies like database sessions and services.
- **Async Support**: Asynchronous views and logic for high concurrency.
- **Docker Ready**: Includes a `Dockerfile` for easy containerization and deployment.
- **Testing**: Unit and integration tests using `pytest` and `TestClient`.

## 📂 Project Structure

```
.
├── alembic/              # Alembic migration scripts
├── src/                  # Main source code
│   ├── core/             # Core logic (config, middleware)
│   ├── database/         # Database models and base configuration
│   ├── dependencies/     # FastAPI dependency injection setup
│   ├── handlers/         # Custom exception handlers
│   ├── repositories/     # Data access layer (interacts with the DB)
│   ├── routers/          # API endpoint definitions
│   ├── schemas/          # Pydantic data models (DTOs)
│   ├── services/         # Business logic layer
│   └── main.py           # FastAPI application entrypoint
├── tests/                # Application tests
├── .env.example          # Example environment variables
├── alembic.ini           # Alembic configuration
├── Dockerfile            # Container definition for deployment
├── pyproject.toml        # Project metadata and dependencies (Poetry)
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Poetry for dependency management.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/api-rest.git
    cd api-rest
    ```

2.  **Create and configure the environment file:**

    Copy the example `.env` file and fill in your own secret key. You can generate a strong secret key with `openssl rand -hex 32`.

    ```bash
    cp .env.example .env
    ```

    Your `.env` file should look like this:
    ```
    SECRET_KEY="your_super_secret_key_here"
    ALGORITHM="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    COOKIE_SECURE=False # Set to True in production with HTTPS
    ```

3.  **Install dependencies:**
    ```bash
    poetry install
    ```

4.  **Run database migrations:**

    This will create the `app.db` file (if it doesn't exist) and set up the necessary tables.
    ```bash
    poetry run alembic upgrade head
    ```

5.  **Run the development server:**
    ```bash
    poetry run poe dev
    ```
    The API will be available at `http://127.0.0.1:8000`. Interactive documentation can be found at `http://127.0.0.1:8000/docs`.

## 🧪 Running Tests

To run the test suite, execute the following command:

```bash
poetry run pytest
```

## 🐳 Deployment

This project is configured for deployment using Docker. See the `Dockerfile` for the build steps. For platforms like Render, you can deploy this as a "Web Service" and point it to your Git repository. Render will automatically build and deploy the image.