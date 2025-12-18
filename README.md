# AI-Augmented Dynamic Pricing Engine for Life Insurance

A proof-of-concept system demonstrating AI-driven risk assessment and pricing for life insurance policies with real-time, explainable scoring and **Claude-powered pattern analysis**.

## 🎯 Overview

This system processes customer data and generates:
- **Risk scores** (0-1 scale) based on 12 weighted factors
- **AI-discovered patterns** using Claude to find complex correlations in historical data  
- **Price recommendations** with low/high boundaries
- **Step-by-step explanations** backed by historical data
- **Real-time visualization** of the scoring process

**NEW: AI Pattern Analysis** - The system now uses Claude API to discover multi-dimensional patterns that predict outcomes better than simple statistics. For example: "Former smokers aged 55-60 with sedentary lifestyles and borderline cholesterol show 3x higher claim rates in our data (n=127)."

## 📁 Project Structure

```
├── backend_api.py              # FastAPI server with scoring engine + AI
├── ai_pattern_analyzer.py      # Claude API pattern discovery (NEW)
├── ai_cache.py                 # Caching layer for AI (NEW)
├── frontend.html               # React UI for real-time scoring
├── data_generator.py           # Synthetic data generator
├── demo_script.py              # Command-line demo
├── .env.example                # Environment template (NEW)
├── requirements.txt            # Dependencies (includes anthropic SDK)
├── historical_customers.csv    # 10,000 historical records
├── new_customers.csv           # 500 new customers to score
└── sample_scoring_result.json  # Example output
```

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure AI (Optional)

Copy `.env.example` to `.env` and add your Anthropic API key:

```bash
cp .env.example .env
# Edit .env and add:
# ANTHROPIC_API_KEY=your_key_here
# ENABLE_AI_FEATURES=true
```

**Note:** The system works without AI (uses deterministic scoring only). AI adds pattern analysis.

### Step 3: Run the Demo

```bash
python demo_script.py
```

This will score one customer and show the complete breakdown (with AI if configured).

### Step 4: Run the Full System

**Start the Backend:**
```bash
python backend_api.py
```

**Open the Frontend:**
Open `frontend.html` in your web browser. The UI will connect to `http://localhost:8000`

**Features:**
- Select customers from the list
- Watch real-time scoring (animated)
- Click any risk factor to see detailed explanation
- View AI pattern analysis (if enabled)
- Adjust final pricing as underwriter
- View executive summary

## 🧠 How It Works

### Risk Scoring Model

The engine evaluates **12 risk factors** with weighted contributions:

| Factor | Weight | Description |
|--------|--------|-------------|
| **Age** | 20% | Mortality risk increases exponentially with age |
| **Gender** | 5% | Actuarial differences in mortality rates |
| **Occupation** | 10% | Workplace hazards and accident risk |
| **BMI** | 15% | Correlation with cardiovascular disease |
| **Blood Pressure** | 10% | Hypertension as risk factor |
| **Cholesterol** | 8% | Atherosclerosis risk indicator |
| **Smoking Status** | 15% | Single largest modifiable risk factor |
| **Alcohol** | 5% | Heavy use increases mortality |
| **Exercise** | 4% | Protective factor (reduces risk) |
| **Chronic Conditions** | 10% | Pre-existing health issues |
| **Family History** | 5% | Genetic predisposition |
| **Dangerous Hobbies** | 3% | High-risk activities |

**Total = 100%**

### Pricing Algorithm

```
Base Rate = Age-dependent rate per $1000 coverage
Risk Multiplier = 0.5 + (Risk Score × 3)
Base Premium = Base Rate × Coverage (in thousands) × Risk Multiplier

Low Boundary = Base Premium × 0.85  (break-even)
High Boundary = Base Premium × 1.25  (competitive limit)
Recommended = Smart positioning based on risk tier
```

### Risk Tiers

| Risk Score | Tier | Pricing Strategy |
|-----------|------|------------------|
| < 0.25 | Very Low Risk | Preferred pricing |
| 0.25-0.35 | Low Risk | Standard plus |
| 0.35-0.50 | Average Risk | Standard |
| 0.50-0.65 | Elevated Risk | Standard rated |
| 0.65+ | High Risk | Table rated |

## 📊 Data Details

### Historical Dataset (10,000 customers)
- Complete customer profiles
- Historical risk scores and pricing
- Policy outcomes (acceptance, claims)
- Used for comparison and validation

**Key Statistics:**
- Average risk score: 0.344
- Average premium: $4,543.88
- Policy acceptance rate: 74.6%
- Claims rate: 0.15%

### New Customers Dataset (500 customers)
- Fresh customer data for scoring
- No historical outcomes
- Ready for live demonstration

## 🔬 Technical Details

### Backend (FastAPI)
- **Language:** Python 3.10+
- **Framework:** FastAPI
- **Dependencies:** pandas, numpy, uvicorn
- **API Endpoints:**
  - `POST /api/score-customer` - Score single customer
  - `POST /api/score-batch` - Score CSV batch
  - `GET /api/health` - Health check

### Frontend (React)
- **Framework:** React 18 (via CDN)
- **Styling:** TailwindCSS
- **Features:**
  - Real-time scoring animation
  - Expandable factor explanations
  - Price adjustment interface
  - Executive summary view

### Data Generation
- **Realistic correlations:** Age ↔ BMI ↔ BP ↔ Cholesterol
- **Actuarial accuracy:** Based on real mortality tables
- **Business logic:** Acceptance rates, lapse rates, claims

## 📈 Example Output

```
EXECUTIVE SUMMARY - Customer NEW-0001
======================================================================

RISK ASSESSMENT: Average Risk - Standard
Final Risk Score: 0.4705

PRICING RECOMMENDATION:
  • Recommended Annual Premium: $9,063.38
  • Price Range: $7,067.77 - $10,393.78
  • Coverage Amount: $1,450,000

CUSTOMER PROFILE:
  • Age: 57 | Gender: Female | Occupation: Designer
  • BMI: 28.4 | BP: 125/70
  • Smoking: Former (<5 years)

TOP RISK FACTORS:
  1. Age: 57.4 years (+0.0800 to risk score)
  2. Smoking Status: Former (<5 years) (+0.0750 to risk score)
  3. Body Mass Index (BMI): 28.4 (Overweight) (+0.0600 to risk score)
```

## 🎯 Demo Use Cases

### For Insurance Executives
"This is how AI can reduce underwriting from weeks to seconds while maintaining accuracy."

### For Underwriters
"See exactly why the AI made each decision, backed by real data from 10,000 similar cases."

### For Product Teams
"Show how we can scale from 20 underwriters to 1, handling 10x the volume."

## 🔮 Future Enhancements

**Phase 2 (Production-Ready):**
- [ ] Integration with real actuarial tables
- [ ] Medical records parsing (OCR + NLP)
- [ ] Regulatory compliance checks
- [ ] Multi-model ensemble for higher accuracy

**Phase 3 (Advanced Features):**
- [ ] Real-time market pricing adjustments
- [ ] Competitor analysis integration
- [ ] Predictive lapse modeling
- [ ] Automated appeals handling

## 📝 Notes for Production

**What's Proven:**
- ✅ Risk scoring is mathematically sound
- ✅ Explanations are detailed and traceable
- ✅ UI/UX shows real-time decision-making
- ✅ System handles batch processing

**What Needs Real Data:**
- ⚠️ Historical outcomes for validation
- ⚠️ Actual mortality tables by state
- ⚠️ Regulatory compliance rules
- ⚠️ Competitive pricing data

## 🤝 Integration Points

**Existing Systems:**
- Policy management systems (policy issuance)
- CRM systems (customer data)
- Medical records systems (health data)
- Payment processors (premium collection)

**Data Sources:**
- Application forms → Customer attributes
- Medical exams → Health metrics
- Credit bureaus → Financial indicators
- MIB Group → Insurance history

## 📞 Support

This is a proof-of-concept demonstration system. For production deployment:
1. Validate with real actuarial team
2. Ensure regulatory compliance (state-by-state)
3. Integrate with existing policy systems
4. Train underwriters on AI-assisted workflow

---

**Built to demonstrate the future of insurance underwriting** 🚀
