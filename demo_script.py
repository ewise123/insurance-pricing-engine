"""
Demo script to show the pricing engine working
"""
import sys
sys.path.append('/home/claude')

import os
from pathlib import Path
from backend_api import RiskScoringEngine, normalize_customer_inputs
import pandas as pd
import json

# Resolve data paths relative to the repository (or DATA_DIR override)
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv('DATA_DIR', BASE_DIR))
NEW_CUSTOMERS_PATH = DATA_DIR / 'new_customers.csv'
HISTORICAL_DATA_PATH = DATA_DIR / 'historical_customers.csv'
OUTPUT_PATH = DATA_DIR / 'sample_scoring_result.json'

# Load a customer from the new customers file
print("Loading sample customer...")
df = pd.read_csv(NEW_CUSTOMERS_PATH)
customer = normalize_customer_inputs(df.iloc[0].to_dict())

print(f"\n{'='*70}")
print(f"PROCESSING CUSTOMER: {customer['customer_id']}")
print(f"{'='*70}\n")

# Initialize the engine
engine = RiskScoringEngine(historical_data_path=HISTORICAL_DATA_PATH)

# Score the customer
print("Analyzing risk factors...\n")
result = engine.score_customer(customer)

# Display results step by step
print(f"{'='*70}")
print("RISK FACTOR ANALYSIS")
print(f"{'='*70}\n")

cumulative_score = 0
for i, step in enumerate(result.scoring_steps, 1):
    cumulative_score += step.weighted_score
    print(f"{i}. {step.factor} ({step.category})")
    print(f"   Value: {step.value}")
    print(f"   Risk Contribution: {step.risk_contribution:.3f}")
    print(f"   Weight: {step.weight*100:.0f}%")
    print(f"   Weighted Score: +{step.weighted_score:.4f}")
    print(f"   Cumulative Risk: {cumulative_score:.4f}")
    print(f"\n   Explanation: {step.explanation}")
    
    if step.supporting_data:
        print(f"\n   Supporting Data:")
        for key, value in step.supporting_data.items():
            print(f"     • {key}: {value}")
    print(f"\n{'-'*70}\n")

# Display final results
print(f"\n{'='*70}")
print("FINAL RESULTS")
print(f"{'='*70}\n")
print(f"Final Risk Score: {result.final_risk_score:.4f}")
print(f"Confidence Level: {result.confidence_level}")
print(f"\nPricing Recommendation:")
print(f"  • Low Boundary:  ${result.annual_premium_low:,.2f}")
print(f"  • Recommended:   ${result.annual_premium_recommended:,.2f}")
print(f"  • High Boundary: ${result.annual_premium_high:,.2f}")
print(f"\n{'='*70}")
print("EXECUTIVE SUMMARY")
print(f"{'='*70}")
print(result.summary)

# Save detailed results to JSON
output_data = {
    'customer_id': result.customer_id,
    'final_risk_score': result.final_risk_score,
    'pricing': {
        'low': result.annual_premium_low,
        'recommended': result.annual_premium_recommended,
        'high': result.annual_premium_high
    },
    'scoring_steps': [
        {
            'category': step.category,
            'factor': step.factor,
            'value': step.value,
            'risk_contribution': step.risk_contribution,
            'weight': step.weight,
            'weighted_score': step.weighted_score,
            'explanation': step.explanation,
            'supporting_data': step.supporting_data
        }
        for step in result.scoring_steps
    ],
    'summary': result.summary,
    'confidence_level': result.confidence_level
}

with open(OUTPUT_PATH, 'w') as f:
    json.dump(output_data, f, indent=2)

print(f"\nDetailed results saved to sample_scoring_result.json")
