import kagglehub
import pandas as pd
# Download latest version
#path = kagglehub.dataset_download("yasserh/walmart-dataset")
#print("Path to dataset files:", path)
#Path to dataset files: /Users/bogdan/.cache/kagglehub/datasets/yasserh/walmart-dataset/versions/1

path = "/Users/bogdan/Desktop/an3.sem2/PacheteSoftware/proiect"
df = pd.read_csv("Walmart.csv")
print(df.head())

print(df.info())
print(df.describe())