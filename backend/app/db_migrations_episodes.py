"""
Script de migration pour ajouter les tables seasons et episodes
"""

from sqlalchemy import inspect

from app.db import Base, check_db_connection, engine


def get_existing_tables():
    """Récupère la liste des tables existantes dans la DB"""
    inspector = inspect(engine)
    return inspector.get_table_names()


def create_episode_tables():
    """Crée les nouvelles tables seasons et episodes"""
    print("🔍 Vérification de la connexion à la base de données...")
    if not check_db_connection():
        print("❌ Impossible de se connecter à la base de données!")
        return False

    print("✅ Connexion établie")

    existing_tables = get_existing_tables()
    print(f"\n📊 Tables existantes : {len(existing_tables)}")
    for table in existing_tables:
        print(f"  - {table}")

    new_tables = [
        "seasons",
        "episodes",
    ]

    tables_to_create = [t for t in new_tables if t not in existing_tables]

    if not tables_to_create:
        print("\n✅ Toutes les tables existent déjà!")
    else:
        print(f"\n🆕 Nouvelles tables à créer : {len(tables_to_create)}")
        for table in tables_to_create:
            print(f"  - {table}")

        try:
            print("\n🚀 Création des nouvelles tables...")
            Base.metadata.create_all(bind=engine, checkfirst=True)
            print("✅ Tables créées avec succès!")

            new_existing_tables = get_existing_tables()
            created = set(new_existing_tables) - set(existing_tables)
            if created:
                print("\n✨ Tables créées :")
                for table in created:
                    print(f"  - {table}")

        except Exception as e:
            print(f"❌ Erreur lors de la création des tables : {e}")
            return False

    return True


def show_table_info():
    """Affiche les informations détaillées sur les nouvelles tables"""
    inspector = inspect(engine)

    print("\n" + "=" * 60)
    print("📋 INFORMATIONS DES NOUVELLES TABLES")
    print("=" * 60)

    for table_name in ["seasons", "episodes"]:
        if table_name not in inspector.get_table_names():
            continue

        columns = inspector.get_columns(table_name)
        indexes = inspector.get_indexes(table_name)

        print(f"\n📌 Table: {table_name}")
        print(f"   Colonnes: {len(columns)}")
        for col in columns:
            col_type = str(col["type"])
            nullable = "NULL" if col["nullable"] else "NOT NULL"
            print(f"      - {col['name']}: {col_type} {nullable}")

        if indexes:
            print(f"   Index: {len(indexes)}")
            for idx in indexes:
                unique = "UNIQUE" if idx["unique"] else ""
                print(f"      - {idx['name']} {unique}")


if __name__ == "__main__":
    print("=" * 60)
    print("🔧 MIGRATION BASE DE DONNÉES - SEASONS & EPISODES")
    print("=" * 60)

    # Créer les tables
    success = create_episode_tables()

    if success:
        # Afficher les infos
        show_table_info()
        print("\n" + "=" * 60)
        print("✅ Migration terminée avec succès!")
        print("=" * 60)
        print("\n💡 Prochaines étapes:")
        print("   1. Redémarrer le backend: uvicorn app.main:app --reload")
        print("   2. Lancer sync_sonarr pour peupler les saisons")
        print("   3. Lancer sync_sonarr_episodes pour peupler les épisodes")
        print("   4. Tester les endpoints:")
        print("      - GET /library/{id}/seasons")
        print("      - GET /library/{id}/seasons/{season_number}/episodes")
    else:
        print("\n" + "=" * 60)
        print("❌ Migration échouée")
        print("=" * 60)
