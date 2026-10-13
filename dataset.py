"""
Generates realistic E-Commerce catalog and 30-day time-series price trend datasets.
Categories: Consumer Electronics, Gaming & Smart Home.
"""

from datetime import datetime, timedelta
import pandas as pd
import numpy as np


PRODUCTS = [
    {
        "sku": "SKU-SNY-WH1000XM5",
        "title": "Sony WH-1000XM5 Wireless Noise Cancelling Headphones",
        "category": "Audio & Headphones",
        "cost_price": 280.00,
        "current_price": 389.99,
        "competitor_a_name": "Amazon US",
        "competitor_a_price": 379.99,
        "comp_a_in_stock": True,
        "competitor_b_name": "BestBuy Online",
        "competitor_b_price": 389.00,
        "comp_b_in_stock": True,
        "demand_velocity": "High"
    },
    {
        "sku": "SKU-APL-AIRPODS-MAX",
        "title": "Apple AirPods Max (USB-C) - Space Gray",
        "category": "Audio & Headphones",
        "cost_price": 410.00,
        "current_price": 549.00,
        "competitor_a_name": "Amazon US",
        "competitor_a_price": 529.00,
        "comp_a_in_stock": True,
        "competitor_b_name": "BestBuy Online",
        "competitor_b_price": 549.00,
        "comp_b_in_stock": False,
        "demand_velocity": "High"
    },
    {
        "sku": "SKU-LOGI-MX-MASTER-3S",
        "title": "Logitech MX Master 3S Performance Wireless Mouse",
        "category": "PC Peripherals",
        "cost_price": 65.00,
        "current_price": 99.99,
        "competitor_a_name": "Amazon US",
        "competitor_a_price": 94.50,
        "comp_a_in_stock": True,
        "competitor_b_name": "BestBuy Online",
        "competitor_b_price": 99.99,
        "comp_b_in_stock": True,
        "demand_velocity": "Ultra"
    },
    {
        "sku": "SKU-KBD-KEYCHRON-Q1",
        "title": "Keychron Q1 Pro Wireless Custom Mechanical Keyboard",
        "category": "PC Peripherals",
        "cost_price": 140.00,
        "current_price": 209.00,
        "competitor_a_name": "Amazon US",
        "competitor_a_price": 199.00,
        "comp_a_in_stock": True,
        "competitor_b_name": "BestBuy Online",
        "competitor_b_price": 215.00,
        "comp_b_in_stock": True,
        "demand_velocity": "Medium"
    },
    {
        "sku": "SKU-DELL-U2723QE",
        "title": "Dell UltraSharp 27 4K USB-C Hub Monitor (U2723QE)",
        "category": "Displays & Monitors",
        "cost_price": 420.00,
        "current_price": 579.99,
        "competitor_a_name": "Amazon US",
        "competitor_a_price": 559.99,
        "comp_a_in_stock": True,
        "competitor_b_name": "BestBuy Online",
        "competitor_b_price": 569.00,
        "comp_b_in_stock": True,
        "demand_velocity": "High"
    },
    {
        "sku": "SKU-SAM-OLED-G8",
        "title": "Samsung 34-Inch Odyssey OLED G8 Curved Gaming Monitor",
        "category": "Displays & Monitors",
        "cost_price": 750.00,
        "current_price": 1099.99,
        "competitor_a_name": "Amazon US",
        "competitor_a_price": 1049.99,
        "comp_a_in_stock": False,
        "competitor_b_name": "BestBuy Online",
        "competitor_b_price": 1079.99,
        "comp_b_in_stock": False,
        "demand_velocity": "Medium"
    },
    {
        "sku": "SKU-SONY-PS5-PRO",
        "title": "Sony PlayStation 5 Pro Console 2TB SSD",
        "category": "Gaming Consoles",
        "cost_price": 580.00,
        "current_price": 699.99,
        "competitor_a_name": "Amazon US",
        "competitor_a_price": 699.99,
        "comp_a_in_stock": False,
        "competitor_b_name": "BestBuy Online",
        "competitor_b_price": 699.99,
        "comp_b_in_stock": False,
        "demand_velocity": "Ultra"
    },
    {
        "sku": "SKU-VALVE-STEAMDECK-OLED",
        "title": "Steam Deck OLED 512GB Handheld Gaming PC",
        "category": "Gaming Consoles",
        "cost_price": 440.00,
        "current_price": 569.00,
        "competitor_a_name": "Amazon US",
        "competitor_a_price": 589.00,
        "comp_a_in_stock": True,
        "competitor_b_name": "BestBuy Online",
        "competitor_b_price": 579.00,
        "comp_b_in_stock": True,
        "demand_velocity": "High"
    },
    {
        "sku": "SKU-DJI-MINI-4-PRO",
        "title": "DJI Mini 4 Pro Drone with RC 2 Controller",
        "category": "Drones & Cameras",
        "cost_price": 690.00,
        "current_price": 959.00,
        "competitor_a_name": "Amazon US",
        "competitor_a_price": 929.00,
        "comp_a_in_stock": True,
        "competitor_b_name": "BestBuy Online",
        "competitor_b_price": 949.00,
        "comp_b_in_stock": True,
        "demand_velocity": "High"
    },
    {
        "sku": "SKU-GO-PRO-HERO13",
        "title": "GoPro HERO13 Black Action Camera 5.3K60 Video",
        "category": "Drones & Cameras",
        "cost_price": 280.00,
        "current_price": 399.99,
        "competitor_a_name": "Amazon US",
        "competitor_a_price": 349.99,
        "comp_a_in_stock": True,
        "competitor_b_name": "BestBuy Online",
        "competitor_b_price": 379.00,
        "comp_b_in_stock": True,
        "demand_velocity": "High"
    },
    {
        "sku": "SKU-ANKER-PRIME-250W",
        "title": "Anker Prime 250W Multi-Port GaN Charging Station",
        "category": "Power & Accessories",
        "cost_price": 105.00,
        "current_price": 169.99,
        "competitor_a_name": "Amazon US",
        "competitor_a_price": 149.99,
        "comp_a_in_stock": True,
        "competitor_b_name": "BestBuy Online",
        "competitor_b_price": 159.99,
        "comp_b_in_stock": True,
        "demand_velocity": "Medium"
    },
    {
        "sku": "SKU-BOSE-QC-ULTRA",
        "title": "Bose QuietComfort Ultra Wireless Noise Cancelling Earbuds",
        "category": "Audio & Headphones",
        "cost_price": 195.00,
        "current_price": 299.00,
        "competitor_a_name": "Amazon US",
        "competitor_a_price": 279.00,
        "comp_a_in_stock": True,
        "competitor_b_name": "BestBuy Online",
        "competitor_b_price": 289.00,
        "comp_b_in_stock": True,
        "demand_velocity": "High"
    }
]


def generate_catalog_dataframe() -> pd.DataFrame:
    """Returns the base catalog DataFrame."""
    return pd.DataFrame(PRODUCTS)


def generate_time_series_history(days: int = 30) -> pd.DataFrame:
    """Generates historical daily price records for each product."""
    np.random.seed(42)
    history_records = []
    end_date = datetime.now()
    dates = [end_date - timedelta(days=i) for i in reversed(range(days))]

    for prod in PRODUCTS:
        base_our = prod["current_price"]
        base_comp_a = prod["competitor_a_price"]
        base_comp_b = prod["competitor_b_price"]

        for d in dates:
            # Add subtle realistic daily random walk fluctuations
            noise_our = round(np.random.choice([-1.5, 0, 0, 1.0, 0]), 2)
            noise_a = round(np.random.choice([-3.0, -1.0, 0, 0, 2.0]), 2)
            noise_b = round(np.random.choice([-2.0, 0, 0, 1.5]), 2)

            history_records.append({
                "date": d.strftime("%Y-%m-%d"),
                "sku": prod["sku"],
                "title": prod["title"],
                "our_price": round(max(prod["cost_price"] * 1.1, base_our + noise_our), 2),
                "comp_a_price": round(max(prod["cost_price"] * 1.05, base_comp_a + noise_a), 2),
                "comp_b_price": round(max(prod["cost_price"] * 1.05, base_comp_b + noise_b), 2)
            })

    return pd.DataFrame(history_records)


if __name__ == "__main__":
    df_cat = generate_catalog_dataframe()
    df_cat.to_excel("catalog.xlsx", index=False)
    df_hist = generate_time_series_history()
    df_hist.to_excel("price_history.xlsx", index=False)
    print(f"Generated {len(df_cat)} catalog items and {len(df_hist)} historical time-series points.")
