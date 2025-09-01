import os
import json
import pandas as pd
import matplotlib.pyplot as plt


def _ensure_dirs():
    os.makedirs("data/eda", exist_ok=True)
    os.makedirs("artifacts/eda", exist_ok=True)


def _read_any(path: str) -> pd.DataFrame:
    if path.endswith(".jsonl"):
        rows = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                rows.append(json.loads(line))
        return pd.DataFrame(rows)
    return pd.read_csv(path)


def _norm_price(row):
    lo = row.get("price_min")
    hi = row.get("price_max")
    if pd.isna(lo) and pd.isna(hi) and isinstance(row.get("price_text"), str):
        # very rough parse for ranges like "$10 - $15" or "₹ 3,50,000 / Piece"
        import re
        nums = re.findall(r"[0-9]+(?:[.,][0-9]+)*", row["price_text"])
        nums = [x.replace(",", "") for x in nums]
        if nums:
            nums = list(map(float, nums))
            lo = min(nums)
            hi = max(nums)
    return pd.Series({"price_lo": lo, "price_hi": hi})


def run(inp: str):
    _ensure_dirs()
    df = _read_any(inp)

    if df.empty:
        print("No data found.")
        return

    price = df.apply(_norm_price, axis=1)
    df["price_lo"] = price["price_lo"]
    df["price_hi"] = price["price_hi"]

    # summaries
    pd.Series(
        {
            "n_rows": len(df),
            "sites": df["site"].value_counts(dropna=False).to_dict()
            if "site" in df
            else {},
            "categories": df["category"].value_counts(dropna=False)
            .head(20)
            .to_dict()
            if "category" in df
            else {},
        }
    ).to_csv("data/eda/summary.csv")

    if "supplier_name" in df:
        df["supplier_name"].dropna().value_counts().head(20).to_csv(
            "data/eda/top_suppliers.csv"
        )

    if "supplier_location" in df:
        top = df["supplier_location"].dropna().value_counts().head(20)
        top.to_csv("data/eda/top_regions.csv")
        if len(top):
            plt.figure()
            top.plot(kind="bar")
            plt.title("Top Supplier Locations")
            plt.tight_layout()
            plt.savefig("artifacts/eda/top_regions.png")
            plt.close()

    if "price_lo" in df:
        vals = pd.to_numeric(df["price_lo"], errors="coerce").dropna()
        if len(vals):
            plt.figure()
            plt.hist(vals, bins=30)
            plt.title("Price (lower bound) distribution")
            plt.xlabel("Price")
            plt.ylabel("Frequency")
            plt.tight_layout()
            plt.savefig("artifacts/eda/price_lo_hist.png")
            plt.close()

    if "category" in df:
        cats = df["category"].value_counts().head(15)
        if len(cats):
            plt.figure()
            cats.plot(kind="bar")
            plt.title("Top Categories (by items)")
            plt.tight_layout()
            plt.savefig("artifacts/eda/top_categories.png")
            plt.close()

