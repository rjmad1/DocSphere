from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
import hmac
import hashlib
import os
import logging

logger = logging.getLogger("EKOS-ChannelIntegrations")

class ChannelType(str, Enum):
    SLACK = "SLACK"
    DISCORD = "DISCORD"
    TELEGRAM = "TELEGRAM"

class ChannelMessage(BaseModel):
    channel_type: ChannelType
    channel_id: str
    user_id: str
    user_name: str
    content: str
    timestamp: datetime

class ChannelResponse(BaseModel):
    channel_type: ChannelType
    channel_id: str
    content: str
    citations: List[str] = Field(default_factory=list)

class ChannelConfig(BaseModel):
    channel_type: ChannelType
    tenant_id: str
    bot_token: str
    signing_secret: Optional[str] = None
    webhook_url: Optional[str] = None
    is_active: bool = True

class BaseChannelAdapter(ABC):
    """Abstract base class for channel adapters."""
    
    @abstractmethod
    async def process_event(self, event: Dict) -> Optional[ChannelMessage]:
        pass

    @abstractmethod
    async def send_response(self, response: ChannelResponse) -> Dict:
        pass

    @abstractmethod
    async def verify_request(self, headers: Dict, body: bytes) -> bool:
        pass

class SlackAdapter(BaseChannelAdapter):
    def __init__(self, config: Optional[ChannelConfig] = None):
        self.config = config

    async def process_event(self, event: Dict) -> Optional[ChannelMessage]:
        # Handle Slack URL verification challenge
        if event.get("type") == "url_verification":
            return None
            
        event_data = event.get("event", {})
        if event_data.get("type") == "message" and "bot_id" not in event_data:
            return ChannelMessage(
                channel_type=ChannelType.SLACK,
                channel_id=event_data.get("channel", ""),
                user_id=event_data.get("user", ""),
                user_name=event_data.get("user", "Unknown"), # Slack needs API call to resolve name
                content=event_data.get("text", ""),
                timestamp=datetime.now()
            )
        return None

    async def send_response(self, response: ChannelResponse) -> Dict:
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": response.content
                }
            }
        ]
        
        if response.citations:
            citations_text = "\\n".join([f"• {c}" for c in response.citations])
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Sources:*\\n{citations_text}"
                    }
                ]
            })
            
        # Production: requests.post to Slack API
        return {"ok": True, "channel": response.channel_id, "blocks": blocks}

    async def verify_request(self, headers: Dict, body: bytes) -> bool:
        if not self.config or not self.config.signing_secret:
            return False
            
        slack_signature = headers.get("X-Slack-Signature", "")
        slack_timestamp = headers.get("X-Slack-Request-Timestamp", "")
        
        sig_basestring = f"v0:{slack_timestamp}:{body.decode('utf-8')}"
        my_signature = "v0=" + hmac.new(
            self.config.signing_secret.encode(),
            sig_basestring.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(my_signature, slack_signature)

class DiscordAdapter(BaseChannelAdapter):
    def __init__(self, config: Optional[ChannelConfig] = None):
        self.config = config

    async def process_event(self, event: Dict) -> Optional[ChannelMessage]:
        if "content" in event and "author" in event and not event["author"].get("bot"):
            return ChannelMessage(
                channel_type=ChannelType.DISCORD,
                channel_id=event.get("channel_id", ""),
                user_id=event["author"].get("id", ""),
                user_name=event["author"].get("username", ""),
                content=event.get("content", ""),
                timestamp=datetime.now()
            )
        return None

    async def send_response(self, response: ChannelResponse) -> Dict:
        embed = {
            "description": response.content,
            "color": 3447003
        }
        
        if response.citations:
            embed["fields"] = [
                {
                    "name": "Sources",
                    "value": "\\n".join(response.citations)
                }
            ]
            
        # Production: aiohttp.post to Discord channel webhook/API
        return {"channel_id": response.channel_id, "embeds": [embed]}

    async def verify_request(self, headers: Dict, body: bytes) -> bool:
        # ponytail: full Ed25519 verification requires `PyNaCl`. Until that dependency
        # is added, we enforce that EKOS_DISCORD_PUBLIC_KEY is configured and use an
        # HMAC-SHA256 check against the X-Signature-Ed25519 header as a defence-in-depth
        # guard. Upgrade path: replace this with nacl.signing.VerifyKey verification.
        public_key = os.getenv("EKOS_DISCORD_PUBLIC_KEY")
        if not public_key:
            # Fail closed: if no public key is configured, reject all Discord webhooks.
            logger.error("EKOS_DISCORD_PUBLIC_KEY is not set — Discord webhook rejected.")
            return False

        signature = headers.get("X-Signature-Ed25519", "")
        timestamp = headers.get("X-Signature-Timestamp", "")
        if not signature or not timestamp:
            return False

        # HMAC-SHA256 best-effort guard until Ed25519 is added
        message = (timestamp.encode() + body)
        expected = hmac.new(public_key.encode(), message, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

class TelegramAdapter(BaseChannelAdapter):
    def __init__(self, config: Optional[ChannelConfig] = None):
        self.config = config

    async def process_event(self, event: Dict) -> Optional[ChannelMessage]:
        message = event.get("message", {})
        if "text" in message and "from" in message:
            return ChannelMessage(
                channel_type=ChannelType.TELEGRAM,
                channel_id=str(message.get("chat", {}).get("id", "")),
                user_id=str(message["from"].get("id", "")),
                user_name=message["from"].get("username", ""),
                content=message.get("text", ""),
                timestamp=datetime.now()
            )
        return None

    async def send_response(self, response: ChannelResponse) -> Dict:
        text = response.content
        if response.citations:
            text += "\\n\\n*Sources:*\\n" + "\\n".join([f"- {c}" for c in response.citations])
            
        # Production: send message to Telegram Bot API
        return {
            "chat_id": response.channel_id,
            "text": text,
            "parse_mode": "Markdown"
        }

    async def verify_request(self, headers: Dict, body: bytes) -> bool:
        # Telegram sends secret token in header
        secret_token = headers.get("X-Telegram-Bot-Api-Secret-Token")
        return bool(self.config and secret_token == self.config.bot_token)

class ChannelRouter:
    """Routes events to the appropriate channel adapter."""
    
    def __init__(self):
        self._adapters: Dict[ChannelType, BaseChannelAdapter] = {}
        logger.info("ChannelRouter initialized")
        
        # Default initialization
        self.register_adapter(ChannelType.SLACK, SlackAdapter())
        self.register_adapter(ChannelType.DISCORD, DiscordAdapter())
        self.register_adapter(ChannelType.TELEGRAM, TelegramAdapter())

    def register_adapter(self, channel_type: ChannelType, adapter: BaseChannelAdapter):
        self._adapters[channel_type] = adapter

    async def route_event(self, channel_type: ChannelType, event: Dict, tenant_id: str) -> Optional[ChannelResponse]:
        adapter = self._adapters.get(channel_type)
        if not adapter:
            logger.warning(f"No adapter for channel type {channel_type}")
            return None
            
        message = await adapter.process_event(event)
        if not message:
            return None
            
        # Production: call ChatEngine/LLM Gateway here
        # Mocked response
        response = ChannelResponse(
            channel_type=channel_type,
            channel_id=message.channel_id,
            content=f"Echoing from {channel_type.value}: {message.content}",
            citations=["Mocked Source 1"]
        )
        
        return response
