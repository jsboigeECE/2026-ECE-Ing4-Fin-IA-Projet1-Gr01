
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import xgboost as xgb
import json
import shap

# Add src to path
sys.path.append(str(Path.cwd()))

import src.data_loader as dl
import src.preprocessing as pp
import src.explainability as xai
import src.llm_utils as llm

print("Loading Model...")
model = xgb.XGBClassifier()
model.load_model("output/latest_model.json")

with open("output/feature_cols.json", "r") as f:
    feature_cols = json.load(f)

print(f"Model Loaded. Features: {len(feature_cols)}")

# Create Dummy Input
print("Creating Dummy Input...")
dummy_data = {col: [0.0] for col in feature_cols}
X_latest = pd.DataFrame(dummy_data)

print("Running explain_latest...")
try:
    explanation = xai.explain_latest(model, X_latest)
    print("Explanation Success!")
    print(explanation)
except Exception as e:
    print("Caught Exception in explain_latest:")
    print(e)
    import traceback
    traceback.print_exc()

print("Testing LLM generation...")
try:
    mock_explanation = {
        'prediction': 'LONG',
        'confidence': 0.75,
        'base_value': 0.5,
        'bullish_args': [{'text': 'Test Bull', 'shap': 0.1}],
        'bearish_args': [{'text': 'Test Bear', 'shap': -0.05}]
    }
    commentary = llm.generate_market_commentary('AAPL', mock_explanation)
    print("Commentary:")
    print(commentary)
except Exception as e:
    print("Caught Exception in LLM:")
    print(e)
    import traceback
    traceback.print_exc()
