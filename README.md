# Google Agent Development Kit (ADK) Tutorial

A hands-on repository demonstrating agent development using the **Google Agent Development Kit (ADK)** and the **Gemini API**.

This project showcases several agent architectures—from foundational conversational bots to multi-tool agents with custom Python functions, Google Search grounding, LangChain third-party integrations, and Gemini's built-in code execution.

---

## 🚀 Agents Overview

This repository includes five specialized agents:

### 1. `campusx_bot`
* **Type:** Conversational LLM Agent
* **Model:** `gemini-3.8-flash`
* **Features:** Introductory agent built with Google ADK for answering user queries and testing agent workflows.

### 2. `google_agent`
* **Type:** Grounded Search Agent
* **Model:** `gemini-3.8-flash`
* **Tools:** Built-in `GoogleSearchTool` (`google_search`)
* **Features:** Connects Gemini directly to Google Search for live web grounding, fact verification, and real-time data retrieval.

### 3. `tavily_search_agent`
* **Type:** Third-Party Tool Integration Agent
* **Model:** `gemini-3.8-flash`
* **Tools:** `LangchainTool` wrapping `TavilySearch`
* **Features:** Demonstrates how to bridge external LangChain ecosystem tools into Google ADK using `LangchainTool`.

### 4. `world_clock_agent`
* **Type:** Multi-Tool Advanced Agent
* **Model:** `gemini-3.8-flash`
* **Tools & Capabilities:**
  * **Custom Python Tool (`get_current_time`):** Accepts an IANA timezone string (e.g. `'Asia/Kolkata'`, `'America/New_York'`, `'UTC'`) and returns a structured dictionary with local date, time, 12-hour/24-hour formats, day of the week, and timezone abbreviations using `dateutil`.
  * **Google Search (`google_search`):** Grounding tool to look up unknown cities, regions, and timezone offsets.
  * **Built-in Code Interpreter (`BuiltInCodeExecutor`):** Allows the model to write and execute Python code in Gemini's sandbox environment.
  * **Server-Side Tool Invocations (`include_server_side_tool_invocations=True`):** Configures `types.ToolConfig` to expose server-side tool interactions (such as search queries and code execution outputs) directly within response events.

### 5. `campusx_student_management`
* **Type:** Database-Backed Workflow & Policy Agent
* **Model:** `gemini-3.8-flash`
* **Tools & Capabilities:**
  * **Student Lookup (`get_student_by_email`):** Query student records uniquely via email.
  * **Enrollment Tracking (`get_student_enrollments`):** Retrieve enrolled courses, progress, payment date, and refund status.
  * **Refund Policy Evaluation (`check_refund_eligibility`):** Automated business rule checking (eligible only if paid, within 7 days of payment, and <= 20% course completed).
  * **Refund Processing (`process_refund`):** Updates database records upon approved refund requests.
  * **Course Catalog (`list_courses`):** Lists all active courses.

---

## 🛠️ Project Structure

```text
google_adk_tutorial/
├── campusx_bot/
│   ├── agent.py               # Basic ADK LLM agent
│   └── __init__.py
├── google_agent/
│   ├── agent.py               # Agent with Google Search grounding
│   └── __init__.py
├── tavily_search_agent/
│   ├── agent.py               # Agent with LangChain Tavily search
│   └── __init__.py
├── world_clock_agent/
│   ├── agent.py               # Multi-tool agent (Clock + Search + Code Execution)
│   └── __init__.py
├── .env.example               # Template for environment variables
├── .gitignore                 # Git ignore rules
└── README.md                  # Project documentation
```

---

## 📦 Prerequisites & Installation

### 1. Clone the repository
```bash
git clone https://github.com/AbhinavEliac/Google_adk_tutorial.git
cd Google_adk_tutorial
```

### 2. Set up virtual environment
```bash
# Windows
python -m venv env
.\env\Scripts\activate

# macOS / Linux
python3 -m venv env
source env/bin/activate
```

### 3. Install dependencies
```bash
pip install google-adk google-genai python-dotenv python-dateutil langchain-tavily
```

### 4. Configure API Keys
Create a `.env` file in the root directory (or inside individual agent directories) based on `.env.example`:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
GOOGLE_GENAI_USE_ENTERPRISE=0

# Required only for tavily_search_agent:
TAVILY_API_KEY=your_tavily_api_key_here
```

> **Note:** Obtain your Gemini API key from [Google AI Studio](https://aistudio.google.com/).

---

## 🖥️ Running the Agents

### Command Line Interface (CLI)
You can run and interact with any agent via terminal using `adk run`:

```bash
# Run campusx_bot
adk run campusx_bot

# Run google_agent
adk run google_agent

# Run tavily_search_agent
adk run tavily_search_agent

# Run world_clock_agent
adk run world_clock_agent
```

### Web UI
Launch the interactive FastAPI-powered Web UI:

```bash
adk web
```
Then open your browser and navigate to:
```
http://127.0.0.1:8000
```

*(If port 8000 is occupied, use `adk web --port 8001`)*

---

## 👤 Author

* **Name:** Abhinav Gupta
* **Email:** [abhinavgupta15.ag@gmail.com](mailto:abhinavgupta15.ag@gmail.com)
* **GitHub:** [@AbhinavEliac](https://github.com/AbhinavEliac)
