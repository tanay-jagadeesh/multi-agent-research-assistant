from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_community.agent_toolkits.load_tools import load_tools

load_dotenv()

prompt = "What is the current U.S. president's age to the power of 2?"

llm = ChatOpenAI(temperature=0.9, model='gpt-4')

tools = load_tools(['wikipedia', "llm-math"], llm=llm)

# Create agent with the new API
agent = create_agent(llm, tools, debug=False)

inputs = {"messages": [{"role": "user", "content": prompt}]}
result = agent.invoke(inputs)

final_message = result['messages'][-1]
print(final_message.content)  
