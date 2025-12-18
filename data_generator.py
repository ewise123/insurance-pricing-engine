"""
Synthetic Life Insurance Data Generator
Generates realistic historical and new customer data for pricing engine demo
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
from pathlib import Path

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv('DATA_DIR', BASE_DIR))
DATA_DIR.mkdir(parents=True, exist_ok=True)

class LifeInsuranceDataGenerator:
    """Generate synthetic life insurance customer data with realistic correlations"""
    
    def __init__(self):
        self.occupations = {
            'Class I (Low Risk)': ['Software Engineer', 'Accountant', 'Teacher', 'Manager', 'Analyst', 'Designer'],
            'Class II (Moderate Risk)': ['Electrician', 'Plumber', 'Mechanic', 'Sales Rep', 'Nurse', 'Chef'],
            'Class III (High Risk)': ['Construction Worker', 'Truck Driver', 'Warehouse Worker', 'Factory Worker'],
            'Class IV (Very High Risk)': ['Firefighter', 'Police Officer', 'Roofer', 'Logger', 'Pilot']
        }
        
        self.chronic_conditions = [
            'None', 'Hypertension', 'High Cholesterol', 'Diabetes Type 2', 
            'Asthma', 'Arthritis', 'Thyroid Disorder'
        ]
        
        self.family_history = [
            'None', 'Heart Disease', 'Cancer', 'Diabetes', 'Stroke', 'Alzheimer\'s'
        ]
        
        self.hobbies = [
            'None', 'Skydiving', 'Scuba Diving', 'Rock Climbing', 
            'Motorcycle Racing', 'Base Jumping', 'Skiing'
        ]
    
    def generate_customer(self, customer_id, for_historical=True):
        """Generate a single customer with correlated attributes"""
        
        # Core demographics
        age = np.random.normal(45, 12)
        age = max(18, min(75, age))  # Clip to reasonable range
        
        gender = random.choice(['Male', 'Female'])
        
        # Occupation (correlated with age and education)
        occupation_class = random.choices(
            list(self.occupations.keys()),
            weights=[0.4, 0.35, 0.2, 0.05],  # Most people in safer jobs
            k=1
        )[0]
        occupation = random.choice(self.occupations[occupation_class])
        
        # Health metrics (correlated with age)
        height_inches = np.random.normal(67 if gender == 'Male' else 64, 3)
        
        # BMI increases with age
        base_bmi = 22 + (age - 30) * 0.15
        bmi = np.random.normal(base_bmi, 4)
        bmi = max(17, min(45, bmi))
        
        weight_lbs = (bmi * (height_inches ** 2)) / 703
        
        # Blood pressure (increases with age and BMI)
        systolic_bp = 100 + age * 0.5 + (bmi - 25) * 0.8 + np.random.normal(0, 10)
        systolic_bp = max(90, min(180, systolic_bp))
        
        diastolic_bp = 60 + age * 0.2 + (bmi - 25) * 0.4 + np.random.normal(0, 8)
        diastolic_bp = max(60, min(110, diastolic_bp))
        
        # Cholesterol (correlated with age and BMI)
        total_cholesterol = 150 + age * 0.8 + (bmi - 25) * 2 + np.random.normal(0, 20)
        total_cholesterol = max(120, min(300, total_cholesterol))
        
        hdl_cholesterol = 55 - (bmi - 25) * 0.5 + np.random.normal(0, 10)
        hdl_cholesterol = max(30, min(80, hdl_cholesterol))
        
        ldl_cholesterol = total_cholesterol - hdl_cholesterol - 20
        
        # Smoking (decreases with age after 40)
        smoking_prob = 0.15 if age < 40 else 0.10
        smoking_status = random.choices(
            ['Never', 'Former (>5 years)', 'Former (<5 years)', 'Current'],
            weights=[0.6, 0.2, smoking_prob, smoking_prob],
            k=1
        )[0]
        
        # Alcohol (correlated with occupation class)
        alcohol_risk_factor = 1.3 if 'High Risk' in occupation_class else 1.0
        alcohol_consumption = random.choices(
            ['None', 'Light (1-2/week)', 'Moderate (3-7/week)', 'Heavy (>7/week)'],
            weights=[0.2, 0.5 * alcohol_risk_factor, 0.25, 0.05 * alcohol_risk_factor],
            k=1
        )[0]
        
        # Exercise (inversely correlated with BMI)
        exercise_prob = max(0.3, 0.8 - (bmi - 22) * 0.02)
        exercise_frequency = random.choices(
            ['Sedentary', 'Light (1-2/week)', 'Moderate (3-4/week)', 'Active (5+/week)'],
            weights=[0.25, 0.35, 0.25, 0.15],
            k=1
        )[0]
        
        # Chronic conditions (probability increases with age and BMI)
        chronic_condition_prob = 0.1 + (age - 30) * 0.01 + (bmi - 25) * 0.015
        chronic_condition_prob = max(0, min(0.7, chronic_condition_prob))
        
        chronic_conditions_list = []
        if random.random() < chronic_condition_prob:
            num_conditions = random.choices([1, 2, 3], weights=[0.7, 0.25, 0.05], k=1)[0]
            chronic_conditions_list = random.sample(self.chronic_conditions[1:], min(num_conditions, len(self.chronic_conditions)-1))
        
        chronic_conditions = '; '.join(chronic_conditions_list) if chronic_conditions_list else 'None'
        
        # Family history (30% have something)
        family_history = 'None'
        if random.random() < 0.3:
            num_history = random.choices([1, 2], weights=[0.8, 0.2], k=1)[0]
            family_history_list = random.sample(self.family_history[1:], min(num_history, len(self.family_history)-1))
            family_history = '; '.join(family_history_list)
        
        # Dangerous hobbies (5% have one)
        dangerous_hobby = 'None'
        if random.random() < 0.05:
            dangerous_hobby = random.choice(self.hobbies[1:])
        
        # Financial data
        # Income correlated with age and occupation
        base_income = {
            'Class I (Low Risk)': 85000,
            'Class II (Moderate Risk)': 60000,
            'Class III (High Risk)': 50000,
            'Class IV (Very High Risk)': 55000
        }[occupation_class]
        
        annual_income = base_income + (age - 35) * 2000 + np.random.normal(0, 15000)
        annual_income = max(30000, annual_income)
        
        # Coverage amount (typically 10-20x income)
        coverage_multiplier = random.uniform(8, 15)
        coverage_amount = round(annual_income * coverage_multiplier / 50000) * 50000  # Round to nearest 50k
        coverage_amount = max(100000, min(5000000, coverage_amount))
        
        # Credit score (correlated with income and age)
        credit_score = 580 + (annual_income / 1000) * 0.5 + (age - 25) * 2 + np.random.normal(0, 40)
        credit_score = max(300, min(850, credit_score))
        
        # Existing policies (probability increases with age and income)
        has_existing = random.random() < (0.1 + age * 0.003 + annual_income / 500000)
        existing_coverage = round(random.uniform(100000, 500000) / 50000) * 50000 if has_existing else 0
        
        customer = {
            'customer_id': customer_id,
            'age': round(age, 1),
            'gender': gender,
            'occupation': occupation,
            'occupation_class': occupation_class,
            'height_inches': round(height_inches, 1),
            'weight_lbs': round(weight_lbs, 1),
            'bmi': round(bmi, 1),
            'blood_pressure_systolic': round(systolic_bp),
            'blood_pressure_diastolic': round(diastolic_bp),
            'total_cholesterol': round(total_cholesterol),
            'hdl_cholesterol': round(hdl_cholesterol),
            'ldl_cholesterol': round(ldl_cholesterol),
            'smoking_status': smoking_status,
            'alcohol_consumption': alcohol_consumption,
            'exercise_frequency': exercise_frequency,
            'chronic_conditions': chronic_conditions,
            'family_history': family_history,
            'dangerous_hobbies': dangerous_hobby,
            'annual_income': round(annual_income),
            'coverage_amount_requested': int(coverage_amount),
            'credit_score': round(credit_score),
            'existing_coverage': int(existing_coverage)
        }
        
        # For historical data, add outcomes and assigned values
        if for_historical:
            customer.update(self._generate_historical_outcomes(customer))
        
        return customer
    
    def _calculate_risk_score(self, customer):
        """Calculate risk score based on customer attributes (0-1 scale, higher = riskier)"""
        risk_score = 0.0
        
        # Age risk (20% of total)
        age = customer['age']
        if age < 30:
            age_risk = 0.1
        elif age < 40:
            age_risk = 0.15
        elif age < 50:
            age_risk = 0.25
        elif age < 60:
            age_risk = 0.4
        elif age < 70:
            age_risk = 0.6
        else:
            age_risk = 0.8
        risk_score += age_risk * 0.20
        
        # Gender risk (5% of total) - actuarial reality
        gender_risk = 0.55 if customer['gender'] == 'Male' else 0.45
        risk_score += gender_risk * 0.05
        
        # Occupation risk (10% of total)
        occupation_risk = {
            'Class I (Low Risk)': 0.2,
            'Class II (Moderate Risk)': 0.4,
            'Class III (High Risk)': 0.7,
            'Class IV (Very High Risk)': 0.9
        }[customer['occupation_class']]
        risk_score += occupation_risk * 0.10
        
        # BMI risk (15% of total)
        bmi = customer['bmi']
        if bmi < 18.5:
            bmi_risk = 0.4  # Underweight
        elif bmi < 25:
            bmi_risk = 0.2  # Normal
        elif bmi < 30:
            bmi_risk = 0.4  # Overweight
        elif bmi < 35:
            bmi_risk = 0.6  # Obese I
        elif bmi < 40:
            bmi_risk = 0.8  # Obese II
        else:
            bmi_risk = 0.95  # Obese III
        risk_score += bmi_risk * 0.15
        
        # Blood pressure risk (10% of total)
        systolic = customer['blood_pressure_systolic']
        if systolic < 120:
            bp_risk = 0.1
        elif systolic < 130:
            bp_risk = 0.3
        elif systolic < 140:
            bp_risk = 0.5
        elif systolic < 160:
            bp_risk = 0.7
        else:
            bp_risk = 0.9
        risk_score += bp_risk * 0.10
        
        # Cholesterol risk (8% of total)
        total_chol = customer['total_cholesterol']
        if total_chol < 200:
            chol_risk = 0.2
        elif total_chol < 240:
            chol_risk = 0.5
        else:
            chol_risk = 0.8
        risk_score += chol_risk * 0.08
        
        # Smoking risk (15% of total) - HUGE factor
        smoking_risk = {
            'Never': 0.1,
            'Former (>5 years)': 0.3,
            'Former (<5 years)': 0.5,
            'Current': 0.95
        }[customer['smoking_status']]
        risk_score += smoking_risk * 0.15
        
        # Alcohol risk (5% of total)
        alcohol_risk = {
            'None': 0.2,
            'Light (1-2/week)': 0.25,
            'Moderate (3-7/week)': 0.4,
            'Heavy (>7/week)': 0.8
        }[customer['alcohol_consumption']]
        risk_score += alcohol_risk * 0.05
        
        # Exercise benefit (4% of total)
        exercise_risk = {
            'Sedentary': 0.7,
            'Light (1-2/week)': 0.5,
            'Moderate (3-4/week)': 0.3,
            'Active (5+/week)': 0.15
        }[customer['exercise_frequency']]
        risk_score += exercise_risk * 0.04
        
        # Chronic conditions (10% of total)
        if customer['chronic_conditions'] == 'None':
            chronic_risk = 0.1
        else:
            num_conditions = len(customer['chronic_conditions'].split(';'))
            chronic_risk = min(0.95, 0.4 + num_conditions * 0.2)
        risk_score += chronic_risk * 0.10
        
        # Family history (5% of total)
        if customer['family_history'] == 'None':
            family_risk = 0.2
        else:
            num_history = len(customer['family_history'].split(';'))
            family_risk = min(0.8, 0.4 + num_history * 0.2)
        risk_score += family_risk * 0.05
        
        # Dangerous hobbies (3% of total)
        hobby_risk = 0.1 if customer['dangerous_hobbies'] == 'None' else 0.9
        risk_score += hobby_risk * 0.03
        
        return min(0.99, max(0.01, risk_score))
    
    def _generate_historical_outcomes(self, customer):
        """Generate historical risk score, pricing, and outcomes"""
        
        # Calculate base risk score
        risk_score = self._calculate_risk_score(customer)
        
        # Add some noise to simulate underwriter adjustments
        risk_score_assigned = risk_score + np.random.normal(0, 0.03)
        risk_score_assigned = max(0.01, min(0.99, risk_score_assigned))
        
        # Calculate pricing
        # Base annual premium per $1000 of coverage (varies by age)
        age = customer['age']
        if age < 30:
            base_rate = 0.60
        elif age < 40:
            base_rate = 0.80
        elif age < 50:
            base_rate = 1.50
        elif age < 60:
            base_rate = 3.00
        else:
            base_rate = 6.00
        
        # Risk multiplier (risk score of 0.5 = 1x, 0.9 = 3x, etc.)
        risk_multiplier = 0.5 + (risk_score_assigned * 3)
        
        # Calculate base premium
        coverage_thousands = customer['coverage_amount_requested'] / 1000
        base_annual_premium = base_rate * coverage_thousands * risk_multiplier
        
        # Price boundaries
        # Low boundary: break-even (no profit margin)
        low_boundary = base_annual_premium * 0.85
        
        # High boundary: competitive limit (where we lose customers)
        high_boundary = base_annual_premium * 1.25
        
        # Assigned price (what underwriter chose)
        # Usually between base and high, with preference toward higher prices for lower risk
        if risk_score_assigned < 0.3:
            # Low risk - price aggressively
            price_position = random.uniform(0.3, 0.6)  # Closer to base
        elif risk_score_assigned < 0.6:
            # Medium risk - middle ground
            price_position = random.uniform(0.4, 0.7)
        else:
            # High risk - price conservatively
            price_position = random.uniform(0.6, 0.9)
        
        annual_premium_assigned = low_boundary + (high_boundary - low_boundary) * price_position
        
        # Policy status (did they accept? still active?)
        # Lower prices relative to high boundary = higher acceptance
        price_ratio = (annual_premium_assigned - low_boundary) / (high_boundary - low_boundary)
        acceptance_probability = 0.95 - (price_ratio * 0.4)  # 95% at low, 55% at high
        
        policy_accepted = random.random() < acceptance_probability
        
        # If accepted, determine if still active (lapsed?)
        # Higher prices = higher lapse rate
        if policy_accepted:
            lapse_probability = 0.05 + (price_ratio * 0.15)  # 5-20% lapse rate
            policy_active = random.random() > lapse_probability
        else:
            policy_active = False
        
        # Claims (only relevant if policy accepted and active)
        claim_filed = False
        claim_amount = 0
        
        if policy_accepted and policy_active:
            # Claim probability based on risk score
            annual_claim_probability = risk_score_assigned * 0.005  # 0.05% - 0.5% per year
            claim_filed = random.random() < annual_claim_probability
            
            if claim_filed:
                # Most claims are for full coverage (death benefit)
                claim_amount = customer['coverage_amount_requested']
        
        # Underwriter notes (simulated)
        notes_options = [
            "Standard approval",
            "Approved with standard rating",
            "Medical records reviewed - approved",
            "Elevated risk noted but within acceptable range",
            "Premium adjusted for occupation risk",
            "Good health profile, preferred pricing",
            "Multiple risk factors present",
            "Required additional medical exam"
        ]
        
        underwriter_notes = random.choice(notes_options)
        
        return {
            'risk_score_calculated': round(risk_score, 4),
            'risk_score_assigned': round(risk_score_assigned, 4),
            'annual_premium_low_boundary': round(low_boundary, 2),
            'annual_premium_high_boundary': round(high_boundary, 2),
            'annual_premium_assigned': round(annual_premium_assigned, 2),
            'policy_accepted': policy_accepted,
            'policy_active': policy_active,
            'claim_filed': claim_filed,
            'claim_amount': claim_amount,
            'underwriter_notes': underwriter_notes,
            'policy_issue_date': (datetime.now() - timedelta(days=random.randint(365, 1825))).strftime('%Y-%m-%d')
        }
    
    def generate_historical_dataset(self, n_customers=10000):
        """Generate historical customer dataset"""
        print(f"Generating {n_customers} historical customers...")
        customers = []
        
        for i in range(n_customers):
            if (i + 1) % 1000 == 0:
                print(f"  Generated {i + 1}/{n_customers} customers...")
            
            customer = self.generate_customer(f"HIST-{i+1:06d}", for_historical=True)
            customers.append(customer)
        
        df = pd.DataFrame(customers)
        print(f"Historical dataset complete: {len(df)} customers")
        return df
    
    def generate_new_customers(self, n_customers=500):
        """Generate new customers for scoring"""
        print(f"Generating {n_customers} new customers...")
        customers = []
        
        for i in range(n_customers):
            customer = self.generate_customer(f"NEW-{i+1:04d}", for_historical=False)
            customers.append(customer)
        
        df = pd.DataFrame(customers)
        print(f"New customer dataset complete: {len(df)} customers")
        return df


def main():
    """Generate both datasets"""
    generator = LifeInsuranceDataGenerator()
    
    print("=" * 60)
    print("Life Insurance Synthetic Data Generator")
    print("=" * 60)
    print()
    
    # Generate historical data
    historical_df = generator.generate_historical_dataset(10000)
    historical_file = DATA_DIR / 'historical_customers.csv'
    historical_df.to_csv(historical_file, index=False)
    print(f"Saved to: {historical_file}")
    print()
    
    # Generate new customers
    new_df = generator.generate_new_customers(500)
    new_file = DATA_DIR / 'new_customers.csv'
    new_df.to_csv(new_file, index=False)
    print(f"Saved to: {new_file}")
    print()
    
    # Print summary statistics
    print("=" * 60)
    print("HISTORICAL DATA SUMMARY")
    print("=" * 60)
    print(f"Total customers: {len(historical_df)}")
    print(f"Average age: {historical_df['age'].mean():.1f} years")
    print(f"Average risk score: {historical_df['risk_score_assigned'].mean():.3f}")
    print(f"Average premium: ${historical_df['annual_premium_assigned'].mean():,.2f}")
    print(f"Policy acceptance rate: {historical_df['policy_accepted'].mean()*100:.1f}%")
    print(f"Active policy rate: {historical_df['policy_active'].mean()*100:.1f}%")
    print(f"Claims filed: {historical_df['claim_filed'].sum()} ({historical_df['claim_filed'].mean()*100:.2f}%)")
    print()
    
    print("=" * 60)
    print("NEW CUSTOMERS SUMMARY")
    print("=" * 60)
    print(f"Total customers: {len(new_df)}")
    print(f"Average age: {new_df['age'].mean():.1f} years")
    print(f"Average coverage requested: ${new_df['coverage_amount_requested'].mean():,.0f}")
    print()
    
    print("Data generation complete!")


if __name__ == "__main__":
    main()
