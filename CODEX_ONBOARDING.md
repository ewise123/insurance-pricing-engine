# Codex Project Onboarding Prompt

Copy and paste this into Codex to get it up to speed on the Insurance Pricing Engine project:

---

## PROJECT CONTEXT

I have a complete AI-Augmented Dynamic Pricing Engine for Life Insurance that I need you to help me develop and enhance. This is a proof-of-concept system with a working backend, frontend, and synthetic data.

## PROJECT STRUCTURE

```
insurance-pricing-engine/
├── backend_api.py              # FastAPI server with risk scoring engine + AI integration
├── ai_pattern_analyzer.py      # Claude API integration for pattern discovery (NEW)
├── ai_cache.py                 # Caching layer to reduce API costs (NEW)
├── frontend.html               # React UI for underwriters
├── demo_script.py              # Command-line demo
├── data_generator.py           # Synthetic data generator
├── setup.py                    # Dependency checker
├── .env                        # Environment variables (API keys) - NOT in repo
├── .env.example                # Template for .env file
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies (includes anthropic SDK)
├── historical_customers.csv    # 10,000 training records
├── new_customers.csv           # 500 customers to score
└── [Documentation files]
```

## SYSTEM OVERVIEW

**Purpose:** Score life insurance applicants for risk and generate pricing recommendations in real-time with AI-powered pattern analysis.

**How It Works:**
1. Customer data comes in (CSV or API)
2. Backend analyzes 12 risk factors with weighted scoring
3. AI analyzes historical patterns to find complex correlations (NEW!)
4. Generates risk score (0-1), pricing boundaries, and detailed explanations
5. Frontend displays real-time scoring with AI insights
6. Underwriter can review and override decisions

**Key Innovation: AI Pattern Analysis**
The system now uses Claude API to discover multi-dimensional patterns in historical data that predict outcomes better than simple statistical lookups. For example, instead of just "57-year-old females average 0.398 risk", Claude might discover "Former smokers aged 55-60 with sedentary lifestyles and borderline cholesterol show 3x higher claim rates when combined with overweight BMI - a pattern occurring in 127 historical cases."

## CORE COMPONENTS

### 1. Backend (backend_api.py)
- **Framework:** FastAPI with CORS enabled
- **Main Class:** `RiskScoringEngine`
- **Key Method:** `score_customer(customer_dict)` → returns `PricingResult`
- **Risk Factors:** 12 weighted factors (Age 20%, Smoking 15%, BMI 15%, etc.)
- **Pricing Logic:** Age-based rates × risk multiplier × coverage amount
- **Historical Data:** Loads from `historical_customers.csv` for comparisons

**API Endpoints:**
- `POST /api/score-customer` - Score single customer
- `POST /api/score-batch` - Batch CSV upload
- `GET /api/health` - Health check

### 2. Frontend (frontend.html)
- **Framework:** React 18 (CDN, no build step)
- **Styling:** TailwindCSS (CDN)
- **Main Components:**
  - Customer list (left sidebar)
  - Real-time scoring display (animated)
  - Expandable factor cards (with explanations)
  - Pricing visualization (low/recommended/high)
  - Underwriter override interface

**Key Features:**
- Animated step-by-step scoring
- Click any factor to see detailed explanation
- Shows historical comparisons from data
- Price adjustment controls
- AI Pattern Analysis panel (when enabled)

### 3. AI Pattern Analyzer (ai_pattern_analyzer.py) **NEW**
- **Purpose:** Uses Claude API to discover complex multi-dimensional patterns in historical data
- **Main Class:** `PatternAnalyzer`
- **Key Method:** `analyze_customer_patterns(customer, risk_score, top_factors)` → returns `PatternInsight`
- **What it does:** Finds patterns like "Former smokers aged 55-60 with sedentary lifestyles and borderline cholesterol show 3x higher claim rates"
- **Caching:** Uses `AICache` to reduce API costs (similar profiles cached for 1 hour)

**Key Features:**
- Multi-dimensional cohort analysis (age + BMI + smoking + exercise combinations)
- Statistical significance assessment
- Structured output with confidence levels
- Graceful fallback if API fails

**Environment Variables Required:**
```
ANTHROPIC_API_KEY=sk-ant-...
ENABLE_AI_FEATURES=true
AI_MODEL=claude-sonnet-4-20250514
```

### 4. AI Cache (ai_cache.py) **NEW**
- **Purpose:** File-based cache to reduce Claude API costs
- **Main Class:** `AICache`
- **Storage:** `.ai_cache/` directory (gitignored)
- **TTL:** 1 hour default (configurable)
- **Cache Key:** Generated from bucketed customer attributes (age/5, bmi/3, smoking, etc.)
- **Expected Hit Rate:** 50-60% with proper bucketing

### 5. Data Structure

**Customer Schema (34 fields):**
```
Demographics: customer_id, age, gender, occupation, occupation_class
Health: height_inches, weight_lbs, bmi, blood_pressure_systolic, 
        blood_pressure_diastolic, total_cholesterol, hdl_cholesterol, 
        ldl_cholesterol, chronic_conditions, family_history
Lifestyle: smoking_status, alcohol_consumption, exercise_frequency, 
           dangerous_hobbies
Financial: annual_income, coverage_amount_requested, credit_score, 
           existing_coverage

[Historical only]:
risk_score_calculated, risk_score_assigned, annual_premium_low_boundary,
annual_premium_high_boundary, annual_premium_assigned, policy_accepted,
policy_active, claim_filed, claim_amount, underwriter_notes, policy_issue_date
```

## ARCHITECTURE PATTERNS

### Risk Scoring Flow
```python
For each risk factor:
  1. Extract value from customer data
  2. Calculate base_risk (0-1 scale)
  3. Apply weight (factor importance)
  4. weighted_score = base_risk × weight
  5. Generate natural language explanation
  6. Find historical cohort for comparison
  7. Extract supporting_data (cohort_size, avg_risk, etc.)

Final risk score = sum(all weighted_scores)
```

### Pricing Calculation
```python
# Age-based rate per $1000 coverage
base_rate = get_rate_by_age(age)  # e.g., 1.50 for age 45

# Risk multiplier (higher risk = higher cost)
risk_multiplier = 0.5 + (risk_score × 3)

# Calculate premium
coverage_thousands = coverage / 1000
base_premium = base_rate × coverage_thousands × risk_multiplier

# Boundaries
low_boundary = base_premium × 0.85   # Break-even
high_boundary = base_premium × 1.25  # Competitive max
recommended = smart_position_based_on_risk_tier()
```

## IMPORTANT IMPLEMENTATION DETAILS

### 1. Frontend-Backend Communication
- Frontend runs on `file://` protocol (local HTML)
- Backend runs on `http://localhost:8000`
- CORS must be enabled (already configured)
- Frontend uses `fetch()` API for requests

### 2. Data Type Handling
- CSV fields may have NaN values → convert to string and handle 'nan'
- Numbers from CSV are strings → parse with `parseFloat()` or `parseInt()`
- Example fix pattern:
  ```python
  conditions = str(customer['chronic_conditions']) if customer['chronic_conditions'] else 'None'
  if conditions == 'None' or conditions == 'nan':
      conditions = 'None'
  ```

### 3. Historical Data Usage
- Loaded once on engine initialization
- Used for cohort comparisons in explanations
- Filter by relevant attributes (age ±5 years, same occupation class, etc.)
- Always check if data exists before using

### 4. Explanation Generation
- Must be detailed but readable
- Include specific numbers (cohort sizes, percentages)
- Reference actuarial reasoning
- Format: "Customer age of 57.4 places them in the 50-59 bracket. Mortality risk increases with age..."

## COMMON TASKS YOU MIGHT HELP WITH

### Adding New Risk Factors
1. Add to risk factor list (update weights to sum to 100%)
2. Create `_score_[factor_name]()` method
3. Add to `score_customer()` pipeline
4. Update customer schema if new field needed
5. Modify data generator to include new field

### Modifying Pricing Logic
1. Update `_calculate_pricing()` method
2. Adjust base rates, multipliers, or boundaries
3. Update explanation in summary generation
4. Test with sample customers

### UI Enhancements
1. All UI code is in single `frontend.html` file
2. React components are in `<script type="text/babel">`
3. Use Tailwind utility classes for styling
4. State management with React hooks (useState, useEffect)

### Data Generation Changes
1. Modify `data_generator.py`
2. Update correlation logic in `generate_customer()`
3. Adjust risk scoring in `_calculate_risk_score()`
4. Regenerate: `python data_generator.py`

## TESTING THE SYSTEM

### Quick Test
```bash
# Terminal 1: Start backend
python backend_api.py
# Wait for: "Uvicorn running on http://0.0.0.0:8000"

# Terminal 2: Test API
curl http://localhost:8000/api/health

# Browser: Open frontend.html
# Should see: "System Online | 10,000 historical records loaded"
```

### Test Scoring
```bash
python demo_script.py
# Should output complete risk assessment for one customer
```

## CURRENT STATE

✅ **Working:**
- Complete risk scoring engine (12 factors)
- FastAPI backend with all endpoints
- React frontend with real-time display
- 10,000 historical records
- 500 new customer records
- Detailed explanations with historical data
- Price calculation with boundaries

❌ **Not Yet Implemented:**
- Authentication/authorization
- Database persistence (currently file-based)
- Batch processing UI (only single customer in UI)
- PDF report generation
- Real actuarial table integration
- Regulatory compliance checks
- Production deployment configuration

## KEY FILES TO UNDERSTAND

**Priority 1 (Core Logic):**
1. `backend_api.py` lines 1-150 → API structure and engine initialization
2. `backend_api.py` lines 150-700 → Individual risk factor scoring methods
3. `backend_api.py` lines 700-850 → Pricing and summary generation

**Priority 2 (UI):**
1. `frontend.html` lines 1-50 → Structure and setup
2. `frontend.html` lines 50-150 → Main App component and state
3. `frontend.html` lines 200-400 → Scoring display components

**Priority 3 (Data):**
1. `data_generator.py` lines 1-200 → Customer generation with correlations
2. `data_generator.py` lines 200-400 → Risk scoring logic
3. `data_generator.py` lines 400-500 → Historical outcomes

## DEVELOPMENT GUIDELINES

### Code Style
- Python: PEP 8, type hints where helpful
- React: Functional components with hooks
- Comments: Explain WHY, not WHAT
- Variables: Descriptive names (avoid abbreviations)

### Error Handling
- Always wrap API calls in try-catch
- Validate all inputs (especially from CSV)
- Provide helpful error messages
- Log errors for debugging

### Performance
- Current target: <100ms per customer
- Historical data loaded once (not per request)
- Use pandas efficiently (no row-by-row iteration)
- Frontend updates should be smooth (use transitions)

## COMMON ISSUES & SOLUTIONS

**Issue:** Frontend can't connect to backend
- **Solution:** Check CORS is enabled, backend is running on port 8000

**Issue:** NaN values breaking scoring
- **Solution:** Convert to string and check for 'nan' explicitly

**Issue:** Historical data comparisons return empty
- **Solution:** Widen cohort filters (e.g., age ±10 instead of ±5)

**Issue:** Pricing seems unrealistic
- **Solution:** Check base rates and multiplier logic in `_calculate_pricing()`

## WHEN MAKING CHANGES

1. **Test incrementally** - Don't change multiple components at once
2. **Update both ends** - If you change API response, update frontend
3. **Validate data** - Always check CSV changes don't break parsing
4. **Document** - Update README if adding major features
5. **Test edge cases** - Very young (18), very old (75+), high risk (0.8+)

## MY TYPICAL REQUESTS

You'll likely help me with:
- "Add a new risk factor for [X]"
- "Change the pricing to use [different logic]"
- "Make the UI show [additional information]"
- "Fix bug where [description]"
- "Optimize performance for [scenario]"
- "Add validation for [input]"
- "Generate more realistic [data attribute]"

## QUICK REFERENCE

**Start Backend:** `python backend_api.py`
**Run Demo:** `python demo_script.py`
**Check Setup:** `python setup.py`
**Regenerate Data:** `python data_generator.py`

**Main Classes:**
- `RiskScoringEngine` - Core scoring logic
- `PricingResult` - Output model
- `ScoringStep` - Individual factor result

**Key Methods:**
- `score_customer()` - Main scoring pipeline
- `_score_[factor]()` - Individual factor scoring
- `_calculate_pricing()` - Price calculation
- `_generate_summary()` - Executive summary

## WHAT I NEED FROM YOU

When I ask you to make changes:
1. **Understand the full context** - Read related code first
2. **Consider both ends** - Backend AND frontend implications
3. **Maintain consistency** - Follow existing patterns
4. **Test your changes** - Suggest how I can verify it works
5. **Explain tradeoffs** - If there are multiple approaches, tell me pros/cons

Now, I'm ready to start developing. What would you like to work on?

---

## ADDITIONAL CONTEXT (If Needed)

### Business Context
This is a POC to demonstrate to insurance companies that AI can reduce underwriting time from weeks to seconds while maintaining accuracy and explainability.

### Target Users
Primary: Insurance underwriters reviewing AI recommendations
Secondary: Executives evaluating the system's capabilities

### Success Criteria
- ✅ Scores customer in <1 second
- ✅ Every decision fully explainable
- ✅ Professional UI that looks production-ready
- ✅ Accurate pricing based on risk

---

Save this prompt and paste it into Codex when starting a session. It gives Codex everything it needs to understand the architecture, make changes correctly, and maintain consistency with your existing code.
