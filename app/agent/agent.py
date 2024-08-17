from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain import hub
from langchain_core.prompts.prompt import PromptTemplate
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from app.config import OPENAI_API_KEY


class AgentSetup:
    def __init__(self, engine, llm = None, tools=[]):
        self.engine = engine
        self.llm = llm or ChatOpenAI(
            model="gpt-4o-mini", temperature=0, api_key=OPENAI_API_KEY
        )
        self.tools = tools
        self.agent_executor = None
        self.toolkit = None

    def setup(self):
        db = SQLDatabase(self.engine)
        self.toolkit = SQLDatabaseToolkit(db=db, llm=self.llm)

        prompt_template = hub.pull("langchain-ai/sql-agent-system-prompt")
        function_prompt_addition = """
    You are an agent designed to interact with a SQL database.

    Given an input question, check whether the question can be answered by a function already available or create a syntactically correct {dialect} 
    query to run, then look at the results of the query and return the answer.
    Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
    You can order the results by a relevant column to return the most interesting examples in the database.
    Never query for all the columns from a specific table, only ask for the relevant columns given the question.
    You have access to tools for interacting with the database. Only use the below tools. 
    Only use the information returned by the below tools to construct your final answer.
    You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

    DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

    To start you should ALWAYS look at functions in the database and then tables to see what you can use to query.
    Do NOT skip this step. Then you should construct the right query whether you chose a function to run or build your own query.
    Those functions should always take precedence to use and execute over building your own query and running. 
    Decide correctly whether to choose the function or build your own query or return an empty result if the question does not refer to any related query on the database. 
    If you choose a function make sure to build the sql query to execute the function correctly and get the results.
    In order to execute a function run an sql like SELECT <columns> from <function_name(param)>
    At the end of the result provide information. The result should be structured in json format.
    It should include all the columns and results, in addition to the approach used with the final result with three potential values (FUNCTION or QUERY or None)
    FUNCTION if function tool is used, QUERY if own query is used to get the final result. 
    The approach result should be also included in the json, in addition to the function name used.
    Your last answer should only be a valid json and nothing else. in the following format: 
    {{
    "results": [
    {{
      "col1": val1,
      "col2": val2,
      "col3": val3,
      ...
    }}
  ],
  "approach": "FUNCTION or QUERY or NONE",
  "function_used": "<function name>",
  "query": <final using function or not used to retrieve the final results>
    }}
    """

        prompt_template = PromptTemplate(
            input_variables=["dialect", "top_k"], template=function_prompt_addition
        )

        tools =  self.toolkit.get_tools() + self.tools

        self.agent_executor = create_react_agent(
            self.llm,
            tools,
            state_modifier=prompt_template.format(dialect="POSTGRESQL", top_k=5),
        )

    def get_agent(self):
        if not self.agent_executor:
            raise ValueError("Agent not set up. Call setup() first.")
        return self.agent_executor

    def update_llm(self, new_llm):
        self.llm = new_llm
        if self.toolkit:
            self.toolkit.llm = new_llm
        self.setup()  # Re-setup the agent with the new LLM