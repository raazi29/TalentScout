# 🎯 TalentScout Hiring Assistant

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![AI Powered](https://img.shields.io/badge/AI-Powered-green.svg)](https://github.com/raazi29/Talentscout)

> **AI-Powered Candidate Screening Chatbot for Technical Positions**

An intelligent hiring assistant that conducts initial candidate interviews, gathers essential information, and generates relevant technical questions based on the candidate's tech stack.

## 🎬 Live Demo

🌐 **[Try TalentScout Live](https://talentscout-i0hd.onrender.com)** 

> *Experience the full interview process with multilingual support and real-time analytics*

## ✨ Key Features

- **🤖 Smart Interview Flow**: Guides candidates through structured screening process
- **💻 Tech Stack Assessment**: Generates tailored technical questions based on declared skills
- **🌍 Multilingual Support**: 21+ languages with automatic detection
- **📊 Real-time Analytics**: Progress tracking and candidate insights
- **🎨 Modern UI**: Clean, professional interface with dark theme
- **🔒 Secure Data Handling**: Privacy-compliant candidate information storage
- **⚡ Fast & Reliable**: Optimized performance with multiple LLM providers
## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/Raazi29/talentscout.git
cd talentscout

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
# Create .env file with your API keys:
GROQ_API_KEY=your_groq_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here

# 4. Run the application
streamlit run app.py
```

### Access the Application
Open your browser and go to: **http://localhost:8501**

## 💬 How It Works

1. **Greeting**: Chatbot welcomes the candidate and explains the process
2. **Information Gathering**: Collects essential details (name, contact, experience, position, location)
3. **Tech Stack Declaration**: Candidate specifies their technical skills and tools
4. **Technical Assessment**: Generates 3-5 relevant technical questions based on their stack
5. **Interview Conclusion**: Thanks candidate and explains next steps

## 🌍 Multilingual Support

**Automatic Language Detection:**
- Type in any supported language → System detects and adapts
- Example: "Hola, mi nombre es Carlos" → Switches to Spanish
- Manual selection available via sidebar dropdown

**Supported Languages (21+):**
🇺🇸 English | 🇪🇸 Español | 🇫🇷 Français | 🇩🇪 Deutsch | 🇮🇹 Italiano | 🇵🇹 Português | 🇷🇺 Русский | 🇨🇳 中文 | 🇯🇵 日本語 | 🇰🇷 한국어 | 🇮🇳 हिन्दी | 🇮🇳 বাংলা | 🇮🇳 தமிழ் | 🇮🇳 తెలుగు | 🇮🇳 मराठी | 🇮🇳 ગુજરાતી | 🇮🇳 ಕನ್ನಡ | 🇮🇳 മലയാളം | 🇮🇳 ਪੰਜਾਬੀ | 🇮🇳 اردو | 🇸🇦 العربية

## 🏗️ Technical Architecture

```
talentscout/
├── app.py                 # Main Streamlit application
├── config.py              # Configuration settings
├── requirements.txt       # Dependencies
├── utils/
│   ├── llm_router.py      # LLM API routing & fallback
│   ├── prompt_manager.py  # Prompt engineering
│   ├── conversation.py    # Interview flow management
│   ├── language_manager.py # Multilingual support
│   └── data_handler.py    # Data processing & storage
└── data/                  # Candidate data storage
```

## 🎯 Prompt Engineering Strategy

**Key Techniques Implemented:**
- **Role-Based Prompting**: Clear assistant role definition for each interview stage
- **Context Retention**: Maintains candidate information across conversation turns
- **Structured Output**: Consistent response formatting and data extraction
- **Tech Stack Analysis**: Intelligent question generation based on declared skills
- **Fallback Handling**: Graceful recovery from unexpected inputs

## 🔒 Data Privacy & Security

- ✅ Local data storage with randomized session IDs
- ✅ GDPR-compliant data handling practices
- ✅ Secure API communication with LLM providers
- ✅ No persistent storage of sensitive information

## 🚧 Key Challenges Solved

| Challenge | Solution |
|-----------|----------|
| **Context Maintenance** | Conversation manager tracks interview stages and candidate data |
| **Technical Question Generation** | LLM routing system analyzes tech stack for relevant questions |
| **Multilingual Support** | Auto-detection with confidence scoring and cultural adaptation |
| **Unexpected Inputs** | Fallback mechanisms guide conversation back to interview flow |

## 🎁 Bonus Features (Beyond Requirements)

- **🌍 21+ Languages**: Automatic detection and cultural adaptation
- **😊 Sentiment Analysis**: Real-time emotion detection during interviews
- **📊 Advanced Analytics**: Progress tracking and candidate insights
- **🎨 Modern UI/UX**: Professional dark theme with intuitive navigation
- **⚡ Performance Optimization**: Caching and efficient LLM routing

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For questions or issues:
- 📧 Email: support@talentscout.com
- 📚 Documentation: See inline code comments and docstrings
- 🐛 Issues: [GitHub Issues](https://github.com/raazi29/Talentscout/issues)

