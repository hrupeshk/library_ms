import asyncio
from app.seed_data import seed_database

if __name__ == "__main__":
    print("Starting database seeding...")
    asyncio.run(seed_database())
    print("Database seeding completed!") 