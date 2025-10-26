from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import manager
from app.websocket.types import MessageType, WebSocketMessage
from app.agents.config import get_agent_config
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/voice-agent/{agent_id}")
async def voice_agent_endpoint(websocket: WebSocket, agent_id: str):
    """
    Main WebSocket endpoint for voice agent interaction.

    Flow:
    1. Validate agent_id
    2. Accept connection
    3. Send connection confirmation
    4. Listen for messages
    5. Handle messages based on type
    6. Cleanup on disconnect

    Test Cases:
    - Should reject invalid agent_id
    - Should accept valid connection
    - Should send connection_established message
    - Should handle audio_chunk messages
    - Should handle end_session messages
    - Should cleanup on disconnect
    - Should handle WebSocketDisconnect gracefully
    - Should handle errors and send error messages
    """

    # Validate agent
    agent_config = get_agent_config(agent_id)
    if not agent_config:
        await websocket.close(code=1003, reason="Invalid agent ID")
        return

    # Accept connection
    session_id = await manager.connect(websocket, agent_id)

    # Send connection confirmation
    await manager.send_message(session_id, {
        'type': MessageType.CONNECTION_ESTABLISHED,
        'session_id': session_id,
        'agent': agent_config.name,
    })

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message = WebSocketMessage(**data)

            # Route message
            if message.type == MessageType.AUDIO_CHUNK:
                # TODO: Implement handle_audio_chunk
                await manager.send_message(session_id, {
                    'type': MessageType.STATUS_UPDATE,
                    'status': 'processing'
                })

            elif message.type == MessageType.END_SESSION:
                break

            else:
                # Unknown message type
                logger.warning(f"Unknown message type: {message.type}")
                await manager.send_message(session_id, {
                    'type': MessageType.ERROR,
                    'message': f'Unknown message type: {message.type}'
                })

    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {session_id}")

    except Exception as e:
        logger.error(f"Error in WebSocket handler: {e}", exc_info=True)
        await manager.send_message(session_id, {
            'type': MessageType.ERROR,
            'message': str(e)
        })

    finally:
        # Cleanup
        manager.disconnect(session_id)
        logger.info(f"Session ended: {session_id}")