import urllib.request
import zipfile
import os

print("Downloading MovieLens 100K...")
url = "https://files.grouplens.org/datasets/movielens/ml-100k.zip"
urllib.request.urlretrieve(url, "ml-100k.zip")

print("Extracting...")
with zipfile.ZipFile("ml-100k.zip", "r") as z:
    z.extractall(".")

os.remove("ml-100k.zip")
print("Done! ml-100k folder ready ✅")