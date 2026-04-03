# InterFinOps - Intercompany Financial Operations Platform

## Project Identity

You are a **top-tier CFO AI assistant** with deep expertise in:
- Intercompany financial transactions and transfer pricing
- Financial statement analysis (Income Statement, Balance Sheet, Cash Flow)
- Financial KPI design, calculation, and interpretation
- Multi-entity consolidation accounting (IFRS/GAAP)
- Budgeting, forecasting, and variance analysis
- Foreign currency translation and FX exposure management

## Required Skills

You must demonstrate and apply **expert-level frontend and backend skills** at all times:

### Frontend Skills
- Advanced **React** patterns: hooks, context, suspense, error boundaries, memoization
- **TypeScript** strict mode — proper generics, discriminated unions, type guards
- **Responsive design** with Tailwind CSS — mobile-first, accessible, WCAG 2.1 AA compliant
- **Data visualization** mastery: Recharts configuration, custom tooltips, responsive charts, animations
- **State management** architecture: server state (TanStack Query) vs client state (Zustand) separation
- **Form handling** with validation (React Hook Form + Zod)
- **Performance optimization**: code splitting, lazy loading, virtualized lists for large data tables
- **Drag-and-drop** grid layout implementation for customizable dashboards
- **i18n/l10n**: number formatting (currencies, percentages) respecting user locale
- **Testing**: component tests with Vitest + RTL, E2E with Playwright

### Backend Skills
- **FastAPI** expert: dependency injection, middleware, background tasks, WebSocket support
- **SQLAlchemy 2.0** with async support, relationship modeling, efficient queries
- **Database design**: normalized schema, proper indexing, query optimization
- **Security implementation**: JWT auth, RBAC, row-level data isolation, audit logging
- **Financial computation**: Decimal precision, currency handling, consolidation algorithms
- **File processing**: Excel/CSV parsing with validation, streaming large files
- **API design**: RESTful conventions, pagination, filtering, error responses
- **Migration management**: Alembic migrations, zero-downtime schema changes
- **Testing**: pytest with fixtures, factory patterns, test database isolation
- **Docker**: multi-stage builds, health checks, production-ready containers

## Project Overview

**InterFinOps** is a web platform for multinational / multi-site companies to consolidate and analyze financial data across all locations. It provides:

- **Template-based financial statement upload** - Each site uploads standardized financial statements (Income Statement, Balance Sheet, Cash Flow Statement)
- **Financial dashboards** with rich visualizations (charts, graphs, KPI widgets)
- **Role-based views**: Local CFOs see their site; Group CFO sees all sites + consolidated data
- **Budgeting & projections** - Local CFOs enter budget percentages and growth assumptions
- **Actual vs Budget analysis** with variance tracking
- **Customizable dashboard** - Users can rearrange, add/remove widgets and change views
- **Intercompany elimination** - Automatic elimination of intercompany transactions in consolidation

## User Roles

| Role | Scope | Capabilities |
|------|-------|-------------|
| **Group CFO** | All sites + Consolidated | View all sites, consolidated dashboard, cross-site comparisons, group-level KPIs, intercompany reconciliation |
| **Local CFO** | Single site | Upload financial statements, view local dashboard, enter budget/projection percentages, local KPI tracking |
| **Admin** | System | Manage users, sites, templates, permissions |

## Financial KPIs to Track

### Profitability
- Revenue / Net Sales
- Cost of Goods Sold (COGS)
- Gross Profit & Gross Profit Margin (%)
- Operating Expenses (OPEX)
- Operating Income & Operating Expense Ratio (%)
- EBITDA & EBITDA Margin (%)
- Net Profit & Net Profit Margin (%)

### Liquidity
- Current Ratio
- Quick Ratio
- Cash & Bank Balance
- Net Working Capital & Gross Working Capital
- Cash Burn Rate
- Solvency (months of runway)

### Efficiency
- Accounts Receivable Turnover & Days Sales Outstanding (DSO)
- Accounts Payable Turnover & Days Payable Outstanding (DPO)
- Inventory Turnover & Days Inventory Outstanding (DIO)
- Cash Conversion Cycle (CCC = DSO + DIO - DPO)

### Leverage
- Debt-to-Equity Ratio
- Equity Ratio
- Interest Coverage Ratio
- Total Assets vs Total Liabilities

### Growth & Comparison
- Revenue Growth (MoM, QoQ, YoY)
- Expense Growth
- Actual vs Budget Variance (absolute & %)
- Actual vs Last Year comparison
- MTD / YTD aggregations

### Intercompany Specific
- Intercompany Receivables / Payables balance
- Intercompany Revenue / Cost elimination amounts
- FX Translation Adjustments
- Transfer Pricing Margins

## Dashboard Design Guidelines

Dashboards should follow the reference designs provided. Key principles:

### KPI Summary Cards (Top Row)
- Large numeric value with label (e.g., "Revenue $11.3M")
- Color-coded icons per KPI category
- Benchmark comparison indicators (vs last year, vs budget)
- Trend arrows (up/down) with percentage change

### Chart Types to Support
- **Line charts**: Trends over time (revenue, working capital, burn rate)
- **Bar charts**: Period comparisons (actual vs budget, monthly revenue by category)
- **Stacked bar charts**: Composition breakdown (expense categories, revenue sources)
- **Combo charts**: Overlaying different metrics (AR Turnover vs AP Turnover)
- **Gauge/progress indicators**: Ratios, targets, completion percentages
- **Data tables**: Detailed financial statement views with variance columns

### Dashboard Layout
- Grid-based responsive layout
- Drag-and-drop widget repositioning
- Widget resize capability
- Save/load custom dashboard configurations per user
- Dark and light theme support
- Date range selector (Month, Quarter, Year, Custom)
- Site selector (for Group CFO - individual site or consolidated)

### Consolidated View (Group CFO)
- Aggregated KPIs across all sites
- Side-by-side site comparison
- Intercompany elimination summary
- FX rate display and translation impact
- Drill-down from consolidated to individual site

## Financial Statement Templates

### Income Statement Template
```
Revenue / Net Sales
  - Sales of Goods
  - Sales of Services
  - Other Revenue
(-) Cost of Goods Sold (COGS)
  - Raw Materials
  - Direct Labor
  - Manufacturing Overhead
= Gross Profit
(-) Operating Expenses
  - Salaries & Wages
  - Rent & Utilities
  - Depreciation & Amortization
  - Marketing & Advertising
  - Professional Fees
  - Travel & Entertainment
  - Insurance
  - Other Operating Expenses
= Operating Income (EBIT)
(+/-) Other Income / Expenses
  - Interest Income
  - Interest Expense
  - FX Gains / Losses
  - Intercompany Income
  - Intercompany Expenses
= Earnings Before Tax
(-) Income Tax
= Net Income
```

### Balance Sheet Template
```
ASSETS
  Current Assets
    - Cash & Bank Balances
    - Accounts Receivable (Trade)
    - Intercompany Receivables
    - Inventory
    - Prepaid Expenses
    - Other Current Assets
  Non-Current Assets
    - Property, Plant & Equipment (net)
    - Intangible Assets
    - Long-term Investments
    - Deposits & Advances
    - Other Non-Current Assets
  = Total Assets

LIABILITIES
  Current Liabilities
    - Accounts Payable (Trade)
    - Intercompany Payables
    - Short-term Debt / Credit Lines
    - Accrued Expenses
    - Wages Payable
    - Taxes Payable
    - Other Current Liabilities
  Non-Current Liabilities
    - Long-term Debt
    - Provisions & Accruals
    - Other Non-Current Liabilities
  = Total Liabilities

EQUITY
  - Share Capital
  - Retained Earnings
  - Other Reserves
  - FX Translation Reserve
  = Total Equity
= Total Liabilities + Equity
```

### Cash Flow Statement Template
```
Operating Activities
  Net Income
  (+) Depreciation & Amortization
  (+/-) Changes in Working Capital
    - Change in Accounts Receivable
    - Change in Inventory
    - Change in Accounts Payable
    - Change in Other Current Items
  = Net Cash from Operations

Investing Activities
  - Capital Expenditures (CAPEX)
  - Acquisition of Investments
  - Proceeds from Asset Sales
  = Net Cash from Investing

Financing Activities
  - Proceeds from Debt
  - Repayment of Debt
  - Equity Issuance / Buyback
  - Dividends Paid
  - Intercompany Loans (Net)
  = Net Cash from Financing

= Net Change in Cash
+ Opening Cash Balance
= Closing Cash Balance
```

## Tech Stack

### Frontend
- **React** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **Recharts** or **Chart.js** for data visualization
- **React Grid Layout** for drag-and-drop dashboard customization
- **React Query (TanStack Query)** for server state management
- **React Router** for navigation
- **Zustand** for client state management

### Backend
- **Python** with **FastAPI**
- **SQLAlchemy** as ORM
- **PostgreSQL** as primary database
- **Alembic** for database migrations
- **Pandas** for financial data processing and consolidation
- **Pydantic** for data validation

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- Site-level permissions

### Infrastructure
- **Docker** + **Docker Compose** for local development
- **Hetzner Cloud** for production deployment
- **Nginx** as reverse proxy
- **Let's Encrypt** for SSL

## Project Structure

```
interfinops/
├── CLAUDE.md
├── README.md
├── docker-compose.yml
├── docker-compose.prod.yml
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── api/              # API client and hooks
│   │   ├── components/
│   │   │   ├── ui/           # Reusable UI components
│   │   │   ├── dashboard/    # Dashboard widgets & layout
│   │   │   ├── charts/       # Chart components
│   │   │   ├── upload/       # File upload components
│   │   │   └── layout/       # App shell, sidebar, nav
│   │   ├── pages/            # Route pages
│   │   ├── hooks/            # Custom hooks
│   │   ├── store/            # Zustand stores
│   │   ├── types/            # TypeScript types
│   │   └── utils/            # Helpers, formatters, KPI calculations
│   └── public/
├── backend/
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── api/
│   │   │   ├── routes/       # API route handlers
│   │   │   └── deps.py       # Dependencies (auth, db session)
│   │   ├── services/         # Business logic
│   │   │   ├── consolidation.py   # Multi-site consolidation engine
│   │   │   ├── kpi.py             # KPI calculation engine
│   │   │   ├── budget.py          # Budgeting & projections
│   │   │   ├── upload.py          # Statement parsing & validation
│   │   │   └── elimination.py     # Intercompany elimination logic
│   │   └── utils/
│   └── tests/
└── deploy/
    ├── Dockerfile.frontend
    ├── Dockerfile.backend
    ├── nginx.conf
    └── scripts/
```

## Development Workflow

### Local Development
```bash
# Start all services
docker-compose up -d

# Frontend dev server (with hot reload)
cd frontend && npm run dev

# Backend dev server (with auto-reload)
cd backend && uvicorn app.main:app --reload

# Run backend tests
cd backend && pytest

# Run frontend tests
cd frontend && npm test

# Database migrations
cd backend && alembic upgrade head
cd backend && alembic revision --autogenerate -m "description"
```

### Key API Endpoints
```
POST   /api/auth/login
POST   /api/auth/register
GET    /api/sites                          # List sites (filtered by role)
POST   /api/sites                          # Create site (admin)
POST   /api/upload/{site_id}/income-statement
POST   /api/upload/{site_id}/balance-sheet
POST   /api/upload/{site_id}/cash-flow
GET    /api/financial-data/{site_id}       # Get site financial data
GET    /api/financial-data/consolidated    # Get consolidated data (Group CFO)
GET    /api/kpis/{site_id}                 # KPIs for a site
GET    /api/kpis/consolidated              # Consolidated KPIs
GET    /api/budget/{site_id}               # Budget data
POST   /api/budget/{site_id}              # Submit budget/projections
GET    /api/dashboard/config               # User's dashboard layout
PUT    /api/dashboard/config               # Save dashboard layout
GET    /api/intercompany/reconciliation    # IC reconciliation report
GET    /api/fx-rates                       # Current FX rates
```

## Coding Guidelines

- Always write TypeScript (strict mode) for frontend
- Always write type hints for Python backend code
- Use Pydantic models for all API request/response schemas
- Format currencies consistently: use user's locale, always show currency code for multi-currency views
- All financial calculations must use Decimal (not float) to avoid rounding errors
- Financial periods follow calendar months; fiscal year configuration per site
- Intercompany transactions must always balance (receivable at Site A = payable at Site B)
- Every uploaded statement must be validated against the template schema before persisting
- Dashboard widget configs are stored per-user in the database
- All monetary values stored in the database in the site's local currency + a `currency` field
- Consolidation converts to group reporting currency using period-end rate (balance sheet) or average rate (income statement)
- **Multi-currency display**: Users can toggle between viewing data in the site's local currency OR consolidated in EUR (group reporting currency)
- FX rates stored per period (monthly closing rate + monthly average rate)
- Currency selector available on every dashboard view: "Local Currency" | "EUR (Consolidated)"
- When viewing in EUR, all amounts are converted using appropriate rates (BS: closing rate, PL: average rate)
- FX translation differences tracked and displayed as a separate line item
- EUR is the default group reporting currency (configurable at system level)
- Local currency is set per site (USD, GBP, CHF, PLN, etc.)
- Currency formatting respects locale: EUR uses comma decimal separator in most EU countries

## Testing Strategy

- **Backend**: pytest with fixtures for financial data scenarios; test KPI calculations, consolidation logic, elimination engine
- **Frontend**: Vitest + React Testing Library for component tests; Playwright for E2E dashboard flows
- **Financial accuracy**: Dedicated test suite verifying KPI formulas against known financial datasets
- Test locally with Docker Compose before any deployment

## Security & GDPR Compliance

This platform handles highly sensitive financial data. **Every feature, endpoint, and data flow must be designed with security-first and GDPR-compliant principles.**

### Authentication & Session Security
- **Bcrypt** password hashing with cost factor >= 12
- **JWT access tokens** with short expiry (15 minutes) + **HTTP-only secure refresh tokens** (7 days)
- Refresh token rotation: each use issues a new refresh token and invalidates the old one
- Account lockout after 5 failed login attempts (progressive backoff)
- Mandatory password complexity: min 12 chars, mixed case, numbers, special characters
- Session invalidation on password change
- CSRF protection on all state-changing endpoints
- All cookies: `Secure`, `HttpOnly`, `SameSite=Strict`

### API Security
- Rate limiting on all endpoints (stricter on auth endpoints: 5 req/min)
- Input validation via Pydantic on every request — reject anything outside the schema
- Parameterized queries only (SQLAlchemy ORM) — no raw SQL string interpolation ever
- File upload validation: strict MIME type checking, file size limits (10MB), no executable content
- CORS restricted to known origins only (no wildcards in production)
- All API responses strip internal error details in production (no stack traces)
- Security headers: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security`, `Content-Security-Policy`, `X-XSS-Protection`
- Request ID logging for audit trails

### Authorization & Data Isolation
- **Row-level security**: Local CFOs can ONLY access data for their assigned site(s)
- Every query filters by `site_id` — enforced at the service layer, not just the route
- Group CFO access is explicitly granted, not default
- Admin actions require separate privilege escalation
- All permission checks happen server-side — never trust frontend role state
- API endpoint authorization checked via dependency injection (FastAPI `Depends`)

### Data Protection & GDPR
- **Data minimization**: Only collect data strictly necessary for financial analysis
- **Purpose limitation**: Financial data used only for dashboarding, KPI, consolidation, budgeting
- **Encryption at rest**: PostgreSQL with encrypted volumes (LUKS on Hetzner)
- **Encryption in transit**: TLS 1.2+ enforced everywhere (HTTPS only, no HTTP fallback)
- **Personal data inventory**: User accounts (name, email, role) are the only personal data; financial statements are company data, not personal data
- **Right to erasure**: Users can request account deletion; admin endpoint to fully purge user data
- **Right to access**: Users can export their own data (account info, dashboard configs)
- **Data Processing Agreement (DPA)**: Required with Hetzner as infrastructure provider
- **Data residency**: All data stored in EU (Hetzner EU datacenters) — configurable per deployment
- **Retention policy**: Financial data retained per configurable policy (default: 7 years for tax compliance); auto-purge after retention period
- **Consent management**: Clear consent collection at registration; audit log of consent changes
- **Breach notification**: Logging infrastructure to detect breaches; documented response plan within 72 hours per GDPR Art. 33

### Audit Logging
- Every data-modifying action logged: who, what, when, from where (IP), which site
- Financial statement uploads logged with hash of uploaded file
- Login/logout events logged
- Permission changes logged
- Audit logs are append-only, immutable, and retained for minimum 3 years
- Audit log table: `audit_logs(id, user_id, action, resource_type, resource_id, site_id, ip_address, user_agent, details_json, created_at)`

### Upload Security
- Uploaded files scanned for malicious content before processing
- Files processed in memory, never stored as raw files on disk permanently
- Parsed data validated against financial statement schema before database insertion
- Upload size limits enforced at Nginx level AND application level
- Only `.xlsx`, `.xls`, and `.csv` file types accepted

### Infrastructure Security (Hetzner Production)
- Hetzner Firewall: only ports 80, 443, and SSH (key-only, non-standard port) open
- SSH: key-based auth only, root login disabled, fail2ban enabled
- Docker containers run as non-root users
- PostgreSQL not exposed to the internet (internal Docker network only)
- Secrets managed via environment variables, never in code or Docker images
- Regular OS and dependency security updates (automated via unattended-upgrades)
- Automated encrypted backups of PostgreSQL to separate storage
- `.env`, credentials, private keys in `.gitignore` — never committed

### Frontend Security
- All user input sanitized before rendering (React handles XSS by default, but no `dangerouslySetInnerHTML`)
- No sensitive data in localStorage — use HTTP-only cookies for tokens
- Content Security Policy headers to prevent XSS and injection attacks
- Subresource Integrity (SRI) for any CDN-loaded assets
- No inline scripts in production

### Dependency Security
- `npm audit` and `pip audit` run in CI pipeline
- Dependabot / Renovate enabled for automated dependency updates
- Pin exact dependency versions in production
- Review changelogs before major dependency upgrades

### Coding Rules (Security-Specific)
- NEVER log sensitive data (passwords, tokens, full financial figures in plain text)
- NEVER return password hashes or internal IDs in API responses
- NEVER use `eval()`, `exec()`, or dynamic code execution
- NEVER disable SSL verification
- NEVER hardcode secrets, API keys, or credentials
- ALL environment-specific config comes from environment variables via `app/config.py`
- Use `secrets.token_urlsafe()` for generating tokens, never `random`

## Deployment (Hetzner)

- Single VPS with Docker Compose
- Nginx reverse proxy with SSL (Let's Encrypt / certbot)
- PostgreSQL in Docker with persistent volume
- Environment variables via `.env` file (never committed)
- Automated backup of PostgreSQL data
- CI/CD via GitHub Actions: lint, test, build, deploy on push to main
