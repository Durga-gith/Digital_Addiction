import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from app.ml_predictor import predict_addiction_level

test_cases = [
    {
        'depression': 5,
        'anxiety': 8,
        'stress': 6,
        'self_esteem': 25,
        'app_usage_min': 120,
        'screen_time_hours': 4.5,
        'data_usage_mb': 800,
        'battery_drain_mah': 1800,
        'apps_installed': 35,
        'age': 28
    },
    {
        'depression': 15,
        'anxiety': 18,
        'stress': 16,
        'self_esteem': 18,
        'app_usage_min': 240,
        'screen_time_hours': 7.5,
        'data_usage_mb': 2000,
        'battery_drain_mah': 2800,
        'apps_installed': 65,
        'age': 22
    },
    {
        'depression': 25,
        'anxiety': 28,
        'stress': 26,
        'self_esteem': 10,
        'app_usage_min': 420,
        'screen_time_hours': 10.5,
        'data_usage_mb': 4500,
        'battery_drain_mah': 3800,
        'apps_installed': 95,
        'age': 19
    }
]

print("Testing ML Models...")
print("=" * 60)

for i, test_case in enumerate(test_cases, 1):
    print(f"\nTest Case {i}:")
    result = predict_addiction_level(**test_case)
    
    print(f"Depression: {test_case['depression']}/30")
    print(f"Anxiety: {test_case['anxiety']}/30")
    print(f"Stress: {test_case['stress']}/30")
    print(f"Self-esteem: {test_case['self_esteem']}/30")
    print(f"Screen time: {test_case['screen_time_hours']} hours")
    print(f"App usage: {test_case['app_usage_min']} minutes")
    print(f"\nPrediction: {result['addiction_level']}")
    print(f"Risk Score: {result['risk_score']:.2f}")
    print(f"Confidence: {result.get('prediction_confidence', 'N/A')}")
    
    if 'model_predictions' in result:
        print(f"Model Predictions: {result['model_predictions']}")
    
    print(f"\nRecommendations:")
    for rec in result['recommendations']:
        print(f"  • {rec}")
    
    print("-" * 60)

print("\n" + "=" * 60)
print("Model testing complete!")