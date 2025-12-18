"""
Life Insurance Pricing Engine - Backend API
FastAPI server that processes customer data and generates risk scores with detailed explanations
Now with AI-powered pattern analysis using Claude
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from io import StringIO
import uvicorn
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.getenv("DATA_DIR", BASE_DIR)
DEFAULT_HISTORICAL_PATH = os.path.join(DATA_DIR, "historical_customers.csv")
DEFAULT_NEW_CUSTOMERS_PATH = os.path.join(DATA_DIR, "new_customers.csv")

# Load environment variables
load_dotenv()

# Import AI components (conditional on API key)
try:
    from ai_pattern_analyzer import PatternAnalyzer, format_pattern_for_display
    from ai_cache import AICache
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("AI modules not available - install dependencies: pip install anthropic python-dotenv")

app = FastAPI(title="Life Insurance Pricing Engine API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CustomerInput(BaseModel):
    """Single customer data for scoring"""
    customer_id: str
    age: float
    gender: str
    occupation: str
    occupation_class: str
    height_inches: float
    weight_lbs: float
    bmi: float
    blood_pressure_systolic: int
    blood_pressure_diastolic: int
    total_cholesterol: int
    hdl_cholesterol: int
    ldl_cholesterol: int
    smoking_status: str
    alcohol_consumption: str
    exercise_frequency: str
    chronic_conditions: str
    family_history: str
    dangerous_hobbies: str
    annual_income: int
    coverage_amount_requested: int
    credit_score: int
    existing_coverage: int


class ScoringStep(BaseModel):
    """Individual step in the scoring process"""
    category: str
    factor: str
    value: Any
    risk_contribution: float
    weight: float
    weighted_score: float
    explanation: str
    supporting_data: Dict[str, Any]


class PricingResult(BaseModel):
    """Complete pricing result for a customer"""
    customer_id: str
    final_risk_score: float
    annual_premium_low: float
    annual_premium_calculated: float
    annual_premium_recommended: float
    annual_premium_high: float
    predicted_policy_duration_years: float
    attrition_likelihood: float
    scoring_steps: List[ScoringStep]
    summary: str
    confidence_level: str
    ai_pattern_analysis: Optional[Dict] = None  # AI-powered pattern insights


def _normalize_string_field(value: Any, default: str = "None") -> str:
    """Normalize text fields, handling NaN/None consistently."""
    if value is None:
        return default
    if isinstance(value, float) and np.isnan(value):
        return default
    val = str(value).strip()
    if val.lower() in ("nan", ""):
        return default
    return val


def normalize_customer_inputs(customer: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure customer dict has clean string values for text fields."""
    normalized = dict(customer)
    text_fields = [
        "gender",
        "occupation",
        "occupation_class",
        "smoking_status",
        "alcohol_consumption",
        "exercise_frequency",
        "chronic_conditions",
        "family_history",
        "dangerous_hobbies",
    ]
    for field in text_fields:
        normalized[field] = _normalize_string_field(normalized.get(field))
    return normalized


class RiskScoringEngine:
    """Main risk scoring engine with detailed explanations"""
    
    def __init__(self, historical_data_path: Optional[str] = None):
        self.historical_data = None
        if historical_data_path:
            self.historical_data = pd.read_csv(historical_data_path)
    
    def score_customer(self, customer: Dict[str, Any]) -> PricingResult:
        """Score a single customer with detailed step-by-step logging"""
        customer = normalize_customer_inputs(customer)
        
        scoring_steps = []
        total_risk_score = 0.0
        
        # 1. AGE RISK (20% weight)
        age_step = self._score_age(customer)
        scoring_steps.append(age_step)
        total_risk_score += age_step.weighted_score
        
        # 2. GENDER RISK (5% weight)
        gender_step = self._score_gender(customer)
        scoring_steps.append(gender_step)
        total_risk_score += gender_step.weighted_score
        
        # 3. OCCUPATION RISK (10% weight)
        occupation_step = self._score_occupation(customer)
        scoring_steps.append(occupation_step)
        total_risk_score += occupation_step.weighted_score
        
        # 4. BMI RISK (15% weight)
        bmi_step = self._score_bmi(customer)
        scoring_steps.append(bmi_step)
        total_risk_score += bmi_step.weighted_score
        
        # 5. BLOOD PRESSURE RISK (10% weight)
        bp_step = self._score_blood_pressure(customer)
        scoring_steps.append(bp_step)
        total_risk_score += bp_step.weighted_score
        
        # 6. CHOLESTEROL RISK (8% weight)
        chol_step = self._score_cholesterol(customer)
        scoring_steps.append(chol_step)
        total_risk_score += chol_step.weighted_score
        
        # 7. SMOKING RISK (15% weight)
        smoking_step = self._score_smoking(customer)
        scoring_steps.append(smoking_step)
        total_risk_score += smoking_step.weighted_score
        
        # 8. ALCOHOL RISK (5% weight)
        alcohol_step = self._score_alcohol(customer)
        scoring_steps.append(alcohol_step)
        total_risk_score += alcohol_step.weighted_score
        
        # 9. EXERCISE BENEFIT (4% weight)
        exercise_step = self._score_exercise(customer)
        scoring_steps.append(exercise_step)
        total_risk_score += exercise_step.weighted_score
        
        # 10. CHRONIC CONDITIONS (10% weight)
        chronic_step = self._score_chronic_conditions(customer)
        scoring_steps.append(chronic_step)
        total_risk_score += chronic_step.weighted_score
        
        # 11. FAMILY HISTORY (5% weight)
        family_step = self._score_family_history(customer)
        scoring_steps.append(family_step)
        total_risk_score += family_step.weighted_score
        
        # 12. DANGEROUS HOBBIES (3% weight)
        hobby_step = self._score_hobbies(customer)
        scoring_steps.append(hobby_step)
        total_risk_score += hobby_step.weighted_score
        
        # Calculate pricing
        pricing = self._calculate_pricing(customer, total_risk_score)
        
        # Generate summary
        summary = self._generate_summary(customer, total_risk_score, scoring_steps, pricing)
        
        # Determine confidence level
        confidence = self._calculate_confidence(customer, scoring_steps)
        
        # Estimate policy duration and attrition likelihood
        policy_metrics = self._estimate_policy_metrics(customer, total_risk_score)
        
        return PricingResult(
            customer_id=customer['customer_id'],
            final_risk_score=round(total_risk_score, 4),
            annual_premium_low=round(pricing['low'], 2),
            annual_premium_calculated=round(pricing['calculated'], 2),
            annual_premium_recommended=round(pricing['recommended'], 2),
            annual_premium_high=round(pricing['high'], 2),
            predicted_policy_duration_years=round(policy_metrics['predicted_duration_years'], 1),
            attrition_likelihood=round(policy_metrics['attrition_likelihood'], 3),
            scoring_steps=scoring_steps,
            summary=summary,
            confidence_level=confidence
        )
    
    def _score_age(self, customer: Dict) -> ScoringStep:
        """Score age risk factor"""
        age = customer['age']
        weight = 0.20
        
        # Age-based risk tiers
        if age < 30:
            risk = 0.1
            tier = "under 30"
        elif age < 40:
            risk = 0.15
            tier = "30-39"
        elif age < 50:
            risk = 0.25
            tier = "40-49"
        elif age < 60:
            risk = 0.4
            tier = "50-59"
        elif age < 70:
            risk = 0.6
            tier = "60-69"
        else:
            risk = 0.8
            tier = "70+"
        
        weighted_score = risk * weight
        
        # Get historical data for comparison
        comparison_data = {}
        if self.historical_data is not None:
            age_cohort = self.historical_data[
                (self.historical_data['age'] >= age - 5) & 
                (self.historical_data['age'] <= age + 5)
            ]
            if len(age_cohort) > 0:
                comparison_data = {
                    'cohort_size': len(age_cohort),
                    'avg_risk_score': round(age_cohort['risk_score_assigned'].mean(), 2),
                    'claim_rate': round(age_cohort['claim_filed'].mean() * 100, 2)
                }
        
        explanation = (
            f"Customer age of {age:.1f} places them in the {tier} bracket. "
            f"Mortality risk increases with age - this age bracket has a base risk factor of {risk:.2f}. "
            f"Actuarial tables show mortality rates increase exponentially after age 50."
        )
        
        if comparison_data:
            explanation += f" In our historical data, customers aged {age-5:.0f}-{age+5:.0f} (n={comparison_data['cohort_size']}) had an average risk score of {comparison_data['avg_risk_score']} with a {comparison_data['claim_rate']}% claim rate."
        
        return ScoringStep(
            category="Demographics",
            factor="Age",
            value=f"{age:.1f} years",
            risk_contribution=risk,
            weight=weight,
            weighted_score=round(weighted_score, 4),
            explanation=explanation,
            supporting_data=comparison_data
        )
    
    def _score_gender(self, customer: Dict) -> ScoringStep:
        """Score gender risk factor"""
        gender = customer['gender']
        weight = 0.05
        
        # Actuarial reality: males have higher mortality
        risk = 0.55 if gender == 'Male' else 0.45
        weighted_score = risk * weight
        
        comparison_data = {}
        if self.historical_data is not None:
            gender_data = self.historical_data[self.historical_data['gender'] == gender]
            if len(gender_data) > 0:
                comparison_data = {
                    'cohort_size': len(gender_data),
                    'avg_risk_score': round(gender_data['risk_score_assigned'].mean(), 2),
                    'avg_premium': round(gender_data['annual_premium_assigned'].mean(), 2)
                }
        
        explanation = (
            f"Gender: {gender}. Actuarial data consistently shows males have 10-15% higher mortality rates "
            f"across most age groups due to higher rates of heart disease, accidents, and risky behaviors. "
            f"This results in a risk factor of {risk:.2f}."
        )
        
        if comparison_data:
            explanation += f" Historical {gender.lower()} customers (n={comparison_data['cohort_size']}) average a {comparison_data['avg_risk_score']} risk score."
        
        return ScoringStep(
            category="Demographics",
            factor="Gender",
            value=gender,
            risk_contribution=risk,
            weight=weight,
            weighted_score=round(weighted_score, 4),
            explanation=explanation,
            supporting_data=comparison_data
        )
    
    def _score_occupation(self, customer: Dict) -> ScoringStep:
        """Score occupation risk factor"""
        occupation = customer['occupation']
        occupation_class = customer['occupation_class']
        weight = 0.10
        
        risk_map = {
            'Class I (Low Risk)': 0.2,
            'Class II (Moderate Risk)': 0.4,
            'Class III (High Risk)': 0.7,
            'Class IV (Very High Risk)': 0.9
        }
        
        risk = risk_map[occupation_class]
        weighted_score = risk * weight
        
        comparison_data = {}
        if self.historical_data is not None:
            occ_data = self.historical_data[self.historical_data['occupation_class'] == occupation_class]
            if len(occ_data) > 0:
                comparison_data = {
                    'cohort_size': len(occ_data),
                    'avg_risk_score': round(occ_data['risk_score_assigned'].mean(), 2),
                    'claim_rate': round(occ_data['claim_filed'].mean() * 100, 2)
                }
        
        explanation = (
            f"Occupation: {occupation} ({occupation_class}). "
            f"Occupational mortality varies significantly based on workplace hazards, stress levels, and accident risk. "
            f"This occupation class carries a {risk:.2f} risk factor."
        )
        
        if comparison_data:
            explanation += f" {occupation_class} workers in our data (n={comparison_data['cohort_size']}) show {comparison_data['claim_rate']}% claim rates."
        
        return ScoringStep(
            category="Demographics",
            factor="Occupation",
            value=f"{occupation} ({occupation_class})",
            risk_contribution=risk,
            weight=weight,
            weighted_score=round(weighted_score, 4),
            explanation=explanation,
            supporting_data=comparison_data
        )
    
    def _score_bmi(self, customer: Dict) -> ScoringStep:
        """Score BMI risk factor"""
        bmi = customer['bmi']
        weight = 0.15
        
        if bmi < 18.5:
            risk = 0.4
            category = "Underweight"
        elif bmi < 25:
            risk = 0.2
            category = "Normal"
        elif bmi < 30:
            risk = 0.4
            category = "Overweight"
        elif bmi < 35:
            risk = 0.6
            category = "Obese Class I"
        elif bmi < 40:
            risk = 0.8
            category = "Obese Class II"
        else:
            risk = 0.95
            category = "Obese Class III"
        
        weighted_score = risk * weight
        
        comparison_data = {}
        if self.historical_data is not None:
            bmi_cohort = self.historical_data[
                (self.historical_data['bmi'] >= bmi - 2) & 
                (self.historical_data['bmi'] <= bmi + 2)
            ]
            if len(bmi_cohort) > 0:
                comparison_data = {
                    'cohort_size': len(bmi_cohort),
                    'avg_risk_score': round(bmi_cohort['risk_score_assigned'].mean(), 2),
                    'chronic_condition_rate': round((bmi_cohort['chronic_conditions'] != 'None').mean() * 100, 2)
                }
        
        explanation = (
            f"BMI: {bmi:.1f} ({category}). "
            f"Body Mass Index is strongly correlated with mortality risk. Both underweight and overweight conditions "
            f"increase mortality through different mechanisms (malnutrition vs. cardiovascular disease, diabetes). "
            f"This BMI level carries a {risk:.2f} risk factor."
        )
        
        if comparison_data:
            explanation += f" Customers with similar BMI (n={comparison_data['cohort_size']}) have {comparison_data['chronic_condition_rate']}% chronic condition rates."
        
        return ScoringStep(
            category="Health Metrics",
            factor="Body Mass Index (BMI)",
            value=f"{bmi:.1f} ({category})",
            risk_contribution=risk,
            weight=weight,
            weighted_score=round(weighted_score, 4),
            explanation=explanation,
            supporting_data=comparison_data
        )
    
    def _score_blood_pressure(self, customer: Dict) -> ScoringStep:
        """Score blood pressure risk factor"""
        systolic = customer['blood_pressure_systolic']
        diastolic = customer['blood_pressure_diastolic']
        weight = 0.10
        
        if systolic < 120:
            risk = 0.1
            category = "Normal"
        elif systolic < 130:
            risk = 0.3
            category = "Elevated"
        elif systolic < 140:
            risk = 0.5
            category = "High (Stage 1)"
        elif systolic < 160:
            risk = 0.7
            category = "High (Stage 2)"
        else:
            risk = 0.9
            category = "Very High (Crisis)"
        
        weighted_score = risk * weight
        
        comparison_data = {}
        if self.historical_data is not None:
            bp_cohort = self.historical_data[
                (self.historical_data['blood_pressure_systolic'] >= systolic - 10) & 
                (self.historical_data['blood_pressure_systolic'] <= systolic + 10)
            ]
            if len(bp_cohort) > 0:
                comparison_data = {
                    'cohort_size': len(bp_cohort),
                    'avg_risk_score': round(bp_cohort['risk_score_assigned'].mean(), 2)
                }
        
        explanation = (
            f"Blood Pressure: {systolic}/{diastolic} mmHg ({category}). "
            f"Hypertension is a leading risk factor for heart disease, stroke, and kidney disease. "
            f"The American Heart Association defines stages based on systolic readings. "
            f"This reading indicates {category.lower()} blood pressure with a {risk:.2f} risk factor."
        )
        
        if comparison_data:
            explanation += f" Customers with similar BP (n={comparison_data['cohort_size']}) average {comparison_data['avg_risk_score']} risk scores."
        
        return ScoringStep(
            category="Health Metrics",
            factor="Blood Pressure",
            value=f"{systolic}/{diastolic} mmHg ({category})",
            risk_contribution=risk,
            weight=weight,
            weighted_score=round(weighted_score, 4),
            explanation=explanation,
            supporting_data=comparison_data
        )
    
    def _score_cholesterol(self, customer: Dict) -> ScoringStep:
        """Score cholesterol risk factor"""
        total_chol = customer['total_cholesterol']
        hdl = customer['hdl_cholesterol']
        ldl = customer['ldl_cholesterol']
        weight = 0.08
        
        if total_chol < 200:
            risk = 0.2
            category = "Desirable"
        elif total_chol < 240:
            risk = 0.5
            category = "Borderline High"
        else:
            risk = 0.8
            category = "High"
        
        weighted_score = risk * weight
        
        comparison_data = {}
        if self.historical_data is not None:
            chol_cohort = self.historical_data[
                (self.historical_data['total_cholesterol'] >= total_chol - 20) & 
                (self.historical_data['total_cholesterol'] <= total_chol + 20)
            ]
            if len(chol_cohort) > 0:
                comparison_data = {
                    'cohort_size': len(chol_cohort),
                    'avg_risk_score': round(chol_cohort['risk_score_assigned'].mean(), 2)
                }
        
        explanation = (
            f"Total Cholesterol: {total_chol} mg/dL (HDL: {hdl}, LDL: {ldl}) - {category}. "
            f"High cholesterol is a major risk factor for atherosclerosis and coronary artery disease. "
            f"LDL ('bad' cholesterol) should be <100 mg/dL ideally, HDL ('good' cholesterol) should be >40 mg/dL. "
            f"This profile indicates {category.lower()} risk with a {risk:.2f} factor."
        )
        
        if comparison_data:
            explanation += f" Similar cholesterol profiles (n={comparison_data['cohort_size']}) average {comparison_data['avg_risk_score']} risk."
        
        return ScoringStep(
            category="Health Metrics",
            factor="Cholesterol",
            value=f"{total_chol} mg/dL ({category})",
            risk_contribution=risk,
            weight=weight,
            weighted_score=round(weighted_score, 4),
            explanation=explanation,
            supporting_data=comparison_data
        )
    
    def _score_smoking(self, customer: Dict) -> ScoringStep:
        """Score smoking risk factor - MAJOR FACTOR"""
        smoking_status = customer['smoking_status']
        weight = 0.15
        
        risk_map = {
            'Never': 0.1,
            'Former (>5 years)': 0.3,
            'Former (<5 years)': 0.5,
            'Current': 0.95
        }
        
        risk = risk_map[smoking_status]
        weighted_score = risk * weight
        
        comparison_data = {}
        if self.historical_data is not None:
            smoking_cohort = self.historical_data[self.historical_data['smoking_status'] == smoking_status]
            if len(smoking_cohort) > 0:
                comparison_data = {
                    'cohort_size': len(smoking_cohort),
                    'avg_risk_score': round(smoking_cohort['risk_score_assigned'].mean(), 2),
                    'avg_premium': round(smoking_cohort['annual_premium_assigned'].mean(), 2)
                }
        
        explanation = (
            f"Smoking Status: {smoking_status}. "
            f"Smoking is THE single largest modifiable risk factor for mortality. "
            f"Current smokers have 2-3x higher mortality rates than non-smokers due to cancer, heart disease, and respiratory illness. "
            f"This status carries a {risk:.2f} risk factor (15% of total score)."
        )
        
        if comparison_data:
            explanation += f" {smoking_status} customers (n={comparison_data['cohort_size']}) average ${comparison_data['avg_premium']:,.0f} annual premiums."
        
        return ScoringStep(
            category="Lifestyle",
            factor="Smoking Status",
            value=smoking_status,
            risk_contribution=risk,
            weight=weight,
            weighted_score=round(weighted_score, 4),
            explanation=explanation,
            supporting_data=comparison_data
        )
    
    def _score_alcohol(self, customer: Dict) -> ScoringStep:
        """Score alcohol consumption risk factor"""
        alcohol = customer['alcohol_consumption']
        weight = 0.05
        
        risk_map = {
            'None': 0.2,
            'Light (1-2/week)': 0.25,
            'Moderate (3-7/week)': 0.4,
            'Heavy (>7/week)': 0.8
        }
        
        risk = risk_map[alcohol]
        weighted_score = risk * weight
        
        comparison_data = {}
        if self.historical_data is not None:
            alcohol_cohort = self.historical_data[self.historical_data['alcohol_consumption'] == alcohol]
            if len(alcohol_cohort) > 0:
                comparison_data = {
                    'cohort_size': len(alcohol_cohort),
                    'avg_risk_score': round(alcohol_cohort['risk_score_assigned'].mean(), 2)
                }
        
        explanation = (
            f"Alcohol Consumption: {alcohol}. "
            f"Heavy alcohol use increases mortality through liver disease, accidents, and cardiovascular issues. "
            f"Moderate consumption shows J-curved mortality (slight benefit vs. none, but heavy use is harmful). "
            f"This consumption level has a {risk:.2f} risk factor."
        )
        
        if comparison_data:
            explanation += f" Customers with {alcohol.lower()} consumption (n={comparison_data['cohort_size']}) average {comparison_data['avg_risk_score']} risk."
        
        return ScoringStep(
            category="Lifestyle",
            factor="Alcohol Consumption",
            value=alcohol,
            risk_contribution=risk,
            weight=weight,
            weighted_score=round(weighted_score, 4),
            explanation=explanation,
            supporting_data=comparison_data
        )
    
    def _score_exercise(self, customer: Dict) -> ScoringStep:
        """Score exercise frequency - PROTECTIVE FACTOR"""
        exercise = customer['exercise_frequency']
        weight = 0.04
        
        risk_map = {
            'Sedentary': 0.7,
            'Light (1-2/week)': 0.5,
            'Moderate (3-4/week)': 0.3,
            'Active (5+/week)': 0.15
        }
        
        risk = risk_map[exercise]
        weighted_score = risk * weight
        
        comparison_data = {}
        if self.historical_data is not None:
            exercise_cohort = self.historical_data[self.historical_data['exercise_frequency'] == exercise]
            if len(exercise_cohort) > 0:
                comparison_data = {
                    'cohort_size': len(exercise_cohort),
                    'avg_risk_score': round(exercise_cohort['risk_score_assigned'].mean(), 2),
                    'avg_bmi': round(exercise_cohort['bmi'].mean(), 1)
                }
        
        explanation = (
            f"Exercise Frequency: {exercise}. "
            f"Regular physical activity is strongly protective against all-cause mortality, reducing risk by 20-30%. "
            f"Exercise improves cardiovascular health, maintains healthy weight, and reduces chronic disease risk. "
            f"This activity level has a {risk:.2f} risk factor."
        )
        
        if comparison_data:
            explanation += f" {exercise} customers (n={comparison_data['cohort_size']}) have average BMI of {comparison_data['avg_bmi']}."
        
        return ScoringStep(
            category="Lifestyle",
            factor="Exercise Frequency",
            value=exercise,
            risk_contribution=risk,
            weight=weight,
            weighted_score=round(weighted_score, 4),
            explanation=explanation,
            supporting_data=comparison_data
        )
    
    def _score_chronic_conditions(self, customer: Dict) -> ScoringStep:
        """Score chronic conditions risk factor"""
        conditions = customer['chronic_conditions']
        weight = 0.10
        
        if conditions == 'None':
            risk = 0.1
            num_conditions = 0
        else:
            num_conditions = len(conditions.split(';'))
            risk = min(0.95, 0.4 + num_conditions * 0.2)
        
        weighted_score = risk * weight
        
        comparison_data = {}
        if self.historical_data is not None:
            if conditions == 'None':
                condition_cohort = self.historical_data[self.historical_data['chronic_conditions'] == 'None']
            else:
                # Find people with similar number of conditions
                condition_cohort = self.historical_data[
                    self.historical_data['chronic_conditions'].str.count(';') == conditions.count(';')
                ]
            
            if len(condition_cohort) > 0:
                comparison_data = {
                    'cohort_size': len(condition_cohort),
                    'avg_risk_score': round(condition_cohort['risk_score_assigned'].mean(), 2),
                    'claim_rate': round(condition_cohort['claim_filed'].mean() * 100, 2)
                }
        
        explanation = (
            f"Chronic Conditions: {conditions}. "
        )
        
        if num_conditions == 0:
            explanation += f"No chronic conditions present, which is favorable. Risk factor: {risk:.2f}."
        else:
            explanation += (
                f"Presence of {num_conditions} chronic condition(s) significantly increases mortality risk. "
                f"Each condition adds compounding risk through disease progression and comorbidity effects. "
                f"Risk factor: {risk:.2f}."
            )
        
        if comparison_data:
            explanation += f" Customers with similar condition profiles (n={comparison_data['cohort_size']}) have {comparison_data['claim_rate']}% claim rates."
        
        return ScoringStep(
            category="Medical History",
            factor="Chronic Conditions",
            value=conditions,
            risk_contribution=risk,
            weight=weight,
            weighted_score=round(weighted_score, 4),
            explanation=explanation,
            supporting_data=comparison_data
        )
    
    def _score_family_history(self, customer: Dict) -> ScoringStep:
        """Score family history risk factor"""
        family_history = customer['family_history']
        weight = 0.05
        
        if family_history == 'None':
            risk = 0.2
            num_history = 0
        else:
            num_history = len(family_history.split(';'))
            risk = min(0.8, 0.4 + num_history * 0.2)
        
        weighted_score = risk * weight
        
        comparison_data = {}
        if self.historical_data is not None:
            if family_history == 'None':
                history_cohort = self.historical_data[self.historical_data['family_history'] == 'None']
            else:
                history_cohort = self.historical_data[
                    self.historical_data['family_history'].str.count(';') == family_history.count(';')
                ]
            
            if len(history_cohort) > 0:
                comparison_data = {
                    'cohort_size': len(history_cohort),
                    'avg_risk_score': round(history_cohort['risk_score_assigned'].mean(), 2)
                }
        
        explanation = (
            f"Family History: {family_history}. "
        )
        
        if num_history == 0:
            explanation += f"No significant family history reported. Risk factor: {risk:.2f}."
        else:
            explanation += (
                f"Family history of {family_history.lower()} indicates genetic predisposition to these conditions. "
                f"Hereditary factors account for significant disease risk, particularly for heart disease and cancer. "
                f"Risk factor: {risk:.2f}."
            )
        
        if comparison_data:
            explanation += f" Similar family histories (n={comparison_data['cohort_size']}) average {comparison_data['avg_risk_score']} risk."
        
        return ScoringStep(
            category="Medical History",
            factor="Family History",
            value=family_history,
            risk_contribution=risk,
            weight=weight,
            weighted_score=round(weighted_score, 4),
            explanation=explanation,
            supporting_data=comparison_data
        )
    
    def _score_hobbies(self, customer: Dict) -> ScoringStep:
        """Score dangerous hobbies risk factor"""
        hobby = customer['dangerous_hobbies']
        weight = 0.03
        
        risk = 0.1 if hobby == 'None' else 0.9
        weighted_score = risk * weight
        
        comparison_data = {}
        if self.historical_data is not None:
            if hobby == 'None':
                hobby_cohort = self.historical_data[self.historical_data['dangerous_hobbies'] == 'None']
            else:
                hobby_cohort = self.historical_data[self.historical_data['dangerous_hobbies'] != 'None']
            
            if len(hobby_cohort) > 0:
                comparison_data = {
                    'cohort_size': len(hobby_cohort),
                    'avg_risk_score': round(hobby_cohort['risk_score_assigned'].mean(), 2)
                }
        
        explanation = (
            f"Dangerous Hobbies: {hobby}. "
        )
        
        if hobby == 'None':
            explanation += f"No high-risk recreational activities reported. Risk factor: {risk:.2f}."
        else:
            explanation += (
                f"Participation in {hobby.lower()} significantly increases accident and fatality risk. "
                f"These activities carry substantially higher mortality rates than general population. "
                f"Risk factor: {risk:.2f}."
            )
        
        if comparison_data:
            explanation += f" Customers with dangerous hobbies (n={comparison_data['cohort_size']}) average {comparison_data['avg_risk_score']} risk."
        
        return ScoringStep(
            category="Lifestyle",
            factor="Dangerous Hobbies",
            value=hobby,
            risk_contribution=risk,
            weight=weight,
            weighted_score=round(weighted_score, 4),
            explanation=explanation,
            supporting_data=comparison_data
        )
    
    def _calculate_pricing(self, customer: Dict, risk_score: float) -> Dict[str, float]:
        """Calculate pricing boundaries based on risk score"""
        age = customer['age']
        
        # Base annual premium per $1000 of coverage (age-dependent)
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
        
        # Risk multiplier (risk score of 0.5 = 1x, higher = more expensive)
        risk_multiplier = 0.5 + (risk_score * 3)
        
        # Calculate base premium
        coverage_thousands = customer['coverage_amount_requested'] / 1000
        base_annual_premium = base_rate * coverage_thousands * risk_multiplier
        
        # Price boundaries
        low_boundary = base_annual_premium * 0.85  # Break-even (no profit)
        high_boundary = base_annual_premium * 1.25  # Competitive limit
        
        # Recommended price (sweet spot based on risk)
        if risk_score < 0.3:
            # Low risk - price aggressively to win business
            recommended = low_boundary + (high_boundary - low_boundary) * 0.4
        elif risk_score < 0.6:
            # Medium risk - middle ground
            recommended = low_boundary + (high_boundary - low_boundary) * 0.6
        else:
            # High risk - price conservatively
            recommended = low_boundary + (high_boundary - low_boundary) * 0.75
        
        return {
            'low': low_boundary,
            'calculated': recommended,  # pure math recommendation
            'recommended': recommended,  # will be AI-adjusted if available
            'high': high_boundary
        }
    
    def _estimate_policy_metrics(self, customer: Dict, risk_score: float) -> Dict[str, float]:
        """Estimate policy duration (years) and attrition likelihood using historical outcomes."""
        def fallback() -> Dict[str, float]:
            duration = max(3.0, min(20.0, 12.0 - (risk_score * 6.0)))
            attrition = max(0.05, min(0.6, 0.12 + (risk_score * 0.25)))
            return {
                'predicted_duration_years': duration,
                'attrition_likelihood': attrition
            }
        
        if self.historical_data is None or self.historical_data.empty:
            return fallback()
        
        df = self.historical_data
        age = customer['age']
        cohort = df[
            (df['age'] >= age - 5) & (df['age'] <= age + 5)
        ]
        cohort = cohort[cohort['occupation_class'] == customer['occupation_class']]
        cohort = cohort[cohort['smoking_status'] == customer['smoking_status']]
        
        if len(cohort) < 50:
            cohort = df[
                (df['age'] >= age - 10) & (df['age'] <= age + 10)
            ]
            cohort = cohort[cohort['smoking_status'] == customer['smoking_status']]
        
        if len(cohort) < 30:
            cohort = df[
                (df['age'] >= age - 10) & (df['age'] <= age + 10)
            ]
        
        accepted = cohort[cohort['policy_accepted'] == True]
        if accepted.empty:
            return fallback()
        
        active_rate = accepted['policy_active'].mean()
        attrition_likelihood = 1.0 - float(active_rate)
        
        issue_dates = pd.to_datetime(accepted['policy_issue_date'], errors='coerce')
        tenure_years = (pd.Timestamp.today() - issue_dates).dt.days / 365.25
        tenure_years = tenure_years.dropna()
        
        if tenure_years.empty:
            return fallback()
        
        active_mask = accepted['policy_active'] == True
        active_tenure = tenure_years[active_mask.values] if len(tenure_years) == len(accepted) else tenure_years
        avg_tenure = active_tenure.mean() if not active_tenure.empty else tenure_years.mean()
        
        predicted_duration_years = max(1.0, min(30.0, float(avg_tenure)))
        attrition_likelihood = max(0.0, min(1.0, float(attrition_likelihood)))
        
        return {
            'predicted_duration_years': predicted_duration_years,
            'attrition_likelihood': attrition_likelihood
        }
    
    def _generate_summary(self, customer: Dict, risk_score: float, steps: List[ScoringStep], pricing: Dict) -> str:
        """Generate executive summary of the risk assessment"""
        
        # Identify top risk contributors
        top_risks = sorted(steps, key=lambda x: x.weighted_score, reverse=True)[:3]
        top_protective = sorted(steps, key=lambda x: x.weighted_score)[:2]
        
        # Risk tier
        if risk_score < 0.25:
            risk_tier = "Very Low Risk - Preferred Pricing"
        elif risk_score < 0.35:
            risk_tier = "Low Risk - Standard Plus"
        elif risk_score < 0.50:
            risk_tier = "Average Risk - Standard"
        elif risk_score < 0.65:
            risk_tier = "Elevated Risk - Standard Rated"
        else:
            risk_tier = "High Risk - Table Rated"
        
        summary = f"""
EXECUTIVE SUMMARY - Customer {customer['customer_id']}
{'=' * 70}

RISK ASSESSMENT: {risk_tier}
Final Risk Score: {risk_score:.2f} (0 = lowest risk, 1 = highest risk)

PRICING RECOMMENDATION:
  • Recommended Annual Premium: ${pricing['recommended']:,.2f}
  • Price Range: ${pricing['low']:,.2f} - ${pricing['high']:,.2f}
  • Coverage Amount: ${customer['coverage_amount_requested']:,.0f}

CUSTOMER PROFILE:
  • Age: {customer['age']:.0f} | Gender: {customer['gender']} | Occupation: {customer['occupation']}
  • BMI: {customer['bmi']:.1f} | BP: {customer['blood_pressure_systolic']}/{customer['blood_pressure_diastolic']}
  • Smoking: {customer['smoking_status']}

TOP RISK FACTORS:
  1. {top_risks[0].factor}: {top_risks[0].value} (+{top_risks[0].weighted_score:.2f} to risk score)
  2. {top_risks[1].factor}: {top_risks[1].value} (+{top_risks[1].weighted_score:.2f} to risk score)
  3. {top_risks[2].factor}: {top_risks[2].value} (+{top_risks[2].weighted_score:.2f} to risk score)

PROTECTIVE FACTORS:
  1. {top_protective[0].factor}: {top_protective[0].value} (Low risk contribution: {top_protective[0].weighted_score:.2f})
  2. {top_protective[1].factor}: {top_protective[1].value} (Low risk contribution: {top_protective[1].weighted_score:.2f})

UNDERWRITER NOTES:
Based on the comprehensive risk assessment across 12 factors, this customer presents a 
{risk_tier.lower()} profile. The pricing recommendation of ${pricing['recommended']:,.2f} annually 
provides adequate margin while remaining competitive in the market. 
"""
        
        if risk_score > 0.6:
            summary += "\nHIGH RISK: Consider requiring additional medical examination or aviation/hobby questionnaire."
        elif risk_score < 0.3:
            summary += "\nPREFERRED RISK: Excellent candidate for accelerated underwriting and competitive pricing."
        
        return summary.strip()
    
    def _calculate_confidence(self, customer: Dict, steps: List[ScoringStep]) -> str:
        """Calculate confidence level in the risk assessment"""
        
        # Factors that reduce confidence
        confidence_score = 1.0
        
        # Very young or very old reduces confidence (less data)
        age = customer['age']
        if age < 25 or age > 70:
            confidence_score *= 0.9
        
        # Extreme risk scores are less common
        total_risk = sum(step.weighted_score for step in steps)
        if total_risk > 0.7:
            confidence_score *= 0.85
        
        # Dangerous hobbies add uncertainty
        if customer['dangerous_hobbies'] != 'None':
            confidence_score *= 0.9
        
        # Multiple chronic conditions add complexity
        if customer['chronic_conditions'] != 'None':
            num_conditions = len(customer['chronic_conditions'].split(';'))
            if num_conditions >= 2:
                confidence_score *= 0.92
        
        if confidence_score >= 0.95:
            return "Very High"
        elif confidence_score >= 0.85:
            return "High"
        elif confidence_score >= 0.75:
            return "Moderate"
        else:
            return "Low"


# Initialize the scoring engine with historical data
engine = RiskScoringEngine(historical_data_path=DEFAULT_HISTORICAL_PATH)

# Initialize AI pattern analyzer if enabled
pattern_analyzer = None
if AI_AVAILABLE and os.getenv('ANTHROPIC_API_KEY') and os.getenv('ENABLE_AI_FEATURES', 'false').lower() == 'true':
    try:
        cache = AICache()
        pattern_analyzer = PatternAnalyzer(engine.historical_data, cache=cache)
        print("AI Pattern Analysis enabled (Claude API)")
        print(f"   Model: {os.getenv('AI_MODEL', 'claude-sonnet-4-20250514')}")
        print(f"   Cache: {cache.get_stats()['cache_dir']}")
    except Exception as e:
        print(f"AI Pattern Analysis failed to initialize: {e}")
        pattern_analyzer = None
else:
    if not AI_AVAILABLE:
        print("AI Pattern Analysis unavailable (missing dependencies)")
    elif not os.getenv('ANTHROPIC_API_KEY'):
        print("AI Pattern Analysis disabled (no ANTHROPIC_API_KEY)")
    else:
        print("AI Pattern Analysis disabled (ENABLE_AI_FEATURES=false)")


@app.post("/api/score-customer", response_model=PricingResult)
async def score_customer(customer: CustomerInput):
    """Score a single customer and return detailed results with AI pattern analysis"""
    try:
        customer_dict = customer.dict()
        
        # Step 1: Deterministic scoring (existing logic)
        result = engine.score_customer(customer_dict)
        
        pattern_insight = None
        # Step 2: AI Pattern Analysis (if enabled)
        if pattern_analyzer:
            try:
                # Get top 3 risk factors
                top_factors = sorted(
                    result.scoring_steps, 
                    key=lambda x: x.weighted_score, 
                    reverse=True
                )[:3]
                
                # Analyze patterns with Claude
                pattern_insight = pattern_analyzer.analyze_customer_patterns(
                    customer=customer_dict,
                    risk_score=result.final_risk_score,
                    top_risk_factors=[
                        {
                            'factor': s.factor,
                            'value': s.value,
                            'weighted_score': s.weighted_score
                        }
                        for s in top_factors
                    ]
                )
                
                # Add to result as additional field
                result.ai_pattern_analysis = format_pattern_for_display(pattern_insight)
                
            except Exception as e:
                print(f"AI Pattern Analysis failed: {e}")
                # Continue without AI insights if it fails
                result.ai_pattern_analysis = None
        else:
            result.ai_pattern_analysis = None

        # Step 3: AI-influenced pricing recommendation
        low = result.annual_premium_low
        high = result.annual_premium_high
        base_recommendation = result.annual_premium_calculated
        ai_recommended = base_recommendation
        
        position = None
        if pattern_insight:
            suggested = getattr(pattern_insight, 'suggested_price_position', None)
            if suggested is not None:
                try:
                    position = max(0.0, min(1.0, float(suggested)))
                except (TypeError, ValueError):
                    position = None
            if position is None:
                rm = pattern_insight.risk_multiplier if pattern_insight.risk_multiplier is not None else 1.0
                if rm > 1.5:
                    position = 0.75
                elif rm > 1.2:
                    position = 0.65
                elif rm < 0.8:
                    position = 0.45
                else:
                    position = 0.6
        else:
            position = None
        
        if position is not None and high > low:
            ai_recommended = low + (high - low) * position
        
        result.annual_premium_recommended = round(ai_recommended, 2)
        
        # Refresh summary to reflect AI-influenced recommendation
        pricing_for_summary = {
            'low': low,
            'recommended': ai_recommended,
            'high': high
        }
        result.summary = engine._generate_summary(
            customer_dict,
            result.final_risk_score,
            result.scoring_steps,
            pricing_for_summary
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/score-batch")
async def score_batch(file: UploadFile = File(...)):
    """Score a batch of customers from CSV upload"""
    try:
        # Read CSV
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode('utf-8')))
        
        # Score each customer
        results = []
        for _, row in df.iterrows():
            customer_dict = row.to_dict()
            result = engine.score_customer(customer_dict)
            results.append(result.dict())
        
        return {
            "total_customers": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "historical_data_loaded": engine.historical_data is not None,
        "historical_records": len(engine.historical_data) if engine.historical_data is not None else 0,
        "ai_enabled": pattern_analyzer is not None,
        "ai_model": os.getenv('AI_MODEL', 'claude-sonnet-4-20250514') if pattern_analyzer else None
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
