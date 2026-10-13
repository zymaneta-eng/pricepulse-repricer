"""
PricePulse AI — Enterprise Matching Engine.
Calculates token-based fuzzy similarity, barcode alignment (EAN/UPC), and confidence scores.
"""

import re
from difflib import SequenceMatcher
from typing import Dict, Any, Tuple


class ProductMatchingEngine:
    """Matches catalog items against marketplace listings with confidence scoring."""

    @staticmethod
    def clean_title(title: str) -> str:
        """Normalizes product title by stripping punctuation and standardizing spaces."""
        cleaned = re.sub(r"[^\w\s\d]", " ", title.lower())
        return " ".join(cleaned.split())

    @classmethod
    def token_similarity(cls, title_a: str, title_b: str) -> float:
        """Calculates token-sort ratio between two titles."""
        clean_a = cls.clean_title(title_a)
        clean_b = cls.clean_title(title_b)

        # Standard token similarity
        tokens_a = set(clean_a.split())
        tokens_b = set(clean_b.split())
        if not tokens_a or not tokens_b:
            return 0.0

        intersection = tokens_a.intersection(tokens_b)
        union = tokens_a.union(tokens_b)
        jaccard = len(intersection) / len(union)

        # Sequence matcher ratio
        seq_ratio = SequenceMatcher(None, clean_a, clean_b).ratio()

        # Weighted score (60% token overlap + 40% substring order)
        return round((jaccard * 0.6 + seq_ratio * 0.4) * 100, 1)

    @classmethod
    def match_listing(
        cls,
        our_product: Dict[str, Any],
        competitor_listing: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determines if competitor listing matches our product.
        Verifies Barcode (EAN-13/UPC) or calculates Fuzzy Title Confidence.
        """
        our_ean = str(our_product.get("barcode") or our_product.get("ean") or "").strip()
        comp_ean = str(competitor_listing.get("barcode") or competitor_listing.get("ean") or "").strip()

        # Rule 1: Exact Barcode Match (100% Ground Truth)
        if our_ean and comp_ean and our_ean == comp_ean:
            return {
                "is_match": True,
                "confidence_score": 100.0,
                "match_type": "🔒 Exact Barcode (EAN-13)",
                "confidence_badge": "VERIFIED_100",
                "notes": f"Strict match via global barcode {our_ean}"
            }

        # Rule 2: Fuzzy Title Matching
        sim = cls.token_similarity(
            our_product.get("title", ""),
            competitor_listing.get("title", "")
        )

        if sim >= 85.0:
            return {
                "is_match": True,
                "confidence_score": sim,
                "match_type": "⚡ High Fuzzy Similarity",
                "confidence_badge": "HIGH_CONFIDENCE",
                "notes": f"High lexical overlap ({sim}%)"
            }
        elif sim >= 70.0:
            return {
                "is_match": True,
                "confidence_score": sim,
                "match_type": "⚠️ Review Recommended",
                "confidence_badge": "MEDIUM_CONFIDENCE",
                "notes": f"Probable match ({sim}%), human audit advised"
            }
        else:
            return {
                "is_match": False,
                "confidence_score": sim,
                "match_type": "❌ Low Similarity (<70%)",
                "confidence_badge": "UNMATCHED",
                "notes": "Rejected by anti-mismatch safeguard"
            }
