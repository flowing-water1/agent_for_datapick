import json
from langchain_openai import ChatOpenAI
import pandas as pd
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_experimental.agents.agent_toolkits import create_csv_agent


PROMPT_DATA_PICK = '''

You are a data analysis assistant, and your response content depends on the user's request.

1. For questions answered in text, respond in this format:
{"answer": "Write your answer here>"}
For example:
{"answer": "The product ID with the highest order quantity is 'MNWC3-067'."}

2. If the user needs a table, respond in this format:
{"table": {"columns": ["column1", "column2", ...], "data": [[value1, value2, ...], [value1, value2, ...], ...]}}

3. For specific extraction tasks, the following should be considered:
- Extract the relevant rows based on the names or items mentioned in the user’s query.
- Append the specified quantities or counts as an additional column.
- Ensure all strings in "columns" and "data" lists are enclosed in double quotation marks.

For example, if the user asks:
'I need to extract data from John and May, who have attended 2 and 3 conferences.'
The expected output should be:
{"table": {"columns": ["CustomerID", "Gender", "Age", "Annual Income ($)", "Spending Score (1-100)", "Profession", "Work Experience", "Family Size", "Name", "Number of attendees"], "data": [["1", "Male", "21", "35000", "81", "Engineer", "3", "3", "John", "2"], ["2", "Female", "23", "59000", "77", "Lawyer", "0", "2", "May", "3"]]}}
        
Please return all outputs as JSON strings. Please note to enclose all strings in the "columns" list and data list with double quotation marks.
For example: {"columns": ["Products", "Orders"], "data": [["32085Lip", 245], ["76439Eye", 178]}        

Finally, please answer in Chinese

Handle user requests accordingly:
'''

def dataframe_agent(openai_api_key, openai_api_base, model_name, df, query):
    model = ChatOpenAI( model = model_name,
                        openai_api_key = openai_api_key,
                        openai_api_base = openai_api_base,
                        temperature = 0)

    agent = create_pandas_dataframe_agent(llm=model,
                                          df = df,
                                          agent_executor_kwargs={"handle_parsing_errors": True},
                                          return_intermediate_steps= True,
                                          verbose= True,
                                          allow_dangerous_code= True)
    prompt = PROMPT_DATA_PICK + query
    response = agent.invoke({"input":prompt})

    return response["output"], response["intermediate_steps"]