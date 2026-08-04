import logging
import uuid
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("EKOS-AgentBuilder")

class HandlerType(str, Enum):
    """Types of handlers for agent tools."""
    HTTP_CALL = "HTTP_CALL"
    KNOWLEDGE_QUERY = "KNOWLEDGE_QUERY"
    WEB_SEARCH = "WEB_SEARCH"
    CUSTOM = "CUSTOM"

class AgentToolDefinition(BaseModel):
    """Definition of a tool available to agents."""
    tool_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    handler_type: HandlerType
    parameters_schema: Dict[str, Any] = Field(default_factory=dict)
    endpoint_url: Optional[str] = None

class AgentDefinition(BaseModel):
    """Definition of a custom agent."""
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    persona: str
    system_prompt_template_id: Optional[str] = None
    knowledge_source_ids: List[str] = Field(default_factory=list)
    enabled_tools: List[str] = Field(default_factory=list)
    llm_provider_override: Optional[str] = None
    llm_model_override: Optional[str] = None
    tenant_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

class AgentExecutionResult(BaseModel):
    """Result of an agent execution."""
    agent_id: str
    query: str
    response: str
    tools_used: List[str] = Field(default_factory=list)
    sources_consulted: List[str] = Field(default_factory=list)
    execution_time_ms: int

class AgentBuilderService:
    """Service for building and executing custom agents."""
    
    def __init__(self):
        """Initialize with default tools and in-memory storage."""
        self._agents: Dict[str, AgentDefinition] = {}
        self._tools: Dict[str, AgentToolDefinition] = {}
        
        logger.info("Initializing AgentBuilderService with built-in tools.")
        self.register_tool(AgentToolDefinition(
            name="knowledge_query",
            handler_type=HandlerType.KNOWLEDGE_QUERY,
            description="Query the DocSphere knowledge graph",
            parameters_schema={"type": "object", "properties": {"query": {"type": "string"}}}
        ))
        self.register_tool(AgentToolDefinition(
            name="web_search",
            handler_type=HandlerType.WEB_SEARCH,
            description="Search the web for information",
            parameters_schema={"type": "object", "properties": {"query": {"type": "string"}}}
        ))
        self.register_tool(AgentToolDefinition(
            name="api_call",
            handler_type=HandlerType.HTTP_CALL,
            description="Make an HTTP API call",
            parameters_schema={"type": "object", "properties": {"url": {"type": "string"}}}
        ))

    def create_agent(self, definition: AgentDefinition) -> AgentDefinition:
        """Create a new agent definition."""
        self._agents[definition.agent_id] = definition
        logger.info(f"Created agent: {definition.agent_id}")
        return definition

    def get_agent(self, agent_id: str) -> Optional[AgentDefinition]:
        """Retrieve an agent by ID."""
        return self._agents.get(agent_id)

    def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> Optional[AgentDefinition]:
        """Update an existing agent definition."""
        if agent_id not in self._agents:
            return None
        
        agent = self._agents[agent_id]
        agent_data = agent.model_dump()
        agent_data.update(updates)
        
        updated_agent = AgentDefinition(**agent_data)
        self._agents[agent_id] = updated_agent
        logger.info(f"Updated agent: {agent_id}")
        return updated_agent

    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent definition."""
        if agent_id in self._agents:
            del self._agents[agent_id]
            logger.info(f"Deleted agent: {agent_id}")
            return True
        return False

    def list_agents(self, tenant_id: str) -> List[AgentDefinition]:
        """List all agents for a tenant."""
        return [a for a in self._agents.values() if a.tenant_id == tenant_id]

    def register_tool(self, tool: AgentToolDefinition) -> AgentToolDefinition:
        """Register a new tool for agents to use."""
        self._tools[tool.tool_id] = tool
        logger.info(f"Registered tool: {tool.name} ({tool.tool_id})")
        return tool

    def list_tools(self) -> List[AgentToolDefinition]:
        """List all available tools."""
        return list(self._tools.values())

    async def execute_agent(self, agent_id: str, query: str, context: Optional[Dict[str, Any]] = None) -> AgentExecutionResult:
        """Execute an agent with a query."""
        start_time = time.time()
        agent = self.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found.")
            
        if not agent.is_active:
            raise ValueError(f"Agent {agent_id} is inactive.")

        logger.info(f"Executing agent {agent_id} with query: {query}")
        
        # Production: Integrate with LLM Gateway and real tools
        # Simulated execution for placeholder
        tools_used = [tool_id for tool_id in agent.enabled_tools if tool_id in self._tools][:1]
        sources_consulted = agent.knowledge_source_ids[:2]
        
        execution_time_ms = int((time.time() - start_time) * 1000)
        response = f"Simulated response from {agent.name} for query: {query}"
        
        return AgentExecutionResult(
            agent_id=agent_id,
            query=query,
            response=response,
            tools_used=tools_used,
            sources_consulted=sources_consulted,
            execution_time_ms=execution_time_ms
        )
