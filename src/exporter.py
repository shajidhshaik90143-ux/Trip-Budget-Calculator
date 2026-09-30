import io
import json
import pandas as pd

def make_csv(rows):
    df = pd.DataFrame(rows)
    return df.to_csv(index=False).encode("utf-8")

def make_json(data):
    return json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
