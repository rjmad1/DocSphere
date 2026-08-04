import logging
from enum import Enum
from typing import Dict, Any, Optional

from pydantic import BaseModel, Field

from backend.services.ingestion.document_parser import DocumentParser

logger = logging.getLogger("EKOS-AudioProcessor")

class AudioFormat(str, Enum):
    MP3 = "MP3"
    WAV = "WAV"
    M4A = "M4A"
    OGG = "OGG"
    WEBM = "WEBM"

class TranscriptionRequest(BaseModel):
    file_path: str
    format: AudioFormat
    language: str = "en"
    tenant_id: str

class TranscriptionResult(BaseModel):
    file_path: str
    transcript: str
    language: str
    confidence: float
    duration_seconds: float
    word_count: int
    metadata: Dict = Field(default_factory=dict)

class VoiceInputRequest(BaseModel):
    audio_data: str  # Base64 string
    format: AudioFormat
    tenant_id: str

class VoiceInputResult(BaseModel):
    transcript: str
    confidence: float

class AudioProcessor:
    """Service for voice and audio processing."""
    
    _supported_formats = {
        AudioFormat.MP3: "audio/mpeg",
        AudioFormat.WAV: "audio/wav",
        AudioFormat.M4A: "audio/mp4",
        AudioFormat.OGG: "audio/ogg",
        AudioFormat.WEBM: "audio/webm"
    }
    
    async def transcribe(self, request: TranscriptionRequest) -> TranscriptionResult:
        """Transcribes audio file."""
        # Production: call Whisper API or local whisper model
        logger.info(f"Transcribing {request.file_path} (Format: {request.format})")
        
        if not self._validate_format(request.file_path, request.format):
            logger.warning("File extension does not match format, proceeding anyway...")
            
        duration = self._estimate_duration(request.file_path)
        simulated_transcript = "This is a simulated transcription of the audio file."
        
        return TranscriptionResult(
            file_path=request.file_path,
            transcript=simulated_transcript,
            language=request.language,
            confidence=0.95,
            duration_seconds=duration,
            word_count=len(simulated_transcript.split()),
            metadata={"source": "audio_processor"}
        )
        
    async def process_voice_input(self, request: VoiceInputRequest) -> VoiceInputResult:
        """Processes live voice input for chat."""
        # Production: call Whisper API or local whisper model on byte stream
        logger.info("Processing live voice input")
        
        return VoiceInputResult(
            transcript="Simulated voice input transcription.",
            confidence=0.92
        )
        
    def _validate_format(self, file_path: str, format: AudioFormat) -> bool:
        """Validates file extension matches format."""
        ext = file_path.split(".")[-1].upper()
        return ext == format.value
        
    def _estimate_duration(self, file_path: str) -> float:
        """Returns estimated duration."""
        # Placeholder
        return 60.0

class AudioIngestionPipeline:
    """Pipeline for ingesting audio files into knowledge base."""
    
    def __init__(self):
        self.processor = AudioProcessor()
        self.document_parser = DocumentParser()
        
    async def ingest_audio(self, file_path: str, format: AudioFormat, tenant_id: str) -> Dict:
        """Transcribes audio, then feeds transcript into document parser pipeline."""
        req = TranscriptionRequest(file_path=file_path, format=format, tenant_id=tenant_id)
        transcription_result = await self.processor.transcribe(req)
        
        # We assume DocumentParser has a parse method. Depending on real implementation,
        # it might need real IO or a specific mocked path.
        logger.info(f"Routing transcribed content from {file_path} to DocumentParser")
        parsed_chunks = self.document_parser.parse_text_content(
            document_id=f"audio-{file_path}",
            raw_text=transcription_result.transcript,
        )

        return {
            "status": "SUCCESS",
            "transcription": transcription_result.model_dump(),
            "parsed_chunks": len(parsed_chunks),
        }
