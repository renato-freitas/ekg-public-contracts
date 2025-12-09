from langgraph.graph import StateGraph

workflow_publation   = StateGraph()
workflow_integration = StateGraph()
workflow_fusion      = StateGraph()


team_publation   = workflow_publation.compile()
team_integration = workflow_integration.compile()
team_fusion      = workflow_fusion.compile()

# 
# Agents
#