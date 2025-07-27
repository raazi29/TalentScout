# TalentScout Hiring Assistant

An intelligent AI-powered chatbot for conducting initial candidate screening interviews for technical positions.

## Overview

TalentScout Hiring Assistant is a Streamlit application that uses large language models to conduct preliminary job interviews with candidates. It gathers essential information and asks relevant technical questions based on the candidate's tech stack to help recruiters with the initial screening process.

The assistant handles the following tasks:
- Collects candidate details (name, contact info, experience, etc.)
- Asks about the candidate's technical skills and proficiencies
- Generates tailored technical questions based on the declared tech stack
- Maintains conversation context and provides a natural interview experience
- Stores candidate data securely for review by the hiring team

## Features

- **Intuitive UI**: Clean and user-friendly interface built with Streamlit
- **Context-Aware Conversation**: Maintains the flow of conversation across multiple turns
- **Tech Stack Matching**: Generates relevant technical questions based on the candidate's skills
- **Flexible LLM Routing**: Utilizes multiple language models for different conversation aspects
- **Data Persistence**: Securely stores candidate information for later review
- **Fallback Mechanisms**: Handles unexpected inputs gracefully
- **Sentiment Analysis**: Uses Hugging Face models
## Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Setup

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/talentscout.git
cd talentscout
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Create a `.env` file in the project root with the following variables:

```
GROQ_API_KEY=your_groq_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

## Usage

1. **Run the application**

```bash
streamlit run app.py
```

2. **Access the application**

Open your web browser and navigate to:
```
http://localhost:8501
```

3. **Start the interview**

The chatbot will guide candidates through the interview process, collecting information and asking technical questions.

## Project Structure

```
talentscout/
├── app.py                 # Main Streamlit application
├── config.py              # Configuration settings
├── requirements.txt       # Project dependencies
├── README.md              # Project documentation
├── utils/
│   ├── llm_router.py      # LLM API routing and fallback logic
│   ├── prompt_manager.py  # Prompt templates and engineering
│   ├── conversation.py    # Conversation flow management
│   ├── data_handler.py    # Data processing and storage
│   └── tech_questions.py  # Technical question generation
└── data/                  # Directory for stored candidate data
```

## Prompt Engineering Approach

This project utilizes several prompt engineering techniques:

1. **Role-Based Prompting**: Clearly defining the assistant's role in each conversation stage
2. **Context Retention**: Maintaining relevant candidate information across conversation turns
3. **Structured Output Control**: Guiding the model to produce consistently formatted responses
4. **Knowledge Integration**: Including technical knowledge for accurate question generation
5. **Fallback Handling**: Detecting and recovering from unexpected conversation paths

## Data Privacy and Security

- Candidate data is stored locally with randomized session IDs
- No personal information is transmitted externally except to LLM APIs
- All data processing complies with privacy best practices

## Challenges and Solutions

### Challenge 1: Context Maintenance

**Problem**: Ensuring the chatbot maintains context throughout the conversation.

**Solution**: Implemented a conversation manager that tracks the interview stage and candidate information, allowing for contextual responses and smooth transitions between topics.

### Challenge 2: Technical Question Generation

**Problem**: Generating relevant technical questions based on the candidate's skills.

**Solution**: Created a specialized prompt template and LLM routing system that analyzes the candidate's tech stack and experience level to produce appropriate technical questions.

### Challenge 3: Handling Unexpected Inputs

**Problem**: Gracefully handling off-topic or unexpected user responses.

**Solution**: Developed fallback mechanisms that attempt to extract relevant information when possible, or gently guide the conversation back to the interview flow.

## Future Enhancements

- **Sentiment Analysis**: Gauge candidate emotions during the conversation
- **Multilingual Support**: Support for interviews in multiple languages
- **Video Interview Integration**: Option for candidates to record video responses
- **Customizable Question Sets**: Allow recruiters to define custom technical assessment questions
- **Performance Analytics**: Dashboards for recruiters to analyze candidate performance

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or support, contact:
- Email: support@talentscout.com 

