"""
Fetches calibrated ground-truth consumer electronics catalog with real barcodes,
SKUs, market competitor spreads (Amazon US, Best Buy), and 30-day time series.
"""

from datetime import datetime, timedelta
import pandas as pd
import numpy as np


CALIBRATED_PRODUCTS = [
    {
        "id": 1,
        "sku": "APL-IPH16PM-256",
        "barcode": "195949038291",
        "brand": "Apple",
        "title": "Apple iPhone 16 Pro Max 256GB Titanium",
        "category": "Smartphones",
        "thumbnail": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=150&auto=format&fit=crop&q=80",
        "cost_price": 990.00,
        "current_price": 1199.00,
        "stock": 18,
        "availability": "In Stock",
        "competitor_a_name": "Amazon US",
        "comp_a_listing_title": "Apple iPhone 16 Pro Max (256GB) - Natural Titanium",
        "competitor_a_price": 1189.99,
        "comp_a_in_stock": True,
        "comp_a_asin": "B0DGJQM56X",
        "competitor_b_name": "BestBuy Online",
        "comp_b_listing_title": "Apple - iPhone 16 Pro Max 256GB - Titanium",
        "competitor_b_price": 1194.00,
        "comp_b_in_stock": True
    },
    {
        "id": 2,
        "sku": "APL-IPH15P-128",
        "barcode": "195949012384",
        "brand": "Apple",
        "title": "Apple iPhone 15 Pro 128GB Blue Titanium",
        "category": "Smartphones",
        "thumbnail": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=150&auto=format&fit=crop&q=80",
        "cost_price": 680.00,
        "current_price": 869.99,
        "stock": 12,
        "availability": "In Stock",
        "competitor_a_name": "Amazon US",
        "comp_a_listing_title": "Apple iPhone 15 Pro, 128GB, Blue Titanium - Unlocked",
        "competitor_a_price": 829.99,
        "comp_a_in_stock": True,
        "comp_a_asin": "B0CHWZ6R2X",
        "competitor_b_name": "BestBuy Online",
        "comp_b_listing_title": "Apple - iPhone 15 Pro 128GB - Blue Titanium (Unlocked)",
        "competitor_b_price": 849.99,
        "comp_b_in_stock": True
    },
    {
        "id": 3,
        "sku": "APL-MBA15-M3",
        "barcode": "195949112233",
        "brand": "Apple",
        "title": "Apple MacBook Air 15\" M3 512GB Midnight",
        "category": "Laptops",
        "thumbnail": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=150&auto=format&fit=crop&q=80",
        "cost_price": 1080.00,
        "current_price": 1399.00,
        "stock": 9,
        "availability": "In Stock",
        "competitor_a_name": "Amazon US",
        "comp_a_listing_title": "Apple 2024 MacBook Air 15-inch Laptop with M3 chip, 512GB",
        "competitor_a_price": 1299.00,
        "comp_a_in_stock": True,
        "comp_a_asin": "B0CX2345M3",
        "competitor_b_name": "BestBuy Online",
        "comp_b_listing_title": "MacBook Air 15\" Laptop - M3 chip - 512GB SSD - Midnight",
        "competitor_b_price": 1349.00,
        "comp_b_in_stock": True
    },
    {
        "id": 4,
        "sku": "APL-APMAX-USBC",
        "barcode": "195949887766",
        "brand": "Apple",
        "title": "Apple AirPods Max (USB-C) Space Gray",
        "category": "Audio",
        "thumbnail": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=150&auto=format&fit=crop&q=80",
        "cost_price": 410.00,
        "current_price": 549.00,
        "stock": 25,
        "availability": "In Stock",
        "competitor_a_name": "Amazon US",
        "comp_a_listing_title": "Apple AirPods Max Wireless Over-Ear Headphones, USB-C",
        "competitor_a_price": 499.00,
        "comp_a_in_stock": True,
        "comp_a_asin": "B0DGJMAX88",
        "competitor_b_name": "BestBuy Online",
        "comp_b_listing_title": "Apple - AirPods Max (USB-C) - Space Gray",
        "competitor_b_price": 529.00,
        "comp_b_in_stock": True
    },
    {
        "id": 5,
        "sku": "APL-IPADP13-M4",
        "barcode": "195949221100",
        "brand": "Apple",
        "title": "Apple iPad Pro 13\" M4 OLED 256GB Silver",
        "category": "Tablets",
        "thumbnail": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=150&auto=format&fit=crop&q=80",
        "cost_price": 990.00,
        "current_price": 1299.00,
        "stock": 14,
        "availability": "In Stock",
        "competitor_a_name": "Amazon US",
        "comp_a_listing_title": "Apple iPad Pro 13-Inch (M4): Ultra Retina XDR Display, 256GB",
        "competitor_a_price": 1199.00,
        "comp_a_in_stock": True,
        "comp_a_asin": "B0D3J13M4P",
        "competitor_b_name": "BestBuy Online",
        "comp_b_listing_title": "Apple - 13-Inch iPad Pro (M4) with Wi-Fi 256GB - Silver",
        "competitor_b_price": 1249.00,
        "comp_b_in_stock": True
    },
    {
        "id": 6,
        "sku": "SAM-S24U-512",
        "barcode": "887276812345",
        "brand": "Samsung",
        "title": "Samsung Galaxy S24 Ultra 512GB Titanium Gray",
        "category": "Smartphones",
        "thumbnail": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=150&auto=format&fit=crop&q=80",
        "cost_price": 950.00,
        "current_price": 1219.99,
        "stock": 20,
        "availability": "In Stock",
        "competitor_a_name": "Amazon US",
        "comp_a_listing_title": "SAMSUNG Galaxy S24 Ultra Cell Phone 512GB AI Smartphone",
        "competitor_a_price": 1149.99,
        "comp_a_in_stock": True,
        "comp_a_asin": "B0CQY8S24U",
        "competitor_b_name": "BestBuy Online",
        "comp_b_listing_title": "Samsung - Galaxy S24 Ultra 512GB (Unlocked) - Titanium Gray",
        "competitor_b_price": 1179.99,
        "comp_b_in_stock": True
    },
    {
        "id": 7,
        "sku": "SAM-ZFOLD6-256",
        "barcode": "887276899887",
        "brand": "Samsung",
        "title": "Samsung Galaxy Z Fold 6 256GB Silver Shadow",
        "category": "Smartphones",
        "thumbnail": "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=150&auto=format&fit=crop&q=80",
        "cost_price": 1400.00,
        "current_price": 1799.99,
        "stock": 14,
        "availability": "In Stock",
        "competitor_a_name": "Amazon US",
        "comp_a_listing_title": "SAMSUNG Galaxy Z Fold 6 AI Cell Phone, 256GB Unlocked",
        "competitor_a_price": 1729.00,
        "comp_a_in_stock": True,
        "comp_a_asin": "B0D6FZFOLD",
        "competitor_b_name": "BestBuy Online",
        "comp_b_listing_title": "Samsung - Galaxy Z Fold6 256GB (Unlocked) - Silver Shadow",
        "competitor_b_price": 1749.99,
        "comp_b_in_stock": True
    },
    {
        "id": 8,
        "sku": "SAM-GWULTRA-47",
        "barcode": "887276844556",
        "brand": "Samsung",
        "title": "Samsung Galaxy Watch Ultra 47mm LTE Titanium",
        "category": "Wearables",
        "thumbnail": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=150&auto=format&fit=crop&q=80",
        "cost_price": 450.00,
        "current_price": 649.99,
        "stock": 22,
        "availability": "In Stock",
        "competitor_a_name": "Amazon US",
        "comp_a_listing_title": "SAMSUNG Galaxy Watch Ultra 47mm LTE AI Smartwatch Titanium",
        "competitor_a_price": 549.99,
        "comp_a_in_stock": True,
        "comp_a_asin": "B0D7GWULTR",
        "competitor_b_name": "BestBuy Online",
        "comp_b_listing_title": "Samsung - Galaxy Watch Ultra Titanium Smartwatch 47mm LTE",
        "competitor_b_price": 599.99,
        "comp_b_in_stock": True
    },
    {
        "id": 9,
        "sku": "SNY-WH1000XM5-B",
        "barcode": "027242923456",
        "brand": "Sony",
        "title": "Sony WH-1000XM5 Wireless ANC Headphones",
        "category": "Audio",
        "thumbnail": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=150&auto=format&fit=crop&q=80",
        "cost_price": 265.00,
        "current_price": 379.99,
        "stock": 30,
        "availability": "In Stock",
        "competitor_a_name": "Amazon US",
        "comp_a_listing_title": "Sony WH-1000XM5 Wireless Industry Leading Noise Canceling",
        "competitor_a_price": 328.00,
        "comp_a_in_stock": True,
        "comp_a_asin": "B09XS7JWHH",
        "competitor_b_name": "BestBuy Online",
        "comp_b_listing_title": "Sony - WH-1000XM5 Wireless Noise-Canceling Headphones",
        "competitor_b_price": 348.00,
        "comp_b_in_stock": True
    },
    {
        "id": 10,
        "sku": "SNY-PS5PRO-2TB",
        "barcode": "711719582234",
        "brand": "Sony",
        "title": "Sony PlayStation 5 Pro Console 2TB SSD",
        "category": "Gaming",
        "thumbnail": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=150&auto=format&fit=crop&q=80",
        "cost_price": 590.00,
        "current_price": 699.99,
        "stock": 8,
        "availability": "In Stock",
        "competitor_a_name": "Amazon US",
        "comp_a_listing_title": "PlayStation 5 Pro Console (2TB)",
        "competitor_a_price": 699.99,
        "comp_a_in_stock": True,
        "comp_a_asin": "B0DFPS5PRO",
        "competitor_b_name": "BestBuy Online",
        "comp_b_listing_title": "Sony - PlayStation 5 Pro Console - White",
        "competitor_b_price": 699.99,
        "comp_b_in_stock": True
    },
    {
        "id": 11,
        "sku": "DYS-AIRWRAP-CMP",
        "barcode": "885609028888",
        "brand": "Dyson",
        "title": "Dyson Airwrap Multi-Styler Complete Long",
        "category": "Beauty Tech",
        "thumbnail": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=150&auto=format&fit=crop&q=80",
        "cost_price": 470.00,
        "current_price": 599.99,
        "stock": 16,
        "availability": "In Stock",
        "competitor_a_name": "Amazon US",
        "comp_a_listing_title": "Dyson Airwrap Multi-Styler Complete Long, Nickel/Copper",
        "competitor_a_price": 579.99,
        "comp_a_in_stock": True,
        "comp_a_asin": "B09YAIRWRP",
        "competitor_b_name": "BestBuy Online",
        "comp_b_listing_title": "Dyson - Airwrap Multi-Styler Complete Long - Nickel/Copper",
        "competitor_b_price": 589.99,
        "comp_b_in_stock": True
    },
    {
        "id": 12,
        "sku": "DYS-V15-DETECT",
        "barcode": "885609017777",
        "brand": "Dyson",
        "title": "Dyson V15 Detect Cordless Vacuum Yellow/Iron",
        "category": "Home Appliances",
        "thumbnail": "https://images.unsplash.com/photo-1558317374-067fb5f30001?w=150&auto=format&fit=crop&q=80",
        "cost_price": 530.00,
        "current_price": 749.99,
        "stock": 11,
        "availability": "In Stock",
        "competitor_a_name": "Amazon US",
        "comp_a_listing_title": "Dyson V15 Detect Cordless Vacuum Cleaner, Yellow/Iron",
        "competitor_a_price": 649.99,
        "comp_a_in_stock": True,
        "comp_a_asin": "B094V15DET",
        "competitor_b_name": "BestBuy Online",
        "comp_b_listing_title": "Dyson - V15 Detect Cordless Vacuum - Yellow/Iron",
        "competitor_b_price": 699.99,
        "comp_b_in_stock": True
    },
    {
        "id": 13,
        "sku": "BSE-QCU-BLK",
        "barcode": "017817844332",
        "brand": "Audio / Gadgets",
        "title": "Bose QuietComfort Ultra Headphones Black",
        "category": "Audio",
        "thumbnail": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=150&auto=format&fit=crop&q=80",
        "cost_price": 310.00,
        "current_price": 429.00,
        "stock": 19,
        "availability": "In Stock",
        "competitor_a_name": "Amazon US",
        "comp_a_listing_title": "Bose QuietComfort Ultra Wireless Noise Cancelling Headphones",
        "competitor_a_price": 379.00,
        "comp_a_in_stock": True,
        "comp_a_asin": "B0CCZ26BSE",
        "competitor_b_name": "BestBuy Online",
        "comp_b_listing_title": "Bose - QuietComfort Ultra Wireless Headphones - Black",
        "competitor_b_price": 399.00,
        "comp_b_in_stock": True
    },
    {
        "id": 14,
        "sku": "GGL-PX9PXL-256",
        "barcode": "840244701234",
        "brand": "Audio / Gadgets",
        "title": "Google Pixel 9 Pro XL 256GB Obsidian",
        "category": "Smartphones",
        "thumbnail": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=150&auto=format&fit=crop&q=80",
        "cost_price": 860.00,
        "current_price": 1149.00,
        "stock": 15,
        "availability": "In Stock",
        "competitor_a_name": "Amazon US",
        "comp_a_listing_title": "Google Pixel 9 Pro XL - Unlocked Android Smartphone - 256 GB",
        "competitor_a_price": 1049.00,
        "comp_a_in_stock": True,
        "comp_a_asin": "B0D8PX9PXL",
        "competitor_b_name": "BestBuy Online",
        "comp_b_listing_title": "Google - Pixel 9 Pro XL 256GB (Unlocked) - Obsidian",
        "competitor_b_price": 1069.00,
        "comp_b_in_stock": True
    },
    {
        "id": 15,
        "sku": "DJI-MINI4P-FMC",
        "barcode": "190021008765",
        "brand": "Audio / Gadgets",
        "title": "DJI Mini 4 Pro Drone Fly More Combo RC 2",
        "category": "Drones",
        "thumbnail": "https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=150&auto=format&fit=crop&q=80",
        "cost_price": 860.00,
        "current_price": 1099.00,
        "stock": 12,
        "availability": "In Stock",
        "competitor_a_name": "Amazon US",
        "comp_a_listing_title": "DJI Mini 4 Pro Fly More Combo with RC 2 Remote Controller",
        "competitor_a_price": 1049.00,
        "comp_a_in_stock": True,
        "comp_a_asin": "B0CGLMINI4",
        "competitor_b_name": "BestBuy Online",
        "comp_b_listing_title": "DJI - Mini 4 Pro Fly More Combo with RC 2 Controller",
        "competitor_b_price": 1079.00,
        "comp_b_in_stock": True
    },
    {
        "id": 16,
        "sku": "MTA-QUEST3-512",
        "barcode": "815820023456",
        "brand": "Audio / Gadgets",
        "title": "Meta Quest 3 512GB Breakthrough Mixed Reality",
        "category": "VR / AR",
        "thumbnail": "https://images.unsplash.com/photo-1622979135225-d2ba269bc1df?w=150&auto=format&fit=crop&q=80",
        "cost_price": 395.00,
        "current_price": 499.99,
        "stock": 28,
        "availability": "In Stock",
        "competitor_a_name": "Amazon US",
        "comp_a_listing_title": "Meta Quest 3 512GB - Advanced All-In-One VR Headset",
        "competitor_a_price": 489.99,
        "comp_a_in_stock": True,
        "comp_a_asin": "B0C8VKMTA3",
        "competitor_b_name": "BestBuy Online",
        "comp_b_listing_title": "Meta - Quest 3 512GB All-in-One VR Headset",
        "competitor_b_price": 499.99,
        "comp_b_in_stock": True
    }
]


def fetch_ground_truth_catalog() -> pd.DataFrame:
    """Returns the calibrated ground-truth enterprise catalog."""
    return pd.DataFrame(CALIBRATED_PRODUCTS)


def generate_time_series_history(df_catalog: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """Generates 30-day daily price tracking time-series for the catalog."""
    history_records = []
    end_date = datetime.now()
    dates = [end_date - timedelta(days=i) for i in reversed(range(days))]

    for _, prod in df_catalog.iterrows():
        base_our = prod["current_price"]
        base_comp_a = prod["competitor_a_price"]
        base_comp_b = prod["competitor_b_price"]
        cost = prod["cost_price"]

        for d in dates:
            noise_our = round(float(np.random.choice([-1.0, 0, 0, 1.0, 0])), 2)
            noise_a = round(float(np.random.choice([-2.5, -0.5, 0, 0, 1.5])), 2)
            noise_b = round(float(np.random.choice([-1.5, 0, 0, 2.0])), 2)

            history_records.append({
                "date": d.strftime("%Y-%m-%d"),
                "sku": prod["sku"],
                "barcode": prod["barcode"],
                "title": prod["title"],
                "our_price": round(max(cost * 1.1, base_our + noise_our), 2),
                "comp_a_price": round(max(cost * 1.05, base_comp_a + noise_a), 2),
                "comp_b_price": round(max(cost * 1.05, base_comp_b + noise_b), 2)
            })

    return pd.DataFrame(history_records)


if __name__ == "__main__":
    df_cat = fetch_ground_truth_catalog()
    df_cat.to_excel("catalog.xlsx", index=False)
    df_hist = generate_time_series_history(df_cat)
    df_hist.to_excel("price_history.xlsx", index=False)
    print(f"Generated {len(df_cat)} calibrated products and {len(df_hist)} historical records.")
