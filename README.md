# 🤖 AI Job Application Assistant

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![CrewAI](https://img.shields.io/badge/CrewAI-Latest-green.svg)](https://crewai.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Transform your job applications with AI-powered resume tailoring and interview preparation using multi-agent intelligence.

## 🌟 Overview

The AI Job Application Assistant is an intelligent system that leverages multiple AI agents to analyze job postings, extract your professional profile, tailor your resume, and prepare comprehensive interview materials. Built with CrewAI and Google Gemini, it automates the tedious process of customizing applications for each job opportunity.

### 🎯 Key Features

- **🔍 Smart Job Analysis**: Automatically extracts key requirements from job postings
- **📄 Multi-Format Resume Support**: Handles PDF, Markdown, and text files
- **🎨 Intelligent Resume Tailoring**: Customizes your resume to match job requirements
- **🎤 Interview Preparation**: Generates relevant questions and talking points  
- **🤖 Multi-Agent Architecture**: Four specialized AI agents working in harmony
- **⚡ Real-time Processing**: Stream-based UI with progress tracking
- **🔄 Error Resilience**: Built-in retry logic and error handling

## 🏗️ Architecture

The system employs four specialized AI agents:

1. **📊 Tech Job Researcher**: Analyzes job postings to extract requirements
2. **👤 Personal Profiler**: Builds comprehensive candidate profiles
3. **📝 Resume Strategist**: Tailors resumes to match job requirements
4. **🎤 Interview Preparer**: Creates interview questions and talking points

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key
- SerperDev API key (for web searching)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/naakaarafr/AI-Job-Application-Assistant.git
   cd AI-Job-Application-Assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create a .env file or export directly
   export GOOGLE_API_KEY="your_gemini_api_key_here"
   export SERPER_API_KEY="your_serper_api_key_here"
   ```

4. **Run the application**
   ```bash
   streamlit run main.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8501`

## 📋 Requirements

Create a `requirements.txt` file with:

```txt
crewai>=0.28.0
crewai-tools>=0.1.0
streamlit>=1.28.0
python-dotenv>=1.0.0
PyPDF2>=3.0.0
nest-asyncio>=1.5.0
langchain-google-genai>=1.0.0
google-generativeai>=0.3.0
```

## 🔧 Configuration

### API Keys Setup

#### Google Gemini API
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Set as `GOOGLE_API_KEY` environment variable

#### SerperDev API
1. Sign up at [SerperDev](https://serper.dev)
2. Get your API key from the dashboard
3. Set as `SERPER_API_KEY` environment variable

### Model Configuration

The application supports multiple Gemini models with automatic fallback:
- `gemini-2.0-flash` (primary)
- `gemini-1.5-flash` (fallback)
- `gemini-1.5-pro` (fallback)
- `gemini-pro` (final fallback)

## 💻 Usage

### Basic Workflow

1. **Upload Resume**: Support for PDF, Markdown (.md), or text (.txt) files
2. **Enter Job Details**: Provide the job posting URL
3. **Add Personal Info**: Optional GitHub profile and personal writeup
4. **Generate Materials**: Click "Tailor My Application" to start processing
5. **Download Results**: Get your tailored resume and interview materials

### Advanced Features

#### Resume Processing
- **PDF Support**: Automatic text extraction using PyPDF2
- **Content Validation**: Preview and validation of extracted content
- **Semantic Search**: Intelligent content searching within resumes

#### Error Handling
- **Automatic Retries**: Built-in retry logic with exponential backoff
- **Peak Hour Detection**: Warnings and suggestions for optimal usage times
- **Graceful Degradation**: Fallback options when primary methods fail

## 📁 Project Structure

```
ai-job-application-assistant/
│
├── main.py                 # Streamlit web application
├── agents.py              # AI agent definitions and configurations
├── tasks.py               # Task definitions for agents
├── crew.py                # CrewAI crew orchestration
├── tools.py               # Utility tools and resume processing
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

### Core Components

#### `agents.py`
- Agent definitions with specialized roles
- LLM configuration and retry logic
- Load balancing across different models

#### `tasks.py`  
- Task definitions for each agent
- Context sharing between tasks
- Output file generation

#### `tools.py`
- Resume processing utilities
- PDF text extraction
- Web scraping and search tools

#### `main.py`
- Streamlit user interface
- File upload handling
- Progress tracking and error display

## 🛠️ Troubleshooting

### Common Issues

#### 503 Model Overloaded Error
- **Cause**: High API demand during peak hours
- **Solution**: 
  - Wait 5-10 minutes and retry
  - Use during off-peak hours (early morning/late evening)
  - The app automatically retries with backoff delays

#### Rate Limit Exceeded
- **Cause**: API usage limits reached
- **Solution**: Wait 1-5 minutes before retrying

#### Event Loop Errors
- **Cause**: Asyncio conflicts in Streamlit
- **Solution**: The app uses `nest-asyncio` to handle this automatically

#### File Processing Issues
- **Cause**: Corrupted or unsupported file formats
- **Solution**: 
  - Ensure file is in supported format (PDF, MD, TXT)
  - Try a smaller file size
  - Check file integrity

### Peak Usage Times

**Avoid these hours for best performance:**
- 9 AM - 5 PM (your local timezone)

**Optimal usage times:**
- Early morning: 6-8 AM
- Late evening: 9-11 PM

## 🔒 Privacy & Security

- **No Data Storage**: Files are processed temporarily and deleted after use
- **API Security**: All API keys are handled through environment variables
- **Local Processing**: Resume content is processed locally before API calls

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -m 'Add feature-name'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

### Contribution Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to new functions
- Include error handling for API calls
- Test with different file formats
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CrewAI**: For the multi-agent framework
- **Google Gemini**: For advanced language processing
- **Streamlit**: For the intuitive web interface
- **SerperDev**: For web search capabilities
- **PyPDF2**: For PDF processing

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review the system status in the app sidebar
3. Create an issue on [GitHub](https://github.com/naakaarafr/ai-job-application-assistant/issues)

## 🔮 Future Enhancements

- [ ] Support for additional file formats (DOCX, RTF)
- [ ] Integration with job boards for automatic job fetching
- [ ] Advanced analytics and success tracking
- [ ] Multi-language support
- [ ] Custom agent configurations
- [ ] Batch processing for multiple job applications

---

*Empower your job search with AI-driven insights and personalized application materials.*
