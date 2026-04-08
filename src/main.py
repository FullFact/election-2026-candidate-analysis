import pandas as pd
import json

electid = []
df = pd.read_csv("src/raw_data/dc-candidates-scotland-2026-04-02T16-17-27.csv")
print(df.head())
# for i in range (len(df)):
#   if df(i,2) != electid:
#       electid += df(i,2)
def getlistofcandidates(df):

    allcandidates = []
    for index, row in df.iterrows():
        dictionary = {
            "person_name": row["person_name"],
            "person_id": row["person_id"],
            "party_name": row["party_name"],
        }
        allcandidates.append(dictionary)
    return allcandidates
    print(dictionary)
print(df["election_id"].unique())
def getfullelectionjson(df):
    electionids = df["election_id"].unique()
    dictionary = {}
    for i in electionids:
        filtereddf = df[df["election_id"]==i]
        candidatelist = getlistofcandidates(filtereddf)
        dictionary[i]=candidatelist
    return dictionary
print(getfullelectionjson(df))

print(json.dumps(getfullelectionjson(df),indent = 4))
filename = "src/data_outputs/candidates.json"
with open(filename,"w+")as f:
    json.dump(getfullelectionjson(df),f)