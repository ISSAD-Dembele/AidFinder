from app.database.database import Base, engine
import app.models

print("Creation des tables...")
Base.metadata.create_all(bind=engine)
print("Tables de la base de données créées avec succès.")