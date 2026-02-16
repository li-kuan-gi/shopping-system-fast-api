import logging
from src.database import engine, SessionLocal
from src.shopping.models import metadata
from src.shopping.domain import Product

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    logger.info("Creating tables...")
    metadata.create_all(bind=engine)
    logger.info("Tables created successfully.")

    session = SessionLocal()
    try:
        # Check if products exist
        if session.query(Product).count() > 0:
            logger.info("Products already exist. Skipping seeding.")
            return

        logger.info("Seeding products...")
        # Seed initial products (IDs must match Supabase for consistency if possible,
        # but for local dev, any ID works as long as frontend uses the local API)
        products = [
            Product(id=1, stock=100),
            Product(id=2, stock=50),
            Product(id=3, stock=20),
        ]
        session.add_all(products)
        session.commit()
        logger.info("Products seeded successfully.")
    except Exception as e:
        logger.error(f"Error seeding data: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    init_db()
