import sqlite3
import random
import os
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

DEFAULT_DB_PATH = Path("data/sales.db")
RANDOM_SEED = 42


def main() -> None:
    db_path = Path(os.environ.get("SALES_DB_PATH", DEFAULT_DB_PATH))

    random.seed(RANDOM_SEED)
    Faker.seed(RANDOM_SEED)
    fake = Faker("es_CO")

    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS ventas")
        cursor.execute(
            """
            CREATE TABLE ventas (
                id INTEGER PRIMARY KEY,
                vendedor TEXT NOT NULL,
                sede TEXT NOT NULL,
                producto TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                precio REAL NOT NULL,
                fecha TEXT NOT NULL
            )
            """
        )

        sellers = [fake.name() for _ in range(50)]
        branches = [fake.city() for _ in range(8)]
        products = [
            "Laptop",
            "Smartphone",
            "Tablet",
            "Headphones",
            "Camera",
            "Monitor",
            "Keyboard",
            "Mouse",
            "Printer",
            "External Drive",
        ]
        prices_by_product = {
            "Laptop": 3_500_000,
            "Smartphone": 2_200_000,
            "Tablet": 1_400_000,
            "Headphones": 280_000,
            "Camera": 2_800_000,
            "Monitor": 850_000,
            "Keyboard": 180_000,
            "Mouse": 90_000,
            "Printer": 650_000,
            "External Drive": 320_000,
        }

        start_date = date(2025, 1, 1)

        rows = []
        for sale_id in range(1, 101):
            product = random.choice(products)
            rows.append(
                (
                    sale_id,
                    random.choice(sellers),
                    random.choice(branches),
                    product,
                    random.randint(1, 10),
                    prices_by_product[product],
                    (start_date + timedelta(days=random.randint(0, 120))).isoformat(),
                )
            )

        cursor.executemany(
            """
            INSERT INTO ventas (
                id, vendedor, sede, producto, cantidad, precio, fecha
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    print(f"Database created at {db_path}")


if __name__ == "__main__":
    main()
