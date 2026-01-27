import pandas as pd
import numpy as np
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import xgboost as xgb

# Add src to path
sys.path.append(str(Path(__file__).parent))

import data_loader as dl
import preprocessing as pp
import model as md

def plot_learning_curve(results):
    """
    Plot training vs validation AUC over boosting rounds.
    """
    epochs = len(results['validation_0']['auc'])
    x_axis = range(0, epochs)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x_axis, results['validation_0']['auc'], label='Train')
    ax.plot(x_axis, results['validation_1']['auc'], label='Validation')
    ax.legend()
    ax.set_ylabel('AUC')
    ax.set_title('XGBoost Learning Curve')
    plt.grid(True)
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    plt.savefig(output_dir / "learning_curve.png")
    print(f"Saved learning curve to {output_dir / 'learning_curve.png'}")
    plt.close()

def plot_feature_importance(model, feature_names):
    """
    Plot Top 20 Feature Importance by Gain.
    """
    importance = model.get_booster().get_score(importance_type='gain')
    # importance is dict {feature: score}
    
    # Map back to names if needed, but XGBoost usually handles names if dataframe passed
    # Sort
    sorted_idx = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:20]
    
    features = [k for k, v in sorted_idx]
    scores = [v for k, v in sorted_idx]
    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.barh(features, scores)
    ax.set_xlabel('Gain (Information provided)')
    ax.set_title('Top 20 Features Importance (XGBoost Gain)')
    ax.invert_yaxis() # Highest on top
    
    output_dir = Path("output")
    plt.savefig(output_dir / "feature_importance.png")
    print(f"Saved feature importance to {output_dir / 'feature_importance.png'}")
    plt.close()

def run_xgboost_analysis():
    print("🧠 Starting Dedicated XGBoost Analysis...")
    
    # FORCE RELOAD to get full data (not just cached 1000 rows)
    data_path = Path("data")
    if (data_path / "prices.parquet").exists():
        print("⚠️ Cache found. Removing to ensure full fetch...")
        (data_path / "prices.parquet").unlink()
    if (data_path / "macro.parquet").exists():
        (data_path / "macro.parquet").unlink()
    if (data_path / "technicals.parquet").exists():
        (data_path / "technicals.parquet").unlink()
        
    prices = dl.load_prices()
    macro = dl.load_macro()
    technicals = dl.load_technicals()
    fundamentals = dl.load_fundamentals()
    
    if prices is None or prices.empty:
        print("❌ Failed to load data.")
        return

    print(f"Loaded Prices: {prices.shape}")
    if fundamentals is not None:
        print(f"Loaded Fundamentals: {fundamentals.shape}")

    # Process
    print("PREPROCESSING...")
    prices = pp.clean_data(prices)
    full_df = pp.merge_data(prices, technicals, macro, fundamentals)
    labeled_df = pp.create_target(full_df, horizon=20)
    
    # Filter features
    drop_cols = ['id', 'symbol', 'ticker', 'date', 'trade_date', 'fetched_at', 
                 'close_future', 'fwd_return', 'target', 'created_at', 'updated_at',
                 'provider_code', 'series_id', 'currency', 'exchange']
    feature_cols = [c for c in labeled_df.columns if c not in drop_cols and not str(c).endswith('_at') and not str(c).endswith('_id')]
    
    X = labeled_df[feature_cols].select_dtypes(include=[np.number])
    y = labeled_df['target']
    X['date'] = labeled_df['date'] # For split
    
    print(f"Dataset Size: {len(X)} rows")
    
    X_train, X_val, X_test = pp.temporal_split(X)
    y_train = y.loc[X_train.index]
    y_val = y.loc[X_val.index]
    y_test = y.loc[X_test.index]
    
    X_train = X_train.drop(columns=['date'])
    X_val = X_val.drop(columns=['date'])
    X_test = X_test.drop(columns=['date'])
    
    print("🤖 Training XGBoost...")
    model = md.XGBoostModel()
    model.train(X_train, y_train, X_val, y_val)
    
    print("📊 Evaluating...")
    metrics = model.evaluate(X_test, y_test)
    print(f"\n🏆 TEST RESULTS:\nAUC: {metrics['AUC']:.4f}\nAccuracy: {metrics['Accuracy']:.4f}")
    
    # Analysis
    results = model.model.evals_result()
    plot_learning_curve(results)
    plot_feature_importance(model.model, X_train.columns)
    
    print("Done.")

if __name__ == "__main__":
    run_xgboost_analysis()
