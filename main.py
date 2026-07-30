from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import get_schema_info, execute_read_only_query
from agent import generate_sql_and_explain, is_safe_sql

app = FastAPI(title="AI SQL Assistant")

@app.get("/")
def root():
    return {
        "message": "AI SQL Assistant API is running",
        "routes": ["/schema", "/query", "/docs"]
    }

class QueryRequest(BaseModel):
    prompt: str

class QueryResponse(BaseModel):
    sql: str
    explanation: str
    data: list

@app.get("/schema")
def read_schema():
    return {"schema": get_schema_info()}

@app.post("/query", response_model=QueryResponse)
def handle_query(req: QueryRequest):
    schema = get_schema_info()
    
    # Generate SQL
    ai_output = generate_sql_and_explain(req.prompt, schema)
    sql_query = ai_output["sql"]
    explanation = ai_output["explanation"]
    
    # Validate SQL Safety
    is_safe, reason = is_safe_sql(sql_query)
    if not is_safe:
        raise HTTPException(status_code=400, detail=f"SQL Execution Blocked: {reason}")
        
    # Execute query
    try:
        results = execute_read_only_query(sql_query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Execution Error: {str(e)}")
        
    return {
        "sql": sql_query,
        "explanation": explanation,
        "data": results
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)