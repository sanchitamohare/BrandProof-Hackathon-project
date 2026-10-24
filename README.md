# BrandProof — AI-Powered Brand Governance Platform

> **"Trust Every Brand Claim."**

**BrandProof** is a professional, production-style brand governance and claim verification platform designed for enterprise marketing, legal, and compliance teams. 

Marketing teams often publish high-velocity campaigns across ads, emails, landing pages, and social channels without adequate legal scrutiny. BrandProof bridges the gap by automatically analyzing content against brand guidelines, detecting prohibited or hyperbolic language, cross-referencing quantitative claims against verifiable evidence records in the **Claim Passport**, generating actionable corrections, and routing assets through a human review and approval pipeline.

---

## 🌟 Key Highlights for Hackathon Judges

- **100% Functional & Self-Contained:** Every button, tab, form, audit log, and chart is functional and backed by persistent SQLite storage.
- **Judge-Ready Walkthrough:** Built-in **Help and Demo Guide** with a 12-step guided workflow and pre-loaded demonstration datasets.
- **Transparent, Deterministic Core:** Uses explainable, rule-based algorithms as the reliable default. External AI (OpenAI API) is strictly opt-in and transparently labeled.
- **Calm, Modern SaaS UI:** Minimalist, trustworthy color palette (navy, slate, soft blue, warm amber, emerald green) designed for executive presentations.
- **End-to-End Workflow:** Content submission ➔ automated governance check ➔ interactive correction editor ➔ approval review ➔ Claim Passport evidence linkage ➔ printable audit report export.

---

## 🛠 Technology Stack

- **Frontend & UI:** Streamlit with custom SaaS CSS theme (`assets/style.css`).
- **Backend Logic:** Python 3.10+ / Python 3.13.
- **Data Persistence:** SQLite (`brandproof.db`) with full transactional integrity, audit logging, and foreign key cascades.
- **Data Analysis & Charts:** pandas, Plotly Express.
- **Optional AI Integration:** Modular OpenAI-compatible connector with rule-based fallback.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10 or higher.
- `pip` package manager.

### 2. Installation
Open a terminal in the `brandproof` directory and install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Launching BrandProof
Run the Streamlit application:

```bash
streamlit run app.py
```

The application will open automatically in your browser at `http://localhost:8501`.

*(On Windows, you can also double-click `START_BRANDPROOF.bat` from the root folder).*

---

## 📋 12-Step Demo Workflow for Judges

1. **Dashboard Overview:** Open the platform and inspect real-time workspace KPIs: Total Content Checks, Flagged Claims, Pending Reviews, and Approved Content.
2. **Open Content Checker:** Click **Content Checker** in the left sidebar.
3. **Load Sample Copy:** Select *"High-Risk Promotional Copy (Violates Multiple Rules)"* from the sample dropdown.
4. **Run Analysis:** Click **Analyze Content**. Observe the multi-stage progress indicators.
5. **Inspect Violations:** Review flagged issues including prohibited absolute risk-free guarantees (`100% risk-free`), unsupported superlatives (`unmatched by anyone`), and deprecated nomenclature (`Legacy Cloud`).
6. **Cross-Referenced Claims:** Notice how the `64% reduction` metric is cross-referenced with Claim Passport record `CLM-801`.
7. **Side-by-Side Review:** Compare the original text with the automatically generated compliant draft.
8. **Interactive Editor:** Click **"Apply to Editor & Reanalyze"** to see instant compliance score recomputation.
9. **Submit for Review:** Click **"Send for Review"** to route the asset into the approval pipeline.
10. **Review Center:** Open the **Review Center**, select your reviewer identity (e.g. *Sarah Lin, Brand Director*), and formally approve or request changes with reviewer comments.
11. **Claim Passport:** Open **Claim Passport** to search verified claims, view evidence references, and inspect audit histories.
12. **Analytics & Reports:** Visit **Reports and Analytics** to review findings distributions, download CSV exports, or generate printable HTML compliance certificates.

---

## 📁 Project Structure

```
brandproof/
├── app.py                      # Multi-page router & application controller
├── requirements.txt            # Python dependencies (Streamlit, pandas, Plotly)
├── README.md                   # Complete documentation & judge guide
├── .gitignore                  # Git ignore rules for virtual environments & SQLite
├── .env.example                # Configuration template
├── config/
│   ├── __init__.py
│   └── settings.py             # Colors, categories, statuses, and constants
├── database/
│   ├── __init__.py
│   ├── db.py                   # SQLite schema definitions & connection pool
│   ├── models.py               # Data access layer (CRUD for all 8 entities)
│   └── seed_data.py            # Idempotent demo data seeder
├── modules/
│   ├── __init__.py
│   ├── checker_engine.py       # Rule engine, evidence cross-referencing, scoring
│   ├── ai_assistant.py         # Optional AI provider connector with fallback
│   ├── ui_components.py        # Reusable metric cards, badges, and headers
│   ├── export_utils.py         # CSV serialization & HTML report generation
│   └── pages/
│       ├── __init__.py
│       ├── overview.py         # Dashboard with KPIs & activity feed
│       ├── content_checker.py  # Interactive checker & correction editor
│       ├── claim_passport.py   # Claim Passport lifecycle & evidence manager
│       ├── review_center.py    # Multi-stage approval & reviewer workflows
│       ├── analytics.py        # Visual analytics & CSV export center
│       ├── settings_page.py    # Custom rule builder & brand profile manager
│       └── help_guide.py       # Interactive walkthrough & FAQ
├── assets/
│   └── style.css               # SaaS styling, typography, cards & badges
└── tests/
    ├── __init__.py
    └── test_checker.py         # Automated unit & integration tests
```

---

## ⚙️ Configuration & Optional AI Setup

By default, BrandProof runs in **100% deterministic rule-based mode**, requiring zero external API keys.

To enable optional AI deep rewriting:
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Configure your API key:
   ```env
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-4o-mini
   AI_PROVIDER=openai
   ```
3. Alternatively, you can enter the key directly in the **Settings ➔ AI Configuration** tab within the web interface.

---

## 🚢 Deployment Guide

### Deploying to Streamlit Community Cloud (Recommended)

1. Push the repository to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial BrandProof release"
   git remote add origin https://github.com/<your-username>/brandproof.git
   git push -u origin main
   ```
2. Visit [share.streamlit.io](https://share.streamlit.io) and log in with GitHub.
3. Click **"New app"**, select your repository, branch (`main`), and set the main file path to `brandproof/app.py`.
4. (Optional) Under Advanced Settings, add `OPENAI_API_KEY` if you want AI features enabled.
5. Click **"Deploy!"**. Your application will be live in 2 minutes.

---

## ⚖️ Compliance Notice & Known Limitations

- **Assessment Tool Only:** BrandProof provides internal policy consistency checks and evidence linkage. It does not provide formal legal counsel or regulatory guarantees.
- **Storage:** Uses local SQLite persistence. When deployed on ephemeral cloud instances (like basic containers), persistent volumes or cloud database backends (PostgreSQL) should be configured for long-term production deployments.
