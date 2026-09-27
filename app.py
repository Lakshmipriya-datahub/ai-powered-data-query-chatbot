import streamlit as st
from groq import Groq
import pandas as pd
import mysql.connector
from decimal import Decimal
import time
import re
import altair as alt
from dotenv import load_dotenv
import os
load_dotenv()

def choose_chart_type(labels, values, question):
    """Intelligently pick the best chart type based on data characteristics"""
    question_lower = question.lower()
    
    # Check if labels look like dates/months/years -> Line chart
    date_keywords = ["date", "month", "year", "day", "week", "time", "trend", "over time"]
    is_time_based = any(keyword in question_lower for keyword in date_keywords)
    
    # Check average label length -> long labels need horizontal bar chart
    avg_label_length = sum(len(str(l)) for l in labels) / len(labels)
    
    # Check number of categories -> too many categories, pie chart doesn't work well
    num_categories = len(labels)
    
    if is_time_based:
        return "line"
    elif num_categories <= 6 and avg_label_length < 15:
        return "pie"  # good for part-of-whole with few categories
    elif avg_label_length > 12:
        return "horizontal_bar"  # long names need horizontal space
    else:
        return "bar"  # default, short names, many categories

# Page setup
st.set_page_config(page_title="AI Data Query Chatbot", page_icon="📈", layout="centered")
st.markdown("""
<style>
    /* Main background - black with purple gradient */
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #1a0b2e 50%, #16031f 100%);
    }
    
    /* Title styling */
    h1 {
        color: #c084fc !important;
        font-weight: 700 !important;
        animation: fadeIn 1s ease-in;
    }
    
    /* Regular text */
    p, label, .stMarkdown {
        color: #e2d9f3 !important;
    }
    
    /* Text input box */
    .stTextInput input {
        background-color: #1e1033;
        color: white;
        border: 2px solid #7c3aed;
        border-radius: 10px;
        padding: 10px;
        transition: all 0.3s ease;
    }
    .stTextInput input:focus {
        border-color: #a855f7;
        box-shadow: 0 0 10px rgba(168, 85, 247, 0.5);
    }
    
    /* Selectbox */
    .stSelectbox [data-baseweb="select"] {
        background-color: #1e1033;
        border: 2px solid #7c3aed;
        border-radius: 10px;
    }
    
    /* Success/Info boxes */
    .stSuccess {
        background-color: rgba(124, 58, 237, 0.15) !important;
        border: 1px solid #7c3aed !important;
        border-radius: 10px;
        animation: slideIn 0.5s ease-out;
    }
    .stInfo {
        background-color: rgba(168, 85, 247, 0.15) !important;
        border: 1px solid #a855f7 !important;
        border-radius: 10px;
        animation: slideIn 0.5s ease-out;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0f0518;
        border-right: 1px solid #4c1d95;
    }
    
    /* Code blocks */
    .stCodeBlock {
        border: 1px solid #7c3aed;
        border-radius: 8px;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
/* Info box (Key Insights) - match dark purple theme */
    div[data-testid="stAlert"] {
        background-color: #1a0b2e !important;
        border: 1px solid #a855f7 !important;
        border-radius: 10px !important;
    }
    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] span,
    div[data-testid="stAlert"] div,
    div[data-testid="stAlert"] li,
    div[data-testid="stAlert"] * {
        color: #e2d9f3 !important;
        background-color: transparent !important;
    }
/* Purple outline for ALL buttons */
    .stButton button, [data-testid="stFileUploader"] button, [data-testid="baseButton-secondary"] {
        border: 2px solid #a855f7 !important;
        border-radius: 8px !important;
    }
    
    /* Purple outline for text input */
    .stTextInput input {
        border: 2px solid #a855f7 !important;
    }
    
    /* Purple outline for selectbox/dropdown */
    [data-testid="stSelectbox"] > div > div {
        border: 2px solid #a855f7 !important;
        border-radius: 8px !important;
    }
    
    /* Purple outline for file uploader box */
    [data-testid="stFileUploaderDropzone"] {
        border: 2px solid #a855f7 !important;
    }
    
    /* Purple outline for code block (SQL query box) */
    .stCodeBlock, [data-testid="stCode"] {
        border: 2px solid #a855f7 !important;
        border-radius: 8px !important;
    }
    
    /* Purple outline for success/info boxes */
    [data-testid="stAlert"] {
        border: 2px solid #a855f7 !important;
    }
    /* Purple outline for chat */
    [data-testid="stVegaLiteChart"] {
        border: 2px solid #a855f7 !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        background-color: #0f0518 !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    [data-testid="stVegaLiteChart"] > div {
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
    }
/* Text input - force purple even when focused/active */
    .stTextInput > div > div {
        border: 2px solid #a855f7 !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus, 
    .stTextInput input:active,
    .stTextInput > div:focus-within {
        border-color: #a855f7 !important;
        box-shadow: 0 0 8px rgba(168, 85, 247, 0.4) !important;
        outline: none !important;
    }
/* Hide "Press Enter to Apply" tooltip */
    [data-testid="InputInstructions"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)
# Setup connections
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password = os.getenv("MYSQL_PASSWORD"),
    database="real_world_project"
)

from sqlalchemy import create_engine, inspect

from urllib.parse import quote_plus

MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
encoded_password = quote_plus(MYSQL_PASSWORD)
engine = create_engine(f"mysql+mysqlconnector://root:{encoded_password}@localhost/real_world_project")

def get_all_tables():
    """List all tables currently in the database"""
    inspector = inspect(engine)
    return inspector.get_table_names()

def get_dynamic_schema(table_name):
    """Read a table's columns and sample categorical values automatically"""
    inspector = inspect(engine)
    columns_info = inspector.get_columns(table_name)
    column_names = [col["name"] for col in columns_info]
    
    schema_text = f"Table name: {table_name}\nColumns: {', '.join(column_names)}\n"
    
    # Auto-detect categorical/text columns (likely low-cardinality) to fetch sample values
    cursor = db_connection.cursor()
    categorical_info = ""
    for col in columns_info:
        col_name = col["name"]
        col_type = str(col["type"]).upper()
        if "VARCHAR" in col_type or "TEXT" in col_type or "CHAR" in col_type:
            cursor.execute(f"SELECT DISTINCT `{col_name}` FROM `{table_name}` LIMIT 8")
            values = [str(row[0]) for row in cursor.fetchall()]
            if len(values) <= 8:  # only show if genuinely categorical (few unique values)
                categorical_info += f"- {col_name} column contains these exact values: {values}\n"
    cursor.close()
    
    if categorical_info:
        schema_text += "\nIMPORTANT - Exact values in categorical columns:\n" + categorical_info
    
    return schema_text

# ===== Dataset Selector (Sidebar) =====
st.sidebar.header("📁 Dataset")
all_tables = get_all_tables()
selected_table = st.sidebar.selectbox("Choose dataset to query:", all_tables, 
                                        index=all_tables.index("orders") if "orders" in all_tables else 0)

st.sidebar.markdown("---")
st.sidebar.subheader("🗂️ Upload Dataset")
uploaded_file = st.sidebar.file_uploader("Upload a file", type=["csv","xlsx","xls","json","tsv"])

if uploaded_file is not None:
    file_extension = uploaded_file.name.split(".")[-1].lower()

    if file_extension == "csv":
    	new_df = pd.read_csv(uploaded_file)
    elif file_extension == "tsv":
    	new_df = pd.read_csv(uploaded_file, sep="\t")
    elif file_extension in ["xlsx", "xls"]:
    	new_df = pd.read_excel(uploaded_file)
    elif file_extension == "json":
    	new_df = pd.read_json(uploaded_file)
    new_df.columns = [c.strip().replace(" ", "_") for c in new_df.columns]
    
    default_table_name = uploaded_file.name.replace(".csv", "").replace(" ", "_").lower()
    table_name_input = st.sidebar.text_input("Table name for this dataset:", value=default_table_name)
    
    if st.sidebar.button("Upload to Database"):
        new_df.to_sql(table_name_input, engine, if_exists="replace", index=False)
        st.sidebar.success(f"✅ '{table_name_input}' uploaded! {len(new_df)} rows. Refresh to select it.")

st.sidebar.markdown("---")
st.sidebar.subheader("🗑️ Delete a Dataset")
deletable_tables = [t for t in all_tables if t != "orders"]  # protect the main table
if deletable_tables:
    table_to_delete = st.sidebar.selectbox("Select dataset to delete:", deletable_tables)
    if st.sidebar.button("Delete this dataset", type="secondary"):
        cursor_del = db_connection.cursor()
        cursor_del.execute(f"DROP TABLE IF EXISTS `{table_to_delete}`")
        db_connection.commit()
        cursor_del.close()
        st.sidebar.success(f"✅ '{table_to_delete}' deleted! Refresh to update the list.")
else:
    st.sidebar.info("No extra datasets to delete.")

# Get schema for whichever table is currently selected
full_schema = get_dynamic_schema(selected_table)

def format_number(value, question, sql_query=""):
    """Format number based on question type AND detect currency from SQL/column name"""
    value = float(value)
    question_lower = question.lower()
    sql_lower = sql_query.lower()
    
    percentage_keywords = ["margin", "percentage", "percent", "%", "rate", "ratio"]
    is_percentage = any(keyword in question_lower for keyword in percentage_keywords) or "%" in sql_lower or "percentage" in sql_lower
    
    count_keywords = ["how many", "count", "number of"]
    is_count = any(keyword in question_lower for keyword in count_keywords)
    
    rating_keywords = ["rating", "average rating"]
    is_rating = any(keyword in question_lower for keyword in rating_keywords)
    
    money_keywords = ["sales", "profit", "price", "revenue", "discount", "amount", "salary", "cost", "income"]
    is_money = any(keyword in question_lower for keyword in money_keywords)
    
    # Detect currency symbol from SQL query column names
    if "usd" in sql_lower or "dollar" in sql_lower:
        currency_symbol = "$"
        use_indian_format = False
    elif "eur" in sql_lower:
        currency_symbol = "€"
        use_indian_format = False
    elif "gbp" in sql_lower:
        currency_symbol = "£"
        use_indian_format = False
    else:
        currency_symbol = "₹"
        use_indian_format = True  # Cr/L/K format only makes sense for INR context
    
    if is_percentage:
        return f"{value:.2f}%"
    elif is_count:
        return f"{int(value)}"
    elif is_rating:
        return f"{value:.1f}"
    elif is_money:
        if use_indian_format:
            if value >= 10000000:
                return f"{currency_symbol}{value/10000000:.2f} Cr"
            elif value >= 100000:
                return f"{currency_symbol}{value/100000:.2f} L"
            elif value >= 1000:
                return f"{currency_symbol}{value/1000:.2f} K"
            else:
                return f"{currency_symbol}{value:.2f}"
        else:
            # International format: use K/M/B instead of L/Cr
            if value >= 1000000000:
                return f"{currency_symbol}{value/1000000000:.2f}B"
            elif value >= 1000000:
                return f"{currency_symbol}{value/1000000:.2f}M"
            elif value >= 1000:
                return f"{currency_symbol}{value/1000:.2f}K"
            else:
                return f"{currency_symbol}{value:.2f}"
    else:
        return f"{value:.2f}"

def ask_question(user_question,schema_text):
    prompt = f"""
You are a MySQL expert. Convert the following question into a valid MySQL query.
{schema_text}

IMPORTANT: Always use the EXACT values shown above for categorical columns (e.g., if Returned column shows ['Yes', 'No'], use WHERE Returned = 'Yes', never WHERE Returned = 1).

Question: {user_question}

Return ONLY the SQL query, nothing else. No explanation, no markdown, just the raw SQL query.
"""
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = groq_client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "user", "content": prompt}]
            )
            break
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(3)
            else:
                return None, None
    
    sql_query = response.choices[0].message.content.strip()
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
    
    cursor = db_connection.cursor()
    cursor.execute(sql_query)
    results = cursor.fetchall()
    cursor.close()
    
    return sql_query, results

import pandas as pd

import pandas as pd

# ===== STREAMLIT UI =====
st.title("🔍 AI-Powered Data Query Chatbot")
st.write("Ask questions about your data in plain English!")

user_question = st.text_input("Ask your question:", placeholder="e.g., What is the total sales?")

# Use session_state to remember the answer across button clicks
if "last_answer" not in st.session_state:
    st.session_state.last_answer = None
    st.session_state.last_question = None
    st.session_state.last_sql = None

if st.button("Ask"):
    if user_question:
               
        with st.spinner("Thinking..."):
            sql_query, answer = ask_question(user_question, full_schema)
        
        st.session_state.last_answer = answer
        st.session_state.last_question = user_question
        st.session_state.last_sql = sql_query
    else:
        st.warning("Please enter a question!")

# Display the answer (if available)
if st.session_state.last_answer is not None:
    answer = st.session_state.last_answer
    question = st.session_state.last_question
    sql_query = st.session_state.last_sql
    
    st.code(sql_query, language="sql")
    
    # Single value answer
    if len(answer) == 1 and len(answer[0]) == 1:
        value = answer[0][0]
        
        # Extract clean metric name from SQL alias (e.g., "AS average_revenue" -> "Average Revenue")
        alias_match = re.search(r'AS\s+`?(\w+)`?', sql_query, re.IGNORECASE)
        if alias_match:
            metric_name = alias_match.group(1).replace("_", " ").title()
        else:
            metric_name = "Result"
        
        if isinstance(value, (int, float, Decimal)):
            # Check if the column itself already represents Crores/Lakhs
            sql_lower = sql_query.lower()
            if "crore" in sql_lower:
                formatted = f"₹{float(value):.2f} Cr"
            elif "lakh" in sql_lower or "lac" in sql_lower:
                formatted = f"₹{float(value):.2f} L"
            else:
                formatted = format_number(value, question, sql_query)
            st.success(f"**{metric_name}**\n\n### {formatted}")
        else:
            st.success(f"**{metric_name}**\n\n### {value}")
    
   	# Multiple rows -> show button first
    else:
        if st.button("📊 View Analysis"):
            # Check if data is chart-suitable (exactly 2 columns: label + number)
            is_chartable = len(answer[0]) == 2 and isinstance(answer[0][1], (int, float, Decimal))
            
            if not is_chartable:
                st.warning("This result has multiple columns and isn't suitable for a chart. Showing as a table instead.")
                st.dataframe(pd.DataFrame(answer))
            else:
                def clean_label(val):
                    s = str(val)
                    if s.endswith(".0"):
                        return s[:-2]
                    return s
                
                labels = [clean_label(row[0]) for row in answer]
                values = [float(row[1]) for row in answer]
                
                import datetime
                from collections import defaultdict
                
                def parse_date_flexible(label):
                    """Try multiple date formats, return a datetime object or None"""
                    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y-%m-%d %H:%M:%S"):
                        try:
                            return datetime.datetime.strptime(label, fmt)
                        except:
                            continue
                    return None
                
                parsed_dates = [parse_date_flexible(l) for l in labels]
                is_date_based = all(d is not None for d in parsed_dates)
                
                if is_date_based:
                    monthly_totals = defaultdict(float)
                    for date_obj, value in zip(parsed_dates, values):
                        month_key = (date_obj.year, date_obj.month)
                        monthly_totals[month_key] += value
                    
                    sorted_months = sorted(monthly_totals.keys())
                    display_labels = [datetime.date(y, m, 1).strftime("%b %Y") for (y, m) in sorted_months]
                    values = [monthly_totals[key] for key in sorted_months]
                    labels = display_labels
                else:
                    display_labels = labels
                
                df = pd.DataFrame({"Category": display_labels, "Value": values})
                df["Category"] = pd.Categorical(df["Category"], categories=display_labels, ordered=True)
                chart_type = choose_chart_type(labels, values, question)
                
                if chart_type == "line":
                    st.line_chart(df.set_index("Category"), color="#7c3aed", use_container_width=True)
                elif chart_type == "pie":
                    import matplotlib.pyplot as plt
                    fig, ax = plt.subplots()
                    ax.pie(values, labels=display_labels, autopct='%1.1f%%', startangle=90)
                    ax.axis('equal')
                    st.pyplot(fig)
                elif chart_type == "horizontal_bar":
                    st.bar_chart(df.set_index("Category"), horizontal=True, color="#a855f7", use_container_width=True)
                else:
                    import re
                    alias_match = re.search(r'AS\s+(\w+)', sql_query, re.IGNORECASE)
                    if alias_match:
                        y_axis_label = alias_match.group(1).replace("_", " ").title()
                    else:
                        y_axis_label = "Value"
                    
                    chart = alt.Chart(df).mark_bar(color="#a855f7").encode(
                        x=alt.X("Category", sort=None, axis=alt.Axis(labelAngle=0), title="Category"),
                        y=alt.Y("Value", title=y_axis_label)
                    ).properties(height=400)
                    st.altair_chart(chart, use_container_width=True)
                
                # ===== Calculate EXACT facts in code (no LLM guessing) =====
                max_idx = values.index(max(values))
                min_idx = values.index(min(values))
                max_label, max_value = display_labels[max_idx], values[max_idx]
                min_label, min_value = display_labels[min_idx], values[min_idx]
                avg_value = sum(values) / len(values)
                
                first_label, first_value = display_labels[0], values[0]
                last_label, last_value = display_labels[-1], values[-1]
                trend_direction = "increased" if last_value > first_value else "decreased"
                
                period_word = "monthly" if is_date_based else "value"
                
                max_value_fmt = format_number(max_value, question, sql_query)
                min_value_fmt = format_number(min_value, question, sql_query)
                avg_value_fmt = format_number(avg_value, question, sql_query)
                first_value_fmt = format_number(first_value, question, sql_query)
                last_value_fmt = format_number(last_value, question, sql_query)
                
                exact_facts = f"""
- Highest {period_word}: {max_label} with {max_value_fmt}
- Lowest {period_word}: {min_label} with {min_value_fmt}
- Average {period_word}: {avg_value_fmt}
- First point: {first_label} = {first_value_fmt}, Last point: {last_label} = {last_value_fmt} (overall {trend_direction})
"""
                
                with st.spinner("Generating insights..."):
                    insight_prompt = f"""
You are explaining data to a non-technical business person for the question: "{question}"

Here are the EXACT calculated facts (do not recalculate, just explain these in simple words):
{exact_facts}

Write exactly 3 short, simple insight sentences based ONLY on the facts above. 
Do not make up any other numbers, dates, or values not listed above. Format as a numbered list.
"""
                    insight_response = groq_client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[{"role": "user", "content": insight_prompt}]
                    )
                    st.markdown("### 💡 Key Insights")
                    st.info(insight_response.choices[0].message.content)