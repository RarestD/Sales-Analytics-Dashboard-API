import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from fastapi.responses import FileResponse
from fastapi import FastAPI
import numpy as np


data_mentah = {
  "produk": ["Kaos", "Celana", "Topi", "Jaket", "Sepatu", "Tas"],
  "kategori": ["Atasan", "Bawahan", "Aksesoris", "Atasan", "Aksesoris", "Aksesoris"],
  "harga": [80000, 150000, None, 250000, 300000, None],
  "terjual": [120, 45, 200, 30, 15, 60]
}

df = pd.DataFrame(data_mentah)

app = FastAPI()

def fill_harga(data):
  summary = data.copy()
  summary["harga"] = summary["harga"].fillna(data.groupby("kategori")["harga"].transform("mean")) # jika ada minimal 1 kategori yang ada harganya maka gunakna refrensi rata rata harga tersebut
  summary["harga"] = summary["harga"].fillna(summary["harga"].mean()) # jika kategori tersebut tidak ada harganya sama sekali maka gunakan rata2 semua kategori
  summary["pendapatan"] = summary["harga"] * summary["terjual"]
  return summary


def sales_summary(data):
  summary = fill_harga(data)
  produk_pendapatan_tertinggi = summary[summary["pendapatan"] == summary["pendapatan"].max()][["produk", "pendapatan"]].round(2)
  mean = np.mean(summary["pendapatan"])
  std = np.std(summary["pendapatan"])
  summary_json = {
    "total_pendapatan_per_kategori":summary.groupby("kategori")["pendapatan"].sum().reset_index().to_dict(orient="records"),
    "produk_pendapatan_tertinggi":produk_pendapatan_tertinggi.to_dict(orient="records"),
    "statistik": {
            "mean": round(float(mean), 2),
            "std": round(float(std), 2)
        }
  }
  return summary_json

@app.get("/sales-summary")
def get_sales_summary():
  return sales_summary(df)

@app.get("/sales-chart")
def get_sales_chart():
  data = df.copy()
  summary = fill_harga(data)
  summary_chart = summary.groupby("kategori")["pendapatan"].sum().reset_index()
  sns.barplot(data=summary_chart, x="kategori", y="pendapatan")
  plt.title("pendapatan per kategori")
  nama_file = "sales-chart.png"
  plt.savefig(nama_file, format="png")
  plt.close()
  return FileResponse(path=nama_file, filename="sales-chart", media_type="image/png")

@app.post("/sales-summary")
def post_sales_summary(payload:dict):
  data = pd.DataFrame(payload)
  return sales_summary(data)


