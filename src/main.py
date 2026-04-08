import pandas as pd

electid = []
df = pd.read_csv("src/raw_data/dc-candidates-scotland-2026-04-02T16-17-27.csv")
print(df.head())
#for i in range (len(df)):
 #   if df(i,2) != electid:
 #       electid += df(i,2)
allcandidates = []
for index,row in df.iterrows():
    dictionary = {"person_name":row["person_name"],"person_id":row["person_id"],"party_name":row["party_name"]}
    allcandidates.append(dictionary)
print(allcandidates)
print(dictionary)