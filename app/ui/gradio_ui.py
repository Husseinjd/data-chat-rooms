from typing import Any, Dict, List

import gradio as gr
from langchain.agents import tool

from app.agent.agent import AgentSetup
from app.database.connections import DatabaseConnection
from app.database.functions import DatabaseFunctions
from app.utils import ResponseFormatter
from langchain_openai import ChatOpenAI
from app.config import OPENAI_API_KEY
from langchain_ollama import ChatOllama
from app.config import EXAMPLE_QUERIES
engine = None

#############
# TOOLS
#############
import logging

logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
logger = logging.getLogger(__name__)
@tool
def get_db_functions_agent_tool() -> List[Dict[str, Any]]:
    """
    Retrieves all functions and their descriptions from the connected PostgreSQL database.

    Returns:
    list of dict: Each dict contains the function name, code, and description
    """
    try:
        functions = DatabaseFunctions(engine).get_all_functions()
        formatted_functions = []
        for func in functions:
            formatted_functions.append(
                {
                    "name": func["function_name"],
                    "description": func["description"] or "No description available.",
                    "code": func["function_code"],
                }
            )
        return formatted_functions
    except Exception as e:
        return [{"error": f"Error retrieving database functions: {str(e)}"}]


###############
# Interface
###############


class GradioInterface:
    def __init__(self):
        self.db_connection = DatabaseConnection()
        self.db_functions = None
        self.agent_setup = None
        self.example_queries = EXAMPLE_QUERIES

    def create_interface(self):
        with gr.Blocks(fill_height=True) as demo:
            gr.Markdown("# Chat with Trusted SQL Agent")

            with gr.Tabs():
                with gr.Tab("Database Connection"):
                    self._create_connection_tab()

                with gr.Tab("Database Functions"):
                    self._create_functions_tab()
                    
                with gr.Tab("Example Queries"):
                    self._create_example_queries_tab()                    

                with gr.Tab("Chat with AI"):
                    self._create_chat_tab()
        
        return demo

    def _create_connection_tab(self):
        gr.Markdown("## Database Connection")
        username_input = gr.Textbox(label="Username")
        password_input = gr.Textbox(label="Password", type="password")
        db_name_input = gr.Textbox(label="Database Name")
        connect_button = gr.Button("Connect to Database")
        connection_status = gr.Textbox(label="Connection Status")

        connect_button.click(
            self._handle_connection,
            inputs=[username_input, password_input, db_name_input],
            outputs=[connection_status],
        )

    def _create_example_queries_tab(self):
        gr.Markdown("## Example Queries")
        query_input = gr.Textbox(label="Enter an example query")
        description_input = gr.Textbox(label="Enter query description")
        add_query_button = gr.Button("Add Query")
        query_status = gr.Textbox(label="Query Status")
        
        delete_query_input = gr.Textbox(label="Enter query description to delete")
        delete_query_button = gr.Button("Delete Query")
        delete_status = gr.Textbox(label="Delete Status")
        
        refresh_button = gr.Button("Refresh Queries")
        self.example_queries_list = gr.HTML()

        add_query_button.click(
            self._handle_add_example_query,
            inputs=[query_input, description_input],
            outputs=[query_status, self.example_queries_list, query_input, description_input],
        )
        
        delete_query_button.click(
            self._handle_delete_example_query,
            inputs=[delete_query_input],
            outputs=[delete_status, self.example_queries_list, delete_query_input],
        )
        
        refresh_button.click(
            self._handle_refresh_example_queries,
            outputs=[self.example_queries_list],
        )

    def _format_example_queries(self):
        formatted_queries = ""
        for i, query in enumerate(self.example_queries):
            formatted_queries += f"""
            <div style='margin-bottom: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 5px;'>
                <h3 style='margin: 0; color: #333;'>{query['description']}</h3>
                <details>
                    <summary>View Query</summary>
                    <pre style='background-color: #f5f5f5; padding: 5px; border-radius: 3px; white-space: pre-wrap; word-wrap: break-word;'>{query['query']}</pre>
                </details>
            </div>
            """
        return formatted_queries

    def _handle_add_example_query(self, query, description):
        try:
            self.example_queries.append({"query": query, "description": description})
            return (
                f"Query added successfully!",
                self._format_example_queries(),
                "",
                "",
            )
        except Exception as e:
            return f"Error adding query: {str(e)}", self._format_example_queries(), query, description

    def _handle_delete_example_query(self, description):
        try:
            self.example_queries = [q for q in self.example_queries if q['description'] != description]
            return (
                f"Query with description '{description}' deleted successfully!",
                self._format_example_queries(),
                "",
            )
        except Exception as e:
            return f"Error deleting query: {str(e)}", self._format_example_queries(), description

    def _handle_refresh_example_queries(self):
        return self._format_example_queries()

    def _create_functions_tab(self):
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## Add New Function")
                new_function_name = gr.Textbox(label="Function Name")
                new_function_code = gr.Textbox(label="Function SQL Code", lines=5)
                new_function_description = gr.Textbox(label="Function Description")
                add_function_button = gr.Button("Add Function")
                add_function_status = gr.Textbox(label="Add Function Status")

                gr.Markdown("## Delete Function")
                delete_function_name = gr.Textbox(label="Function Name to Delete")
                delete_function_button = gr.Button("Delete Function")
                delete_function_status = gr.Textbox(label="Delete Function Status")

            with gr.Column(scale=2):
                gr.Markdown("## Available Functions")
                refresh_button = gr.Button('Refresh')
                self.functions_list = gr.HTML()

        add_function_button.click(
            self._handle_add_function,
            inputs=[new_function_name, new_function_code, new_function_description],
            outputs=[
                add_function_status,
                self.functions_list,
                new_function_name,
                new_function_code,
                new_function_description,
            ],
        )
        delete_function_button.click(
            self._handle_delete_function,
            inputs=[delete_function_name],
            outputs=[delete_function_status, self.functions_list, delete_function_name],
        )
        
        refresh_button.click(
            self._handle_refresh_functions,
            outputs=[self.functions_list],
        )
        

    def _create_chat_tab(self):
        gr.Markdown("## Chat with AI Agent")
        
        llm_choices = ["gpt-4o-mini", "llama3.1"]
        llm_dropdown = gr.Dropdown(choices=llm_choices, label="Select LLM", value="gpt-4o-mini")
        
        chatbot = gr.Chatbot(height='60vh')
        msg = gr.Textbox(label="Enter your message")
        clear = gr.Button("Clear")

        def handle_llm_selection(choice):
            if choice == "gpt-4o-mini":
                new_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=OPENAI_API_KEY)
            else:
                new_llm = ChatOllama(model="llama3.1",temperature=0)
            
            if self.agent_setup:
                self.agent_setup.update_llm(new_llm)
            
            return f"Selected {choice}"

        llm_dropdown.change(handle_llm_selection, inputs=[llm_dropdown], outputs=[gr.Textbox(label="LLM Status")])
        msg.submit(self._handle_chat, inputs=[msg, chatbot], outputs=[msg, chatbot])
        clear.click(lambda: None, None, chatbot, queue=False)

    def _handle_refresh_functions(self):
        self.db_functions = DatabaseFunctions(engine)
        return ResponseFormatter.format_functions(self.db_functions.get_all_functions())

    def _handle_connection(self, username, password, db_name):
        global engine

        try:
            engine = self.db_connection.connect(username, password, db_name)
            
            tools = [get_db_functions_agent_tool]
            self.agent_setup = AgentSetup(engine, tools=tools)
            self.agent_setup.setup()

            return "Connection successful!", 

        except Exception as e:
            return f"Connection failed: {str(e)}", ""

    def _handle_chat(self, message, history):
        if not self.agent_setup:
            return "Please connect to the database first.", history
        
        try:
            agent = self.agent_setup.get_agent()
            
            # Add example queries to the context
            context = "Example queries:\n"
            for query in self.example_queries:
                context += f"Query: {query['query']}\nDescription: {query['description']}\n\n"
            
            # Combine the context with the user's message
            full_message = f"{context}\nUser query: {message}"
                        
            events = agent.stream(
                {"messages": [("user", full_message)]},
                stream_mode="values",
            )
            response = ""
            for event in events:
                response = event["messages"][-1].content
                logger.info(event["messages"][-1].pretty_print())

            formatted_response = ResponseFormatter.format_agent_response(response)
            history.append((message, formatted_response))
            return "", history
        except Exception as e:
            return f"Error: {str(e)}", history
    
    def _handle_add_example_query(self, query, description):
        try:
            self.example_queries.append({"query": query, "description": description})
            return (
                f"Query added successfully!",
                self._format_example_queries(),
                "",
                "",
            )
        except Exception as e:
            return f"Error adding query: {str(e)}", "", query, description        

    def _handle_add_function(self, name, code, description):
        try:
            self.db_functions.add_function(name, code, description)
            functions = self.db_functions.get_all_functions()
            return (
                f"Function '{name}' added successfully!",
                ResponseFormatter.format_functions(functions),
                "",
                "",
                "",
            )
        except Exception as e:
            return f"Error adding function: {str(e)}", "", name, code, description

    def _handle_delete_function(self, name):
        try:
            self.db_functions.delete_function(name)
            functions = self.db_functions.get_all_functions()
            return (
                f"Function '{name}' deleted successfully!",
                ResponseFormatter.format_functions(functions),
                "",
            )
        except Exception as e:
            return f"Error deleting function: {str(e)}", "", name