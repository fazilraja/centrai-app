from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class AgentConfig:
    """Agent configuration"""

    id: str
    name: str
    description: str
    prompt: str
    voice_id: str  # ElevenLabs voice ID
    temperature: float = 0.7
    max_tokens: int = 150


# Agent configurations
AGENTS: Dict[str, AgentConfig] = {
    'receptionist': AgentConfig(
        id='receptionist',
        name='Receptionist',
        description='Friendly receptionist for appointment scheduling',
        prompt="""You are a professional and friendly receptionist for a medical clinic.

Your responsibilities:
- Greet callers warmly
- Help schedule appointments
- Answer basic questions about clinic hours and services
- Collect patient information (name, phone, reason for visit)
- Be concise and clear in your responses

Guidelines:
- Keep responses under 2-3 sentences for natural conversation flow
- Be polite and professional
- If you don't know something, offer to transfer or take a message
- Confirm important information back to the caller""",
        voice_id='EXAVITQu4vr4xnSDxMaL',
    ),

    'sales': AgentConfig(
        id='sales',
        name='Sales Agent',
        description='Professional sales agent for product inquiries',
        prompt="""You are an experienced sales representative for a software company.

Your role:
- Understand customer needs
- Present product features and benefits
- Answer questions about pricing and plans
- Build rapport and trust
- Guide customers toward a purchase decision

Guidelines:
- Be enthusiastic but not pushy
- Listen actively and ask clarifying questions
- Provide specific, relevant information
- Keep responses concise (2-3 sentences)
- Focus on value, not just features""",
        voice_id='21m00Tcm4TlvDq8ikWAM',
    ),

    'callcenter': AgentConfig(
        id='callcenter',
        name='Call Center Agent',
        description='Customer support for technical issues',
        prompt="""You are a skilled customer support agent for a tech company.

Your mission:
- Help customers troubleshoot technical issues
- Provide step-by-step guidance
- Document issues and solutions
- Escalate complex problems when needed
- Ensure customer satisfaction

Guidelines:
- Be patient and empathetic
- Use simple, non-technical language
- Confirm understanding before moving forward
- Keep responses brief and actionable
- Stay calm under pressure""",
        voice_id='pNInz6obpgDQGcFmaJgB',
    ),
}


def get_agent_config(agent_id: str) -> Optional[AgentConfig]:
    """
    Get agent configuration by ID.

    Args:
        agent_id: Agent identifier

    Returns:
        AgentConfig or None if not found

    Test Cases:
    - Should return config for valid agent_id
    - Should return None for invalid agent_id
    """
    return AGENTS.get(agent_id)


def get_all_agents() -> Dict[str, AgentConfig]:
    """
    Get all agent configurations.

    Returns:
        Dict of all agents

    Test Cases:
    - Should return all agents
    - Should return dict with 3 agents
    """
    return AGENTS