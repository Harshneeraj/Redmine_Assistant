# Redmine_Assistant
Creating a redmine assistant, capable of performing actions in redmine via langgraph

# 🧠 Redmine Assistant with LangGraph + LangChain + Selenium

This project implements a conversational AI assistant that automates tasks in a Redmine project management system using LangGraph, LangChain, and Selenium-based tools.

## 🚀 Features

- Chat-based assistant for interacting with Redmine  
- Login automation with Redmine  
- Project listing and issue management  
- Time logging against issues  
- Tool execution with fallback handling  
- Persistent dialog state using LangGraph memory  

## 🛠 Tech Stack

- LangGraph – Graph-based state machines for LLM agents  
- LangChain – LLM orchestration framework  
- Selenium – For web automation  
- Groq LLM (LLaMA 3) – Ultra-fast inference via GroqCloud  
- Python – Core programming language  

## 📁 Project Structure

```
.
├── tools/                      # Custom Selenium tools
├── assistant.py               # Core assistant logic
├── README.md                  # This file
└── requirements.txt           # Python dependencies
```

## 🔧 Setup Instructions

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/redmine-assistant.git
cd redmine-assistant
```

2. **(Optional) Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Set Environment Variables**
```bash
export GROQ_API_KEY=your_groq_api_key
```
Or set it in code:
```python
llm = ChatGroq(model="llama-3-3-70b-versatile", groq_api_key="your_groq_api_key")
```

5. **Run the Assistant**
```bash
python assistant.py
```

## 💡 Available Tools

- login_to_redmine – Logs into Redmine  
- list_projects – Lists available projects  
- create_issue – Creates a new issue  
- list_issues – Lists assigned issues  
- log_time_to_selected_issue – Logs time on an issue  

## 💬 Example Usage

```
User Input: login to redmine  
Assistant: Logging in...  
Tool: Successfully logged in.

User Input: list projects  
Assistant: Here are your projects:  
- Project X  
- Project Y  
```

Type `exit` to quit.

## 📎 License

MIT License

## 👨‍💻 Author

Built by Harsh