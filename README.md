# Autonomous AI Tutor Orchestrator

An intelligent middleware system that orchestrates educational tools through conversational AI, built with FastAPI, LangGraph, and LangChain.

## 🎉 Project Status: **FULLY IMPLEMENTED AND WORKING** ✅

**Demo Available**: Run `python simple_demo.py` to see the system in action!  
**API Server**: Run `python -m uvicorn app.main:app --reload` for REST API access!

## 🎯 Overview

This system acts as the "brain" between a student's conversation with an AI tutor and educational tools (quiz generators, note makers, concept explainers). It intelligently extracts parameters from natural conversation and automatically executes the appropriate educational tools.

## 🏗️ Architecture

### Core Components
- **Context Analysis Engine**: Parses conversation history and identifies educational intent
- **Parameter Extraction System**: Maps conversational elements to specific tool parameters
- **Tool Orchestration Layer**: Manages API calls to multiple educational tools
- **State Management**: Maintains conversation context and student personalization
- **Schema Validation**: Ensures proper tool execution with validated parameters

### Supported Educational Tools
1. **Note Maker Tool** - Generates structured notes based on topics and learning styles
2. **Flashcard Generator** - Creates practice flashcards with adaptive difficulty
3. **Concept Explainer** - Provides detailed explanations with examples and analogies

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL (optional, for persistent storage)

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional)
cp .env.example .env
# Edit .env with your configuration if you have API keys

# Run the core functionality demo
python simple_demo.py

# OR run the full FastAPI server
python -m uvicorn app.main:app --reload
```

### API Documentation
Once running, visit:
- API Documentation: http://localhost:8000/docs
- Interactive API: http://localhost:8000/redoc

## 🎓 Educational Context Integration

### Teaching Styles
- **Direct**: Clear, step-by-step instruction
- **Socratic**: Question-based guided discovery
- **Visual**: Imagery and analogical explanations
- **Flipped Classroom**: Application-focused learning

### Emotional States
- **Focused/Motivated**: Ready for challenges
- **Anxious**: Needs reassurance and simplified approach
- **Confused**: Requires step-by-step breakdown
- **Tired**: Minimal cognitive load

### Mastery Levels (1-10)
- Levels 1-3: Foundation building with scaffolding
- Levels 4-6: Developing competence with guided practice
- Levels 7-9: Advanced application and understanding
- Level 10: Full mastery enabling teaching others

## 📝 Example Usage

```python
# Example conversation that triggers note generation
student_message = "I'm struggling with calculus derivatives and need some organized notes"

# System automatically:
# 1. Identifies "Note Maker" tool is needed
# 2. Extracts parameters: topic="derivatives", subject="calculus"
# 3. Infers note_taking_style based on student preference
# 4. Executes tool and returns formatted notes
```

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Run integration tests
pytest tests/integration/

# Run with coverage
pytest --cov=app tests/
```

## 📊 Performance Metrics

The system is designed to handle:
- 80+ different educational tools
- Sub-second parameter extraction
- Concurrent tool orchestration
- Scalable architecture for production use

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔧 Technical Details

### API Endpoints
- `POST /orchestrate` - Main orchestration endpoint
- `POST /extract-parameters` - Parameter extraction service
- `GET /tools` - List available educational tools
- `GET /health` - System health check

### Configuration
Environment variables in `.env`:
```
DATABASE_URL=postgresql://localhost/tutor_orchestrator
LANGCHAIN_API_KEY=your_api_key
LOG_LEVEL=INFO
```

For detailed implementation documentation, see the `/docs` directory.