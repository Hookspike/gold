import requests

response = requests.get('http://localhost:5000/api/predictions')
data = response.json()

print("预测数据:")
print(f"Success: {data.get('success')}")
print(f"Data keys: {data.get('data', {}).keys() if data.get('data') else 'None'}")

if data.get('data'):
    predictions = data['data'].get('predictions', {})
    print(f"\nPredictions type: {type(predictions)}")
    print(f"Predictions keys: {list(predictions.keys()) if isinstance(predictions, dict) else 'Not a dict'}")
    
    if isinstance(predictions, dict):
        for key, value in list(predictions.items())[:5]:
            print(f"\n{key}: {value}")
