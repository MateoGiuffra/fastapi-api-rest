Resumen del Flujo de Trabajo
1. Modifica tus modelos en Python.
2. Genera la migración: poetry run alembic revision --autogenerate -m "Mi cambio"
3. Aplica la migración: poetry run alembic upgrade head
4. Ejecuta tu aplicación: poetry run uvicorn src.main:app --reload