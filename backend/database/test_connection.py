from sqlalchemy import text

from backend.database.connection import engine


def test_connection() -> None:
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT current_database(), current_user")
            )
            database_name, user_name = result.one()

        print("Conexión correcta")
        print(f"Base de datos: {database_name}")
        print(f"Usuario: {user_name}")

    except Exception as exc:
        print(f"Error de conexión: {exc}")
        raise


if __name__ == "__main__":
    test_connection()