from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import logging

logger = logging.getLogger(__name__)

def setup_telemetry(app):
    """
    Initializes OpenTelemetry distributed tracing and metrics exposure.
    Currently exports to Console, but should be swapped with OTLPSpanExporter in production.
    """
    logger.info("Setting up OpenTelemetry")
    provider = TracerProvider()
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    
    # Instrument the FastAPI app
    FastAPIInstrumentor.instrument_app(app)
