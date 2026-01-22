from agents.planner_agent import create_planner_agent
from agents.research_agent import create_research_agent

planner_agent, planner_memory = create_planner_agent()

research_agent, research_agent = create_research_agent()

question = "What is the future of Aritificial Intelligence in Healthcare?"

planner_config = {"configurable": {"thread_id": "planner-1"}}
planner_inputs = {"messages": [{"role": "user", "content": question}]}
planner_result = planner_agent.invoke(planner_inputs, planner_config)
sub_questions = planner_result['messages'][-1].content

researcher_config = {"configurable": {"thread_id": "researcher-1"}}
researcher_inputs = {"messages": [{"role": "user", "content": sub_questions}]}
researcher_result = researcher_agent.invoke(researcher_inputs, researcher_config)
findings = researcher_result['messages'][-1].content

print(findings)