import os

from dotenv import load_dotenv
from google.cloud import bigquery, storage

load_dotenv()
PROJECT = os.environ["GCP_PROJECT"]
BUCKET = os.environ["GCS_BUCKET"]

# 1 — can I see my bucket?
gcs = storage.Client(project=PROJECT)
blobs = list(gcs.list_blobs(BUCKET, prefix="erp/"))
print(f"found {len(blobs)} object(s) under erp/")
for b in blobs:
    print(f"   {b.name} | {b.size} bytes | updated {b.updated}")

# 2 — can I query BigQuery?
bq = bigquery.Client(project=PROJECT)
job = bq.query("SELECT COUNT(*) AS n FROM `bigquery-public-data.thelook_ecommerce.orders`")
n = list(job.result())[0].n
print(f"bigquery sees {n:,} orders")
print(f"billed {job.total_bytes_billed / 1e6:.0f} MB")