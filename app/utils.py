import json
import html


class ResponseFormatter:
    @staticmethod
    def format_functions(functions):
        formatted = ""
        for func in functions:
            formatted += f"""
            <div style='margin-bottom: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 5px;'>
                <h3 style='margin: 0; color: #333;'>{func['function_name']}</h3>
                <p style='margin: 5px 0; color: #666;'>{func['description'] or 'No description available.'}</p>
                <details>
                    <summary>View Function Code</summary>
                    <pre style='background-color: #f5f5f5; padding: 5px; border-radius: 3px; white-space: pre-wrap; word-wrap: break-word;'>{func['function_code']}</pre>
                </details>
            </div>
            """
        return formatted

    @staticmethod
    def format_agent_response(response):
        try:
            json_response = json.loads(response)

            is_function_approach = json_response.get("approach") == "FUNCTION"
            function_used = json_response.get("function_used")
            query_used = json_response.get("query")

            results = json_response.get("results", [])

            json_response.pop("approach", None)
            json_response.pop("function_used", None)
            json_response.pop("query", None)

            if is_function_approach:
                formatted_response = (
                    f"✅ **Trusted Response** (Using function: `{function_used}`)\n\n"
                )
            else:
                formatted_response = "**Query Response**\n\n"

            if results:
                columns = list(results[0].keys())
                table = "| " + " | ".join(columns) + " |\n"
                table += "| " + " | ".join(["---" for _ in columns]) + " |\n"
                for row in results:
                    table += (
                        "| "
                        + " | ".join(str(row.get(col, "")) for col in columns)
                        + " |\n"
                    )
                formatted_response += "**Results Table:**\n\n" + table + "\n"

            footer_note = (
                "*This response was generated using an optimized database function.*"
                if is_function_approach
                else "*This response was generated using a custom SQL query.*"
            )

            formatted_response += f"""
                
            
{footer_note}

<details>
<summary>Click to view the SQL query used</summary>
<pre><code class="language-sql">{html.escape(query_used)}</code></pre>
</details>
"""
            return formatted_response
        except json.JSONDecodeError:
            return response
