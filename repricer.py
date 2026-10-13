"""
PricePulse AI — Core Repricing & Market Intelligence Logic.
Calculates optimal Buy-Box prices based on competitor movements, margin floors, and stock status.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


@dataclass
class RepricingRule:
    min_margin_percent: float = 15.0      # Safety floor: never sell below cost + 15%
    undercut_cents: float = 0.50          # Beat competitor by $0.50
    stockout_surge_percent: float = 7.0   # If competitor is out of stock, raise price +7% to harvest margin
    match_strategy: str = "aggressive"    # "aggressive" (undercut), "equal" (match), "premium" (+2%)


class RepricingEngine:
    """Enterprise dynamic pricing algorithm mimicking Amazon & Shopify repricers."""

    def __init__(self, rule: Optional[RepricingRule] = None):
        self.rule = rule or RepricingRule()

    def evaluate_product(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates recommended price, delta, action, and reasoning for a product."""
        cost = float(row.get("cost_price", 0.0))
        our_price = float(row.get("current_price", 0.0))
        comp1_price = float(row.get("competitor_a_price", 0.0))
        comp2_price = float(row.get("competitor_b_price", 0.0))
        comp1_stock = bool(row.get("comp_a_in_stock", True))
        comp2_stock = bool(row.get("comp_b_in_stock", True))

        # Absolute floor: Cost + Min Margin
        floor_price = round(cost * (1 + self.rule.min_margin_percent / 100.0), 2)

        # Determine effective competitor market price among in-stock competitors
        active_comp_prices = []
        if comp1_stock and comp1_price > 0:
            active_comp_prices.append(comp1_price)
        if comp2_stock and comp2_price > 0:
            active_comp_prices.append(comp2_price)

        # Scenario 1: All competitors are OUT OF STOCK (Harvest High Margin)
        if not active_comp_prices:
            surge_multiplier = 1 + (self.rule.stockout_surge_percent / 100.0)
            rec_price = round(max(our_price, comp1_price, comp2_price) * surge_multiplier, 2)
            action = "🔺 Surge Price (+Stock Monopoly)"
            reason = f"Competitors stockout detected. Price raised by +{self.rule.stockout_surge_percent}% to maximize gross profit."
            status_badge = "SURGE"

        else:
            lowest_comp = min(active_comp_prices)

            # Scenario 2: Aggressive Buy-Box undercutting
            target_price = round(lowest_comp - self.rule.undercut_cents, 2)

            if target_price < floor_price:
                # Competitor is dumping below our safety margin! Protect margin.
                rec_price = floor_price
                action = "🛡️ Hold Margin Floor"
                reason = f"Competitor dumped to ${lowest_comp:.2f}. Price locked at safety floor (${floor_price:.2f}, {self.rule.min_margin_percent}% margin)."
                status_badge = "PROTECTED"
            elif target_price < our_price:
                # We need to undercut to win back sales volume
                rec_price = target_price
                diff = our_price - rec_price
                action = f"📉 Drop -${diff:.2f} (Win Buy-Box)"
                reason = f"Competitor leads at ${lowest_comp:.2f}. Undercutting by ${self.rule.undercut_cents:.2f} to recapture #1 market position."
                status_badge = "UNDERCUT"
            elif target_price > our_price:
                # We are priced unnecessarily low! We can raise our price and keep winning
                rec_price = target_price
                gain = rec_price - our_price
                action = f"📈 Raise +${gain:.2f} (Harvest Margin)"
                reason = f"Lowest competitor is at ${lowest_comp:.2f}. We can safely increase price by +${gain:.2f} without losing Buy-Box."
                status_badge = "OPTIMIZED"
            else:
                rec_price = our_price
                action = "✓ Optimal Price"
                reason = "Current price already maintains optimal Buy-Box advantage."
                status_badge = "OPTIMAL"

        margin_dollar = round(rec_price - cost, 2)
        margin_pct = round((margin_dollar / rec_price) * 100, 1) if rec_price > 0 else 0.0
        price_diff = round(rec_price - our_price, 2)

        return {
            "recommended_price": rec_price,
            "floor_price": floor_price,
            "price_diff": price_diff,
            "action": action,
            "status_badge": status_badge,
            "reason": reason,
            "new_margin_pct": margin_pct,
            "new_margin_dollar": margin_dollar
        }

    def process_catalog(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies dynamic repricing across an entire product catalog."""
        results = []
        for _, row in df.iterrows():
            eval_res = self.evaluate_product(row.to_dict())
            results.append(eval_res)

        res_df = pd.DataFrame(results)
        return pd.concat([df.reset_index(drop=True), res_df], axis=1)
