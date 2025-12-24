# Retail Insights Assistant 🛍️

## Enterprise-Grade Multi-Agent GenAI System for Retail Analytics

A sophisticated GenAI-powered solution that enables natural language querying of retail sales data, automated insight generation, and scalable analytics for organizations dealing with large-scale retail datasets.

---

## 🎯 Overview

The Retail Insights Assistant is a production-ready multi-agent system that combines:
- **Advanced LLM Integration** (OpenAI GPT-4 / Google Gemini)
- **Multi-Agent Architecture** (LangGraph orchestration)
- **Efficient Data Processing** (DuckDB for OLAP queries)
- **Intuitive UI** (Streamlit interface)
- **Scalable Design** (Architecture for 100GB+ datasets)

### Key Capabilities

✅ **Conversational Q&A**: Ask business questions in natural language  
✅ **Automated Summarization**: Generate comprehensive insights reports  
✅ **Multi-Agent System**: 4 specialized agents working in orchestration  
✅ **Data Validation**: Ensures accuracy and quality of results  
✅ **Scalable Architecture**: Designed for enterprise-scale data (100GB+)

---

## 🏗️ System Architecture

### Multi-Agent Workflow

```
User Question
    ↓
┌─────────────────────────────────────────────────┐
│  Agent 1: Query Resolution Agent                │
│  • Interprets natural language                  │
│  • Extracts entities (regions, dates, metrics)  │
│  • Generates SQL queries                        │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│  Agent 2: Data Extraction Agent                 │
│  • Executes SQL on DuckDB                       │
│  • Retrieves relevant data                      │
│  • Generates data summaries                     │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│  Agent 3: Validation Agent                      │
│  • Validates result quality                     │
│  • Checks data integrity                        │
│  • Flags anomalies                              │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│  Agent 4: Response Generation Agent             │
│  • Creates natural language responses           │
│  • Provides business insights                   │
│  • Formats results clearly                      │
└─────────────────────────────────────────────────┘
    ↓
Final Answer to User
```

### Technology Stack

- **LLM Framework**: LangChain + LangGraph
- **LLM Providers**: OpenAI GPT-4 / Google Gemini
- **Database**: DuckDB (embedded OLAP database)
- **UI Framework**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Language**: Python 3.9+

---

## 📦 Project Structure

```
retail-insights-assistant/
├── agents/
│   ├── query_agent.py          # Agent 1: Query resolution
│   ├── extraction_agent.py     # Agent 2: Data extraction
│   ├── validation_agent.py     # Agent 3: Result validation
│   ├── response_agent.py       # Agent 4: Response generation
│   └── orchestrator.py         # LangGraph orchestration
├── utils/
│   ├── data_layer.py           # DuckDB integration
│   └── llm_utils.py            # LLM utilities
├── data/
│   ├── generate_data.py        # Sample data generator
│   └── sales_data.csv          # Generated data (not in repo)
├── tests/
│   └── test_agents.py          # Unit tests
├── docs/
│   ├── ARCHITECTURE.md         # Detailed architecture
│   └── SCALABILITY.md          # 100GB+ design
├── screenshots/                # Demo screenshots
├── app.py                      # Streamlit UI
├── config.py                   # Configuration
├── requirements.txt            # Dependencies
├── .env.example                # Environment template
└── README.md                   # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- OpenAI API key OR Google Gemini API key
- 4GB RAM minimum (8GB recommended)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd retail-insights-assistant
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your API key:
# For OpenAI: OPENAI_API_KEY=your_key_here
# For Gemini: GOOGLE_API_KEY=your_key_here
```

5. **Generate sample data**
```bash
python data/generate_data.py
```
This creates `data/sales_data.csv` with 50,000 sample transactions.

6. **Run the application**
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 💻 Usage

### Conversational Q&A Mode

Ask natural language questions like:
- "What were total sales in Q3 2023?"
- "Which region had the highest growth in 2023?"
- "Top 5 products by profit?"
- "Compare Electronics vs Clothing category revenue"
- "Show monthly sales trend for the North region"

### Summary Mode

Generate automated comprehensive reports covering:
- Overall performance metrics
- Regional analysis
- Category breakdowns
- Year-over-year trends
- Channel performance

### Data Explorer

Visualize key metrics with:
- Interactive charts
- Regional breakdown
- Category performance
- Yearly trends

---

## 🔧 Configuration

### LLM Selection

Edit `.env` to choose your LLM provider:

**Option 1: OpenAI (Recommended)**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview
```

**Option 2: Google Gemini**
```env
LLM_PROVIDER=google
GOOGLE_API_KEY=your-key-here
GEMINI_MODEL=gemini-pro
```

### Advanced Settings

```env
MAX_CONTEXT_LENGTH=4000      # Maximum tokens for context
TEMPERATURE=0.1              # LLM temperature (0.0 = deterministic)
MAX_TOKENS=2000              # Maximum response tokens
```

---

## 🧪 Testing

Run the test suite:
```bash
pytest tests/ -v
```

Test individual components:
```bash
# Test query agent
python -c "from agents.query_agent import QueryResolutionAgent; agent = QueryResolutionAgent(); print(agent.resolve_query('What were total sales?'))"

# Test data layer
python -c "from utils.data_layer import get_data_layer; dl = get_data_layer(); print(dl.get_summary_stats())"
```

---

## 📊 Sample Questions & Outputs

### Example 1: Revenue Analysis
**Q**: "What were total sales in 2023?"  
**A**: "In 2023, total sales reached $XX.XX million across X,XXX transactions, representing a YY% increase compared to 2022..."

### Example 2: Regional Comparison
**Q**: "Which region performed best?"  
**A**: "The West region led in revenue with $X.XX million (XX% of total), followed by North ($X.XX million, XX%)..."

### Example 3: Category Insights
**Q**: "Top 3 categories by profit margin?"  
**A**: "Electronics achieved the highest profit margin at XX%, generating $X.XX million in profit..."

---

## 🔐 Security & Privacy

- API keys stored in `.env` (never committed to repo)
- No data leaves your local environment (except LLM API calls)
- DuckDB database is local and embedded
- All processing happens on your machine

---

## 🎓 Project Highlights

### Technical Excellence
✅ **Multi-Agent Design**: 4 specialized agents with clear separation of concerns  
✅ **LangGraph Orchestration**: State-based workflow management  
✅ **Efficient Querying**: DuckDB for sub-second analytics  
✅ **Error Handling**: Graceful failure recovery at each stage  
✅ **Validation Layer**: Ensures data quality and accuracy

### Production-Ready Features
✅ **Configurable LLM**: Support for multiple providers  
✅ **Conversation History**: Track query patterns  
✅ **Data Explorer**: Visual analytics  
✅ **Export Functionality**: Download reports  
✅ **Extensible Architecture**: Easy to add new agents

---

## 📈 Scalability to 100GB+

See [docs/SCALABILITY.md](docs/SCALABILITY.md) for detailed architecture.

### Key Strategies

1. **Data Lake Architecture**: Store raw data in S3/GCS/Azure
2. **Distributed Processing**: Use PySpark/Dask for ETL
3. **Data Warehouse**: Snowflake/BigQuery for OLAP
4. **Vector Indexing**: FAISS/Pinecone for semantic search
5. **Caching Layer**: Redis for frequent queries
6. **Query Optimization**: Partitioning, columnar storage
7. **RAG Pattern**: Retrieve relevant subsets before querying

**Estimated Performance at Scale**:
- **100GB Dataset**: < 2 second query response
- **1TB Dataset**: < 5 second query response
- **10TB Dataset**: < 10 second query response (with proper indexing)

---

## 🛠️ Assumptions & Limitations

### Current Implementation Assumptions
- Data fits in memory (< 5GB CSV recommended for local demo)
- Single-user application (no concurrent access)
- English language queries only
- Structured tabular data (CSV format)
- Date range: 2021-2023 (configurable)

### Known Limitations
- No real-time streaming data support
- Limited to predefined schema
- No user authentication/authorization
- Single database instance
- No distributed query execution

### Planned Improvements
- [ ] Multi-user support with authentication
- [ ] Real-time data ingestion
- [ ] Support for unstructured data (PDFs, images)
- [ ] Advanced visualizations (Plotly, charts)
- [ ] Query caching for performance
- [ ] API endpoint for programmatic access
- [ ] Multi-language support
- [ ] Advanced RAG with vector embeddings

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📄 License

MIT License - see LICENSE file for details

---

## 👥 Author

**Your Name**  
Email: your.email@example.com  
GitHub: @yourusername  
LinkedIn: linkedin.com/in/yourprofile

---

## 🙏 Acknowledgments

- **LangChain**: For the excellent LLM framework
- **LangGraph**: For multi-agent orchestration
- **DuckDB**: For blazing-fast analytics
- **Streamlit**: For the beautiful UI framework
- **OpenAI/Google**: For powerful LLM APIs

---

## 📞 Support

For questions or issues:
- Open a GitHub issue
- Email: support@yourcompany.com
- Documentation: [docs/](docs/)

---

**Built with ❤️ for Blend360 GenAI Interview Assignment**

*Demonstrating enterprise-grade GenAI engineering, scalable architecture design, and production-ready implementation.*
