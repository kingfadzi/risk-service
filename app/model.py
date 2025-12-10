import yaml
import re
import pandas as pd
import scorecardpy as sc
from typing import Dict, Any, Optional, List, Tuple
import threading


class ScorecardModel:
    """
    Loads a YAML config and converts it to a scorecardpy-compatible
    scorecard DataFrame, then uses sc.scorecard_ply() for scoring.
    """

    def __init__(self, config_path: str = "config/scorecard.yaml"):
        self.config_path = config_path
        self._lock = threading.Lock()
        self.load_config()

    def load_config(self) -> None:
        """Load YAML and build scorecardpy-compatible scorecard DataFrame."""
        with self._lock:
            with open(self.config_path, "r") as f:
                self.cfg = yaml.safe_load(f)

            self.version = self.cfg.get("version", 1)
            self.score_name = self.cfg.get("score_name", "RiskScore")
            self.scaling = self.cfg.get("scaling", {})
            self.bands = self.cfg.get("bands", [])

            # Base points added to all scores
            self.base_points = self.scaling.get("points0", 600)

            # Build scorecardpy scorecard as dict of DataFrames per variable
            # This is the format expected by sc.scorecard_ply()
            self.scorecard = {}
            self.numeric_bins = {}  # Store parsed numeric bins for pre-binning

            for variable, bins in self.cfg.get("scorecard", {}).items():
                rows = []
                is_numeric = False

                for bin_def in bins:
                    bin_str = bin_def["bin"]
                    rows.append({
                        "variable": variable,
                        "bin": bin_str,
                        "points": bin_def["points"]
                    })
                    # Detect numeric bins by interval notation
                    if "[" in bin_str or "inf" in bin_str:
                        is_numeric = True

                self.scorecard[variable] = pd.DataFrame(rows)

                # Parse numeric bins for pre-binning
                if is_numeric:
                    self.numeric_bins[variable] = self._parse_numeric_bins(bins)

            # Also keep a combined DataFrame for inspection
            all_rows = []
            for variable, df in self.scorecard.items():
                all_rows.extend(df.to_dict("records"))
            self.scorecard_df = pd.DataFrame(all_rows)

    def _parse_numeric_bins(
        self, bins: List[Dict]
    ) -> List[Tuple[float, float, str, int]]:
        """
        Parse numeric bin definitions into (low, high, bin_str, points) tuples.
        Handles interval notation like [-inf,2), [2,4), [10,inf)
        """
        parsed = []
        for bin_def in bins:
            bin_str = bin_def["bin"]
            points = bin_def["points"]

            # Parse interval notation: [low,high) or (low,high]
            match = re.match(r"[\[\(]([^,]+),([^\]\)]+)[\]\)]", bin_str)
            if match:
                low_str, high_str = match.groups()
                low = float("-inf") if "inf" in low_str else float(low_str)
                high = float("inf") if "inf" in high_str else float(high_str)
                parsed.append((low, high, bin_str, points))

        return parsed

    def _bin_numeric_value(
        self, variable: str, value: float
    ) -> Tuple[str, int]:
        """Convert a numeric value to its bin string and points."""
        if variable not in self.numeric_bins:
            raise ValueError(f"No numeric bins defined for {variable}")

        for low, high, bin_str, points in self.numeric_bins[variable]:
            # Use half-open interval [low, high)
            if low <= value < high:
                return bin_str, points
            # Handle the final bin which might include the upper bound
            if high == float("inf") and value >= low:
                return bin_str, points

        raise ValueError(
            f"Value {value} for {variable} doesn't match any bin"
        )

    def score(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a single change record using scorecardpy.

        Uses sc.scorecard_ply() which is the standard scorecardpy
        function for applying a scorecard to new data.

        Numeric features are pre-binned to match interval notation
        before passing to scorecardpy.
        """
        # Pre-bin numeric features
        binned_data = data.copy()
        numeric_points = {}

        for variable in self.numeric_bins:
            if variable in binned_data:
                value = binned_data[variable]
                bin_str, points = self._bin_numeric_value(variable, value)
                binned_data[variable] = bin_str
                numeric_points[variable] = points

        # Convert input to DataFrame (scorecardpy expects DataFrame)
        input_df = pd.DataFrame([binned_data])

        # Apply scorecard using scorecardpy's scoring function
        # scorecard_ply returns DataFrame with score for each variable + total
        scored_df = sc.scorecard_ply(
            dt=input_df,
            card=self.scorecard,
            only_total_score=False,  # Get per-feature breakdown
            print_step=0  # Suppress progress output
        )

        # Extract total score
        # scorecardpy names the total column 'score'
        total_score = float(scored_df["score"].iloc[0])

        # Add base points to get final score
        final_score = self.base_points + total_score

        # Extract per-feature scores for explainability
        # scorecardpy adds '_points' suffix to each variable
        feature_scores = {}
        for col in scored_df.columns:
            if col.endswith("_points"):
                feature_name = col.replace("_points", "")
                score_val = scored_df[col].iloc[0]
                # Use pre-computed points for numeric features if NaN
                if pd.isna(score_val) and feature_name in numeric_points:
                    feature_scores[feature_name] = float(numeric_points[feature_name])
                else:
                    feature_scores[feature_name] = float(score_val)

        # Recalculate total if we had to fix NaN values
        if numeric_points:
            recalc_total = sum(feature_scores.values())
            total_score = recalc_total
            final_score = self.base_points + total_score

        # Determine risk band
        band = self._get_band(final_score)

        return {
            "version": self.version,
            "score": round(final_score, 2),
            "band": band,
            "feature_scores": feature_scores,
            "raw_points": round(total_score, 2)
        }

    def _get_band(self, score: float) -> str:
        """Map score to risk band."""
        for band_def in self.bands:
            if score <= band_def["max_score"]:
                return band_def["name"]
        return "CRITICAL"

    def reload(self) -> None:
        """Hot-reload configuration."""
        self.load_config()

    def get_features(self) -> list[str]:
        """Get list of feature names in the scorecard."""
        return list(self.scorecard.keys())


# Thread-safe singleton
_model_instance: Optional[ScorecardModel] = None
_model_lock = threading.Lock()


def get_model() -> ScorecardModel:
    """Get or create the singleton scorecard model."""
    global _model_instance
    if _model_instance is None:
        with _model_lock:
            if _model_instance is None:
                _model_instance = ScorecardModel()
    return _model_instance


def reload_model() -> None:
    """Trigger hot-reload of the model configuration."""
    model = get_model()
    model.reload()
