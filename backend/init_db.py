from app.db import Base, check_db_connection, engine
from app.models import models  # noqa: F401 - import needed to register models with Base


def init_database():
    """Create all tables"""
    if not check_db_connection():
        print("❌ Can't connect to database")
        return

    print("📦 Writing tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Succes!")


if __name__ == "__main__":
    init_database()
