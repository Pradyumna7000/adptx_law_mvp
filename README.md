# ADPTX Legal AI System

A comprehensive legal research and analysis system powered by AI agents for Indian law.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Groq API Key (for AI models)
- Indian Kanoon API Key (for legal data)

### Backend Setup
```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the server (from root directory)
python main.py
```

### Frontend Setup
```bash
# Install Node.js dependencies
cd frontend
npm install

# Run development server
npm run dev
```

## 📁 Project Structure

```
adaptx/
├── main.py                    # Root entry point (runs backend server)
├── README.md                  # This file
├── .env.example              # Environment variables template
├── frontend/                  # React frontend application
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatPage.jsx   # Main chat interface
│   │   │   ├── LandingPage.jsx # Landing page
│   │   │   └── FallbackComponent.jsx # Error handling
│   │   ├── App.jsx           # Main app component
│   │   └── main.jsx          # App entry point
│   ├── package.json          # Frontend dependencies
│   └── vite.config.js        # Vite configuration
└── backend/                  # Python backend server
    ├── main.py               # FastAPI server
    ├── requirements.txt      # Python dependencies (deployment-ready)
    ├── orchestrator.py       # Main AI orchestrator
    ├── pdf_rag_agent.py      # PDF processing agent
    ├── laws_agent.py         # Law retrieval agent
    ├── case_files_agent.py   # Case analysis agent
    ├── argument_simulator_agent.py # Legal arguments agent
    ├── legal_tools.py        # Legal search tools
    ├── kanoon_law_search.py  # Indian Kanoon integration
    ├── law_pdf_knowledge_base.py # PDF knowledge base
    ├── ikapi.py              # Indian Kanoon API
    ├── logs/                 # Application logs
    ├── uploads/              # File uploads
    ├── files/                # File storage
    ├── vector_store/         # Vector database
    ├── data/                 # Database files
    ├── pdf_storage/          # PDF storage
    ├── kanoon_data/          # Kanoon data
    └── law_data/             # Law data
```

## 🎯 Features

- **🤖 AI-Powered Legal Research**: Advanced legal research using multiple AI agents
- **📄 PDF Document Analysis**: Upload and analyze legal documents with AI
- **⚖️ Case Law Search**: Search for relevant legal precedents from Indian courts
- **💬 Legal Arguments**: Generate legal arguments and counterarguments
- **💬 Real-time Chat**: Interactive chat interface for legal queries
- **🔍 Indian Law Focus**: Specialized for Indian legal system and laws

## 🔌 API Endpoints

- `GET /api/health` - Health check and system status
- `POST /api/chat` - Legal research chat endpoint
- `POST /upload` - File upload endpoint
- `POST /api/analyze-pdf` - PDF analysis with custom queries

## 🛠️ Technologies

### Backend
- **FastAPI**: Modern, fast web framework
- **Python 3.8+**: Core programming language
- **Groq LLM**: High-performance AI models
- **SQLAlchemy**: Database ORM
- **LanceDB**: Vector database for embeddings

### Frontend
- **React 18**: Modern UI framework
- **Vite**: Fast build tool
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing

### AI & ML
- **Multiple AI Agents**: Specialized agents for different legal tasks
- **Vector Search**: Semantic search capabilities
- **Document Processing**: PDF and document analysis

## 🚀 Deployment

### Backend Deployment
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY="your_groq_api_key"
export INDIAN_KANOON_API_KEY="your_kanoon_api_key"

# Run with production server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend Deployment
```bash
# Build for production
cd frontend
npm run build

# Serve static files
npm run preview
```

### Docker Deployment (Optional)
```bash
# Build and run with Docker
docker build -t adptx-legal-ai .
docker run -p 8000:8000 adptx-legal-ai
```

## 🔧 Environment Variables

Create a `.env` file in the backend directory:

```env
# AI Models
GROQ_API_KEY=your_groq_api_key_here

# Legal Data
INDIAN_KANOON_API_KEY=your_kanoon_api_key_here

# Database
DATABASE_URL=sqlite:///./data/legal_research.db

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

## 📊 System Requirements

- **CPU**: 2+ cores recommended
- **RAM**: 4GB+ recommended
- **Storage**: 2GB+ for data and models
- **Network**: Stable internet for API calls

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
