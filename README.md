# Sales Analytics Dashboard API

A REST API built with **FastAPI**, **Pandas**, and **Seaborn** that cleans messy sales data, computes revenue insights, and generates a visual chart — simulating a small analytics service for an online store.

## Features

- Automatic missing-value handling for prices, using a two-step fallback strategy: category average first, then global average if a category has no valid data at all
- Revenue calculation and aggregation per category
- Identifies the best-performing product(s), correctly handling ties
- Chart generation (bar chart of revenue per category) returned as a downloadable PNG image
- Supports both a built-in demo dataset (`GET`) and custom data submitted by the client (`POST`)

## Tech Stack

- Python 3
- FastAPI
- Pandas & NumPy
- Matplotlib & Seaborn
- Uvicorn (ASGI server)

## Installation & Running Locally

```bash
pip install fastapi uvicorn pandas numpy matplotlib seaborn
uvicorn SalesAnalyticsDashboardAPI:app --reload
```

Visit `http://127.0.0.1:8000/docs` for interactive Swagger documentation.

## API Reference

### `GET /sales-summary`

Returns a revenue summary computed from the built-in demo dataset.

**Response**

```json
{
  "total_pendapatan_per_kategori": [
    {"kategori": "Aksesoris", "pendapatan": 82500000.0},
    {"kategori": "Atasan", "pendapatan": 17100000.0},
    {"kategori": "Bawahan", "pendapatan": 6750000.0}
  ],
  "produk_pendapatan_tertinggi": [
    {"produk": "Topi", "pendapatan": 60000000.0}
  ],
  "statistik": {"mean": 17725000.0, "std": 19378548.06}
}
```

### `POST /sales-summary`

Same response shape as above, but computed from custom sales data sent in the request body.

**Request body**

```json
{
  "produk": ["Payung", "Sandal", "Dompet"],
  "kategori": ["Aksesoris", "Alas Kaki", "Aksesoris"],
  "harga": [45000, null, 60000],
  "terjual": [10, 20, 5]
}
```

### `GET /sales-chart`

Returns a PNG bar chart image showing total revenue per category, generated with Seaborn/Matplotlib.

## Lessons Learned

This project surfaced two subtle bugs that never raised an error yet quietly produced wrong numbers — both worth documenting since they reflect real data-engineering pitfalls:

1. **`DataFrame.fillna(series)` vs. `Series.fillna(series)`** — calling `.fillna()` on an entire DataFrame with a Series as the fill value aligns that Series' index against the DataFrame's *column names*, not its row positions. If none of the column names match the Series' index, nothing gets filled at all, silently. The fix was to call `.fillna()` on the specific column (a Series) rather than on the whole DataFrame, so the alignment happens row-by-row as intended.
2. **Accidental reliance on a global variable inside a reusable function** — the missing-value-filling function initially computed category averages from a hardcoded global DataFrame instead of from its own input parameter. This happened to work for the `GET` endpoint (same underlying data) but silently produced incorrect results for the `POST` endpoint whenever a client submitted different data. The fix was to consistently reference the function's own parameter instead of the outer variable.

## Possible Improvements

- Request validation with Pydantic models instead of accepting a raw `dict`
- Save generated charts with unique filenames instead of overwriting a single file, to safely support concurrent requests
- Add automated tests covering the missing-value fallback logic, especially the edge case where an entire category has no valid data
