🤖 AI-Powered Data Query Chatbot
Query your data in plain English — no SQL knowledge required.

An intelligent, natural-language data analysis chatbot that allows users to upload datasets and ask business questions using everyday English. The application converts natural-language questions into SQL queries using a Large Language Model (LLM), executes those queries against MySQL, and presents the results through readable tables, formatted metrics, visualizations, and data-driven insights.

Built with Python, MySQL, Streamlit, and Groq LLM API, the application is designed to make data exploration accessible to both technical and non-technical users.

🔎 Project Overview

Traditional data analysis often requires users to know SQL or depend on data analysts for even simple questions such as:
- What was the total revenue?
- Which category generated the highest sales?
- What is the average customer rating?
- Which month had the highest number of orders?
- How many customers belong to a specific segment?
- This project provides a conversational interface between the user and the database.
- Instead of writing SQL manually, users can simply ask questions in natural language.

Example
User:
"What are the top 5 products by revenue?

🎯 Problem Statement

Business teams frequently need information from datasets, but not every stakeholder has SQL or programming knowledge.

This creates several challenges:

- Dependency on data analysts for routine questions
- Time-consuming manual SQL query creation
- Difficulty exploring unfamiliar datasets
- Risk of incorrect queries
- Difficulty interpreting raw database results
- Lack of immediate visual feedback

The goal of this project is to reduce this dependency by providing a natural-language interface for data querying and exploration.

## 🎯 Problem It Solves

The AI-Powered Data Query Chatbot allows users to:

Upload a dataset.

- Automatically detect its structure.
- Load the dataset into MySQL.
- Ask questions using plain English.
- Generate SQL dynamically using an LLM.
- Execute the generated SQL query.
- Validate and process the results.
- Automatically format important metrics.
- Select an appropriate visualization when possible.
- Display the answer in an easy-to-understand format.

No SQL knowledge is required from the end user.


⚙️ How It Works

The application follows a multi-stage data-querying pipeline.

## ✨ Features

- Natural Language to SQL

 Converts plain English questions into MySQL queries using Groq's LLM API
 
- Multi-format Data Upload

Supports CSV, Excel, JSON, and TSV files — works with any domain's dataset

- Dynamic Schema Detection

Automatically reads any uploaded dataset's structure — no hardcoding required

- Hallucination Prevention

Dynamically fetches actual column values (e.g., 'Yes'/'No' vs 1/0) to prevent the AI from guessing wrong formats

- Smart Formatting

Auto-detects currency (₹/$), percentages, counts, and ratings for context-appropriate display

- Intelligent Visualization

Automatically picks the right chart type (bar/line/pie) based on data characteristics

- Accurate Insights

Key statistics (max/min/average) are calculated in Python — not by the LLM — to guarantee 100% numerical accuracy

- Dataset Management

Upload, switch between, and delete datasets directly from the UI

- Technical Architecture

The application consists of four primary layers.

  1. Presentation Layer

  Built using:

  Streamlit

  Responsible for:

  • File upload

  • Dataset selection

  • Chat interface

  • Query input

  • Result display

  • Tables/Charts

  • Dataset management

  2. Application Layer

  Built using:

  Python

  Responsible for:

 • Dataset processing

 • Schema detection

 • Query orchestration

 • Result processing

 • Formatting

 • Visualization decisions

 • Error handling

 3. AI Layer

 Built using:

 Groq API + LLM

 Responsible for:

 • Understanding natural-language questions

 • Interpreting user intent

 • Generating SQL queries

 • Using schema and actual-value context

 4. Data Layer

 Built using:

 MySQL + SQLAlchemy

 Responsible for:

 • Dataset storage

 • SQL execution

 • Query results

 • Database connectivity

## 🛠️ Tech Stack

- **Backend** : Python, MySQL

- **AI** : Groq API (Llama/OpenAI OSS models)

- **Frontend** : Streamlit

- **Libraries** : pandas, SQLAlchemy, Altair

- **Environment Management** :  python-dotenv


## 📁 Project Structure

## 🔑 Key Technical Challenges Solved

- Fixed LLM hallucination on categorical/boolean columns by injecting real sample values into the prompt
- Corrected chronological date sorting (charts were defaulting to alphabetical order)
- Built a fallback system to show data as a table when it's unsuitable for charting
- Secured API keys using environment variables instead of hardcoding

## 🚀 How to Run Locally

1. Clone the Repository

2. Install dependencies:`pip install -r requirements.txt`

3. Create a `.env` file with your `GROQ_API_KEY` and `MYSQL_PASSWORD`

4. Run:`streamlit run app.py`


## ⚠️ Limitations

## 🔮 Future Enhancements

## 📌 Conclusion
