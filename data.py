import requests
import pandas as pd
from sklearn.ensemble import IsolationForest
import os

url = "http://localhost:9090/api/v1/query_range"
params = {
    'query': 'up',
    'start': '2023-10-01T00:00:00Z',
    'end': '2023-10-02T00:00:00Z',
    'step': '60s'
}

response = requests.get(url, params=params)
data = response.json()

if not data.get('data', {}).get('result', []):
    print("No data returned from the query.")
    exit()

try:
    df = pd.DataFrame(data['data']['result'][0]['values'], columns=['timestamp', 'value'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')  # Ensure 'value' is numeric
except (IndexError, KeyError, ValueError) as e:
    print("Error processing data: ", e)
    exit()

model = IsolationForest(contamination=0.01)
model.fit(df[['value']])
df['anomaly'] = model.predict(df[['value']])

if df['anomaly'].iloc[-1] == -1:  
    os.system("docker restart <container_name>")
