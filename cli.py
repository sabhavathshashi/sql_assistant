import sys
from tabulate import tabulate  # pip install tabulate (optional, falls back if missing)
from database import get_schema_info, execute_read_only_query
from agent import generate_sql_and_explain, is_safe_sql

def run_cli():
    print("==================================================")
    print(" 🤖 AI SQL Assistant for MySQL (Read-Only Mode)")
    print("==================================================")
    
    print("\n[+] Inspecting Database Schema...")
    try:
        schema = get_schema_info()
        print(schema)
    except Exception as e:
        print(f"❌ Failed to connect to MySQL database: {e}")
        sys.exit(1)
        
    print("\nReady! Ask any question about your database (Type 'exit' or 'q' to quit).\n")
    
    while True:
        try:
            user_input = input("\n💬 Enter query: ").strip()
            if user_input.lower() in ["exit", "q"]:
                print("Goodbye!")
                break
                
            if not user_input:
                continue
                
            print("\n⚙️  Generating SQL with Groq...")
            ai_out = generate_sql_and_explain(user_input, schema)
            sql_query = ai_out["sql"]
            explanation = ai_out["explanation"]
            
            print(f"\n📝 Generated SQL:\n   {sql_query}")
            print(f"\n💡 Explanation:\n   {explanation}")
            
            # Validation Step
            is_safe, reason = is_safe_sql(sql_query)
            if not is_safe:
                print(f"\n🛑 SAFETY BLOCKED: {reason}")
                continue
                
            # Execution
            print("\n🚀 Executing Query...")
            results = execute_read_only_query(sql_query)
            
            print(f"\n📊 Results ({len(results)} rows returned):\n")
            if results:
                # Pretty print using tabulate if available
                try:
                    from tabulate import tabulate
                    print(tabulate(results, headers="keys", tablefmt="grid"))
                except ImportError:
                    print(results)
            else:
                print("   [No data returned]")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    run_cli()
