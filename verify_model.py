import joblib

artifact = joblib.load('models/model_scoring.pkl')
print('✅ Model loaded successfully')
print(f'\n📦 Keys in artifact: {list(artifact.keys())}')
print(f'\n🎯 Features: {artifact.get("features")}')
print(f'\n📊 Metrics:')
metrics = artifact.get('metrics', {})
for key, val in metrics.items():
    print(f'   {key}: {val:.4f}' if isinstance(val, (int, float)) else f'   {key}: {val}')
