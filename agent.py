import os
import re
import sqlglot
from sqlglot import exp
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

FORBIDDEN_KEYWORDS = {"INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "CREATE", "GRANT", "REVOKE"}

def is_safe_sql(sql: str) -> tuple[bool, str]:
    """Validates if a query is purely read-only (SELECT queries only)."""
    clean_sql = sql.strip().strip(";").strip()
    
    # 1. Regex check for dangerous keywords
    first_word = clean_sql.split()[0].upper() if clean_sql else ""
    if first_word != "SELECT" and not clean_sql.upper().startswith("WITH"):
        return False, "Query must start with SELECT or WITH."
        
    for kw in FORBIDDEN_KEYWORDS:
        if re.search(r'\b' + kw + r'\b', clean_sql, re.IGNORECASE):
            return False, f"Forbidden keyword detected: {kw}"
            
    # 2. AST parsing validation via sqlglot
    try:
        parsed = sqlglot.parse_one(clean_sql, read="mysql")
        if not isinstance(parsed, (exp.Select, exp.Expression)):
            return False, "Parsed AST is not a SELECT statement."
    except Exception as e:
        return False, f"SQL Syntax Parsing Error: {str(e)}"
        
    return True, "Safe"

def generate_sql_and_explain(user_prompt: str, schema_info: str) -> dict:
    """Uses Gemini to translate natural language into MySQL query + explanation."""
    prompt = f"""
You are an expert MySQL database administrator.
Database Schema:
{schema_info}

User Question: "{user_prompt}"

Task:
1. Write a single, valid MySQL SELECT query to answer the user's question.
2. Provide a plain-English explanation of how the query works.

OUTPUT FORMAT (STRICT):
===SQL===
<ONLY the raw executable SQL query here, no markdown blocks, no trailing comments>
===EXPLANATION===
<Your concise explanation here>
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    text_response = response.text or ""
    
    # Extract SQL and Explanation
    sql_match = re.search(r"===SQL===\s*(.*?)\s*===EXPLANATION===", text_response, re.DOTALL)
    explanation_match = re.search(r"===EXPLANATION===\s*(.*)", text_response, re.DOTALL)
    
    if not sql_match or not explanation_match:
        # Fallback parsing
        clean_code = re.sub(r"```sql|```", "", text_response).strip()
        return {
            "sql": clean_code,
            "explanation": "Extracted query automatically."
        }
        
    sql_query = sql_match.group(1).strip()
    explanation = explanation_match.group(1).strip()
    
    return {
        "sql": sql_query,
        "explanation": explanation
    }