"""
AI Pattern Analyzer - Uses Claude to find complex patterns in historical data
"""

from anthropic import Anthropic
import pandas as pd
import json
import hashlib
from typing import Dict, List, Optional
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class PatternInsight:
    """Structured pattern analysis result"""
    pattern_description: str
    cohort_size: int
    claim_rate: float
    baseline_claim_rate: float
    risk_multiplier: float
    confidence: str  # "high", "medium", "low"
    key_factors: List[str]
    recommendation: str
    statistical_significance: str
    suggested_price_position: float  # 0.0 = low boundary, 1.0 = high boundary
    key_factors_with_sentiment: Optional[List[Dict[str, str]]] = None


class PatternAnalyzer:
    """
    Analyzes historical data to find complex multi-dimensional patterns
    that predict outcomes better than simple cohort analysis
    """
    
    def __init__(self, historical_data: pd.DataFrame, cache: Optional['AICache'] = None):
        self.historical_data = historical_data
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.cache = cache
        self.model = os.getenv('AI_MODEL', 'claude-sonnet-4-20250514')
        
        # Pre-compute baseline statistics for context
        self.baseline_stats = self._compute_baseline_stats()
    
    def _compute_baseline_stats(self) -> Dict:
        """Compute baseline statistics for comparison"""
        return {
            'total_customers': len(self.historical_data),
            'overall_claim_rate': self.historical_data['claim_filed'].mean(),
            'avg_risk_score': self.historical_data['risk_score_assigned'].mean(),
            'avg_premium': self.historical_data['annual_premium_assigned'].mean(),
            'acceptance_rate': self.historical_data['policy_accepted'].mean(),
            'active_rate': self.historical_data['policy_active'].mean()
        }
    
    def analyze_customer_patterns(
        self, 
        customer: Dict, 
        risk_score: float,
        top_risk_factors: List[Dict]
    ) -> PatternInsight:
        """
        Main entry point: Analyze historical patterns for this customer
        
        Args:
            customer: Customer profile dict
            risk_score: Calculated risk score
            top_risk_factors: Top 3-5 contributing factors
            
        Returns:
            PatternInsight with AI-discovered patterns
        """
        
        # Generate cache key from customer profile
        cache_key = self._generate_cache_key(customer, risk_score)
        
        # Check cache first
        if self.cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return cached_result
        
        # Find similar customers (broad net initially)
        similar_cohort = self._find_similar_cohort(customer)
        
        # Prepare data for Claude
        analysis_context = self._prepare_analysis_context(
            customer, 
            risk_score, 
            top_risk_factors,
            similar_cohort
        )
        
        # Call Claude for pattern analysis
        pattern_insight = self._call_claude_for_patterns(analysis_context)
        
        # Cache result
        if self.cache:
            self.cache.set(cache_key, pattern_insight, ttl=3600)  # 1 hour
        
        return pattern_insight
    
    def _suggest_price_position_from_multiplier(self, risk_multiplier: float) -> float:
        """Map risk multiplier to a price position between low (0) and high (1)."""
        if risk_multiplier is None:
            return 0.6
        if risk_multiplier > 1.5:
            return 0.75
        if risk_multiplier < 0.9:
            return 0.45
        return 0.6
    
    def _find_similar_cohort(self, customer: Dict) -> pd.DataFrame:
        """
        Find broadly similar customers using multiple dimensions
        Not just age - consider multiple factors
        """
        df = self.historical_data.copy()
        
        # Multi-dimensional similarity
        # Age band (±10 years)
        age = customer['age']
        df = df[(df['age'] >= age - 10) & (df['age'] <= age + 10)]
        
        # Same gender
        df = df[df['gender'] == customer['gender']]
        
        # Similar BMI category
        bmi = customer['bmi']
        if bmi < 25:
            df = df[df['bmi'] < 27]  # Normal to slightly overweight
        elif bmi < 30:
            df = df[(df['bmi'] >= 23) & (df['bmi'] < 32)]  # Overweight band
        else:
            df = df[df['bmi'] >= 28]  # Obese band
        
        # Smoking status (exact match is important)
        df = df[df['smoking_status'] == customer['smoking_status']]
        
        # If cohort too small, relax constraints
        if len(df) < 50:
            df = self.historical_data.copy()
            df = df[(df['age'] >= age - 15) & (df['age'] <= age + 15)]
            df = df[df['gender'] == customer['gender']]
        
        return df
    
    def _prepare_analysis_context(
        self,
        customer: Dict,
        risk_score: float,
        top_risk_factors: List[Dict],
        similar_cohort: pd.DataFrame
    ) -> Dict:
        """
        Prepare rich context for Claude analysis
        """
        
        # Customer profile (key attributes only)
        customer_profile = {
            'customer_id': customer['customer_id'],
            'age': customer['age'],
            'gender': customer['gender'],
            'occupation': customer['occupation'],
            'occupation_class': customer['occupation_class'],
            'bmi': customer['bmi'],
            'smoking_status': customer['smoking_status'],
            'blood_pressure': f"{customer['blood_pressure_systolic']}/{customer['blood_pressure_diastolic']}",
            'cholesterol': customer['total_cholesterol'],
            'chronic_conditions': customer['chronic_conditions'],
            'exercise_frequency': customer['exercise_frequency'],
            'alcohol_consumption': customer['alcohol_consumption'],
            'dangerous_hobbies': customer['dangerous_hobbies'],
            'family_history': customer['family_history'],
            'coverage_requested': customer['coverage_amount_requested'],
            'calculated_risk_score': risk_score
        }
        
        # Cohort statistics
        cohort_stats = {
            'cohort_size': len(similar_cohort),
            'avg_risk_score': similar_cohort['risk_score_assigned'].mean(),
            'claim_rate': similar_cohort['claim_filed'].mean(),
            'claims_count': similar_cohort['claim_filed'].sum(),
            'avg_premium': similar_cohort['annual_premium_assigned'].mean(),
            'acceptance_rate': similar_cohort['policy_accepted'].mean(),
            'active_rate': similar_cohort['policy_active'].mean()
        }
        
        # Find interesting sub-patterns in cohort
        sub_patterns = self._find_sub_patterns(similar_cohort, customer)
        
        # Top risk factors formatted
        risk_factors_summary = [
            {
                'factor': f['factor'],
                'value': f['value'],
                'contribution': f['weighted_score']
            }
            for f in top_risk_factors
        ]
        
        return {
            'customer_profile': customer_profile,
            'baseline_stats': self.baseline_stats,
            'cohort_stats': cohort_stats,
            'sub_patterns': sub_patterns,
            'top_risk_factors': risk_factors_summary,
            'total_historical_records': len(self.historical_data)
        }
    
    def _find_sub_patterns(self, cohort: pd.DataFrame, customer: Dict) -> List[Dict]:
        """
        Pre-compute some interesting sub-patterns for Claude to analyze
        """
        patterns = []
        
        # Pattern 1: Same smoking + BMI category
        smoking_bmi = cohort[
            (cohort['smoking_status'] == customer['smoking_status']) &
            (abs(cohort['bmi'] - customer['bmi']) < 3)
        ]
        if len(smoking_bmi) > 10:
            patterns.append({
                'description': f"Similar smoking status + BMI range",
                'size': len(smoking_bmi),
                'claim_rate': smoking_bmi['claim_filed'].mean(),
                'avg_risk': smoking_bmi['risk_score_assigned'].mean()
            })
        
        # Pattern 2: Same occupation class + chronic conditions
        occ_chronic = cohort[
            (cohort['occupation_class'] == customer['occupation_class']) &
            (cohort['chronic_conditions'] == customer['chronic_conditions'])
        ]
        if len(occ_chronic) > 10:
            patterns.append({
                'description': f"Same occupation class + chronic condition status",
                'size': len(occ_chronic),
                'claim_rate': occ_chronic['claim_filed'].mean(),
                'avg_risk': occ_chronic['risk_score_assigned'].mean()
            })
        
        # Pattern 3: Exercise + BMI combination
        exercise_bmi = cohort[
            (cohort['exercise_frequency'] == customer['exercise_frequency']) &
            (abs(cohort['bmi'] - customer['bmi']) < 5)
        ]
        if len(exercise_bmi) > 10:
            patterns.append({
                'description': f"Similar exercise level + BMI",
                'size': len(exercise_bmi),
                'claim_rate': exercise_bmi['claim_filed'].mean(),
                'avg_risk': exercise_bmi['risk_score_assigned'].mean()
            })
        
        # Pattern 4: Age + smoking + cholesterol (triple combination)
        age = customer['age']
        triple = cohort[
            (abs(cohort['age'] - age) < 5) &
            (cohort['smoking_status'] == customer['smoking_status']) &
            (abs(cohort['total_cholesterol'] - customer['total_cholesterol']) < 30)
        ]
        if len(triple) > 10:
            patterns.append({
                'description': f"Age + smoking + cholesterol triple match",
                'size': len(triple),
                'claim_rate': triple['claim_filed'].mean(),
                'avg_risk': triple['risk_score_assigned'].mean()
            })
        
        return patterns
    
    def _call_claude_for_patterns(self, context: Dict) -> PatternInsight:
        """
        Call Claude API to analyze patterns
        """
        
        # Build prompt
        prompt = self._build_prompt(context)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,  # Lower temperature for analytical tasks
                system="""You are an expert actuarial analyst specializing in life insurance risk assessment. 
Your role is to analyze historical data patterns and identify complex multi-dimensional relationships 
that predict claim rates and risk outcomes. You provide specific, data-driven insights with statistical 
rigor. Always cite exact numbers from the data provided.""",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse Claude's response
            analysis_text = response.content[0].text
            
            # Extract structured data from response
            pattern_insight = self._parse_claude_response(analysis_text, context)
            
            return pattern_insight
            
        except Exception as e:
            print(f"Claude API error: {e}")
            # Fallback to basic pattern if AI fails
            return self._fallback_pattern(context)
    
    def _build_prompt(self, context: Dict) -> str:
        """
        Build the prompt for Claude with all context
        """
        
        customer = context['customer_profile']
        cohort = context['cohort_stats']
        baseline = context['baseline_stats']
        sub_patterns = context['sub_patterns']
        
        prompt = f"""Analyze this life insurance applicant's profile against historical data to identify predictive patterns.

APPLICANT PROFILE:
- ID: {customer['customer_id']}
- Age: {customer['age']} | Gender: {customer['gender']}
- Occupation: {customer['occupation']} ({customer['occupation_class']})
- BMI: {customer['bmi']} | Smoking: {customer['smoking_status']}
- Blood Pressure: {customer['blood_pressure']} | Cholesterol: {customer['cholesterol']}
- Chronic Conditions: {customer['chronic_conditions']}
- Exercise: {customer['exercise_frequency']} | Alcohol: {customer['alcohol_consumption']}
- Dangerous Hobbies: {customer['dangerous_hobbies']}
- Family History: {customer['family_history']}
- Coverage Requested: ${customer['coverage_requested']:,}
- Calculated Risk Score: {customer['calculated_risk_score']:.2f}

HISTORICAL DATA CONTEXT:
Total Historical Records: {context['total_historical_records']:,}
Overall Baseline Claim Rate: {baseline['overall_claim_rate']*100:.2f}%

SIMILAR COHORT ANALYSIS:
Cohort Size: {cohort['cohort_size']} customers
Cohort Claim Rate: {cohort['claim_rate']*100:.2f}%
Actual Claims Filed: {cohort['claims_count']}
Average Risk Score: {cohort['avg_risk_score']:.2f}
Average Premium: ${cohort['avg_premium']:,.2f}

SUB-PATTERN FINDINGS:
"""
        
        for i, pattern in enumerate(sub_patterns, 1):
            prompt += f"""
{i}. {pattern['description']}
   - Sample Size: {pattern['size']} customers
   - Claim Rate: {pattern['claim_rate']*100:.2f}%
   - Average Risk: {pattern['avg_risk']:.2f}
"""
        
        prompt += f"""

YOUR TASK:
1. Identify the MOST PREDICTIVE multi-dimensional pattern from the data
2. Calculate how this pattern's claim rate compares to baseline
3. Determine if this customer matches any HIGH-RISK or LOW-RISK pattern combinations
4. Assess statistical significance (is sample size large enough to be meaningful?)
5. Provide a specific, actionable recommendation
6. For each key factor, label it as positive (protective), negative (risk), or neutral (mixed/unclear)

OUTPUT FORMAT (be specific with numbers):
{{
  "pattern_description": "Concise description of the key pattern you identified",
  "cohort_size": number of customers matching this exact pattern,
  "claim_rate": claim rate for this specific pattern (as decimal, e.g., 0.063),
  "risk_multiplier": how much higher/lower than baseline (e.g., 1.34 means 34% higher),
  "confidence": "high" | "medium" | "low" (based on sample size and consistency),
  "key_factors": ["factor 1", "factor 2", "factor 3"] (the 2-4 factors driving this pattern),
  "key_factors_with_sentiment": [
    {{"text": "factor 1", "sentiment": "positive|negative|neutral"}},
    {{"text": "factor 2", "sentiment": "positive|negative|neutral"}}
  ],
  "recommendation": "Specific action for underwriter",
  "statistical_significance": "Explanation of whether sample size is adequate and if pattern is reliable",
  "suggested_price_position": decimal between 0.0 and 1.0 indicating where to place price within low/high range (0 = low boundary, 0.5 = middle, 1 = high boundary)
}}

IMPORTANT:
- Focus on COMPOUND factors (combinations matter more than individual factors)
- Be specific with numbers from the data provided
- If sample size is <30, note low confidence
- Compare to baseline ({baseline['overall_claim_rate']*100:.2f}%) explicitly
- Explain WHY this pattern matters for risk assessment
- For suggested_price_position: if risk_multiplier > 1.5 suggest 0.7-0.8, if < 0.9 suggest 0.4-0.5, otherwise around 0.6
- For key_factors_with_sentiment: mark clearly risky/worsening factors as "negative" and clearly protective/mitigating factors as "positive"
"""
        
        return prompt
    
    def _parse_claude_response(self, response_text: str, context: Dict) -> PatternInsight:
        """
        Parse Claude's response into structured PatternInsight
        """
        
        try:
            # Try to extract JSON from response
            # Claude might wrap it in markdown code blocks
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)
                
                # Calculate baseline for comparison
                baseline_claim_rate = context['baseline_stats']['overall_claim_rate']
                suggested_pos = data.get('suggested_price_position')
                if suggested_pos is None:
                    suggested_pos = self._suggest_price_position_from_multiplier(data.get('risk_multiplier', 1.0))
                
                key_factors_with_sentiment = data.get('key_factors_with_sentiment')
                if not key_factors_with_sentiment and data.get('key_factors'):
                    key_factors_with_sentiment = [
                        {"text": f, "sentiment": self._classify_factor(f)}
                        for f in data['key_factors']
                    ]
                
                return PatternInsight(
                    pattern_description=data.get('pattern_description', ''),
                    cohort_size=data.get('cohort_size', 0),
                    claim_rate=data.get('claim_rate', 0.0),
                    baseline_claim_rate=baseline_claim_rate,
                    risk_multiplier=data.get('risk_multiplier', 1.0),
                    confidence=data.get('confidence', 'medium'),
                    key_factors=data.get('key_factors', []),
                    recommendation=data.get('recommendation', ''),
                    statistical_significance=data.get('statistical_significance', ''),
                    suggested_price_position=suggested_pos,
                    key_factors_with_sentiment=key_factors_with_sentiment
                )
            else:
                # If no JSON found, use fallback
                return self._fallback_pattern(context)
                
        except Exception as e:
            print(f"Error parsing Claude response: {e}")
            return self._fallback_pattern(context)
    
    def _fallback_pattern(self, context: Dict) -> PatternInsight:
        """
        Return basic pattern analysis if AI fails
        """
        baseline_claim_rate = context['baseline_stats']['overall_claim_rate']
        cohort_claim_rate = context['cohort_stats']['claim_rate']
        cohort_size = context['cohort_stats']['cohort_size']
        
        risk_multiplier = cohort_claim_rate / baseline_claim_rate if baseline_claim_rate > 0 else 1.0
        
        return PatternInsight(
            pattern_description=f"Similar demographic and health profile customers",
            cohort_size=cohort_size,
            claim_rate=cohort_claim_rate,
            baseline_claim_rate=baseline_claim_rate,
            risk_multiplier=risk_multiplier,
            confidence="medium" if cohort_size > 100 else "low",
            key_factors=["Age", "Gender", "BMI", "Smoking Status"],
            recommendation="Standard underwriting procedures apply",
            statistical_significance=f"Based on {cohort_size} similar customers in historical data",
            suggested_price_position=self._suggest_price_position_from_multiplier(risk_multiplier),
            key_factors_with_sentiment=None
        )
    
    def _generate_cache_key(self, customer: Dict, risk_score: float) -> str:
        """
        Generate cache key from customer profile
        Round/bucket values to increase cache hits
        """
        # Create signature from key attributes
        signature = {
            'age_bucket': int(customer['age'] / 5) * 5,  # 5-year buckets
            'gender': customer['gender'],
            'bmi_bucket': int(customer['bmi'] / 3) * 3,  # 3-point BMI buckets
            'smoking': customer['smoking_status'],
            'occupation_class': customer['occupation_class'],
            'risk_bucket': round(risk_score, 1)  # 0.1 precision
        }
        
        sig_str = json.dumps(signature, sort_keys=True)
        return hashlib.md5(sig_str.encode()).hexdigest()


def format_pattern_for_display(insight: PatternInsight) -> Dict:
    """
    Format PatternInsight for frontend display
    """
    def classify_factor(text: str) -> str:
        """Heuristic sentiment for factor text."""
        t = text.lower()
        positives = [
            "protective", "reduces", "lower", "favorable", "preferred",
            "active", "fit", "good", "strong", "improves", "healthy", "exercise",
            "high hdl", "good hdl", "improved", "benefit", "fitter"
        ]
        negatives = [
            "risk", "high", "elevated", "smoker", "smoking", "obese",
            "overweight", "dangerous", "chronic", "poor", "unfavorable",
            "heavy", "claims", "adverse", "hypertension", "cardiovascular",
            "metabolic", "sedentary", "obesity", "diabetes"
        ]
        if any(word in t for word in positives):
            return "positive"
        if any(word in t for word in negatives):
            return "negative"
        return "neutral"
    
    if insight.key_factors_with_sentiment:
        key_factors_detailed = insight.key_factors_with_sentiment
    else:
        key_factors_detailed = [
            {"text": f, "sentiment": classify_factor(f)}
            for f in insight.key_factors
        ]
    
    claims_count = int(round(insight.claim_rate * insight.cohort_size)) if insight.cohort_size else 0
    if insight.baseline_claim_rate > 0:
        vs_baseline_value = insight.claim_rate / insight.baseline_claim_rate
        vs_baseline_display = f"{vs_baseline_value:.2f}x"
    else:
        vs_baseline_value = None
        vs_baseline_display = "N/A"
    
    return {
        'title': 'AI Pattern Analysis',
        'pattern': insight.pattern_description,
        'metrics': {
            'cohort_size': insight.cohort_size,
            'cohort_claims_count': claims_count,
            'claim_rate_percentage': round(insight.claim_rate * 100, 2),
            'baseline_percentage': round(insight.baseline_claim_rate * 100, 2),
            'vs_baseline_multiplier': vs_baseline_display,
            'vs_baseline_multiplier_value': vs_baseline_value
        },
        'confidence': insight.confidence,
        'key_factors': insight.key_factors,
        'key_factors_detailed': key_factors_detailed,
        'recommendation': insight.recommendation,
        'statistical_note': insight.statistical_significance,
        'ai_generated': True,
        'suggested_price_position': insight.suggested_price_position
    }
