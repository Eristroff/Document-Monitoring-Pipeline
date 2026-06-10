# 📄 Document Monitoring Pipeline

> A multi-agent learning project that automatically monitors publicly available government documents and delivers structured weekly analysis reports.

---

## 🎯 Project Overview

This pipeline deploys a set of specialized AI agents to:

- **Discover** and track government documents from public sources (regulatory filings, policy updates, legislative records, etc.)
- **Ingest** new or updated documents on a scheduled basis
- **Analyze** content for key changes, trends, and insights
- **Report** findings through a structured weekly digest

This project is built for learning purposes — exploring agent orchestration, document intelligence, and automated reporting workflows.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Orchestrator Agent                        │
│              (Schedules & coordinates agents)                │
└────────────┬────────────────────────────────────────────────┘
             │
     ┌───────┼───────┬────────────────┐
     ▼       ▼       ▼                ▼
┌─────────┐ ┌──────────┐ ┌──────────────┐ ┌──────────────────┐
│ Crawler │ │ Ingestion│ │  Analysis    │ │ Reporting Agent  │
│  Agent  │ │  Agent   │ │   Agent      │ │                  │
│         │ │          │ │              │ │  Weekly Digest   │
│ Scrapes │ │ Parses & │ │ Summarizes,  │ │  Generator       │
│ Gov     │ │ stores   │ │ diffs, tags  │ │                  │
│ Sources │ │ documents│ │ key changes  │ │                  │
└─────────┘ └──────────┘ └──────────────┘ └──────────────────┘
```

---

## 🤖 Agents

| Agent | Role | Key Responsibilities |
|---|---|---|
| **Orchestrator** | Pipeline coordinator | Scheduling, task routing, error handling |
| **Crawler Agent** | Source discovery | Monitors gov portals, detects new/updated documents |
| **Ingestion Agent** | Document processing | Downloads, parses (PDF/HTML/XML), deduplicates |
| **Analysis Agent** | Intelligence extraction | Summarization, diff detection, entity tagging, trend tracking |
| **Reporting Agent** | Output generation | Compiles weekly digest, formats and delivers report |

---

## 📁 Project Structure

```
document-monitoring-pipeline/
│
├── agents/
│   ├── orchestrator.py       # Master scheduler and coordinator
│   ├── crawler.py            # Web scraping and source monitoring
│   ├── ingestion.py          # Document parsing and storage
│   ├── analysis.py           # NLP analysis and change detection
│   └── reporting.py          # Weekly report generation
│
├── config/
│   ├── sources.yaml          # Government document sources to monitor
│   └── schedule.yaml         # Run frequency and timing config
│
├── data/
│   ├── raw/                  # Downloaded raw documents
│   ├── processed/            # Parsed and cleaned documents
│   └── reports/              # Generated weekly analysis reports
│
├── prompts/
│   └── analysis_prompt.txt   # LLM prompt templates for analysis
│
├── tests/
│   └── ...                   # Unit and integration tests
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- An LLM API key (e.g., Anthropic Claude, OpenAI)
- Optional: A vector database (e.g., ChromaDB, Pinecone) for document storage

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/document-monitoring-pipeline.git
cd document-monitoring-pipeline

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys and settings
```

### Configuration

Edit `config/sources.yaml` to define the government sources you want to monitor:

```yaml
sources:
  - name: Federal Register
    url: https://www.federalregister.gov/
    doc_type: regulation
    check_interval: daily

  - name: Congress.gov Bills
    url: https://www.congress.gov/search
    doc_type: legislation
    check_interval: weekly
```

### Running the Pipeline

```bash
# Run the full pipeline manually
python agents/orchestrator.py --run-now

# Start the scheduler (runs on configured cadence)
python agents/orchestrator.py --schedule

# Run a specific agent in isolation
python agents/crawler.py
python agents/analysis.py --input data/processed/
```

---

## 📊 Weekly Report Output

Each weekly report includes:

- **New Documents Detected** — list of newly published or updated documents
- **Key Changes Summary** — LLM-generated summary of significant changes
- **Entity Highlights** — key organizations, dates, policy areas mentioned
- **Trend Analysis** — recurring themes across the week's documents
- **Full Document Index** — links and metadata for all monitored documents

Reports are saved to `data/reports/` and can be configured to send via email or Slack.

---

## 🧠 Learning Goals

This project is designed to explore:

- [ ] Agent orchestration patterns (sequential, parallel, hierarchical)
- [ ] Document ingestion pipelines (PDF parsing, HTML scraping, deduplication)
- [ ] LLM-powered summarization and change detection
- [ ] Scheduled automation with persistent state
- [ ] Structured report generation from unstructured data
- [ ] Error handling and retry logic in agentic systems

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| LLM | Anthropic Claude API |
| Scheduling | APScheduler / Cron |
| Document Parsing | PyMuPDF, BeautifulSoup, pdfplumber |
| Storage | SQLite / ChromaDB (vector store) |
| Reporting | Jinja2 templates + Markdown |

---

## 📌 Roadmap

- [x] Project scaffolding and architecture design
- [ ] Crawler agent — basic source monitoring
- [ ] Ingestion agent — PDF and HTML parsing
- [ ] Analysis agent — summarization and diff detection
- [ ] Reporting agent — weekly digest generation
- [ ] Scheduling and orchestration layer
- [ ] Email/Slack delivery integration
- [ ] Dashboard for report visualization

---

## 🤝 Contributing

This is a personal learning project, but feedback and ideas are welcome. Feel free to open an issue or submit a pull request.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built with curiosity and Mu-Sigma's commitment to data-driven decision making.*
