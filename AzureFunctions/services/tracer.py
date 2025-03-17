"""
    services/tracer.py
    Module to set up and configure OpenCensus tracing for Application Insights.
"""

from opencensus.trace import config_integration
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.tracer import Tracer as OCTTracer # Alias to avoid conflict with built-in tracer

class AppTracer:
    """
    AppTracer is a wrapper for the OpenCensus tracer configured to export data to Application Insights.
    """

    def __init__(self, instrumentation_key, sampler_rate=1.0):
        """
        Initialises the AppTracer with the given instrumentation key and sampler rate.
        
        Parameters:
            instrumentation_key (str): Your Application Insights instrumentation key.
            sampler_rate (float): Sampling rate (1.0 means 100% of traces are sampled).
        """
        # Enable integration with the logging library so that log records can include trace information.
        config_integration.trace_integrations(['logging'])

        self.tracer = OCTTracer(
            sampler=ProbabilitySampler(sampler_rate),
            exporter=AzureExporter(
                connection_string=f'InstrumentationKey={instrumentation_key}'
            )
        )

    def span(self, name):
        """
        Creates a tracing span with the given name.
        
        Parameters:
            name (str): The name of the tracing span.
            
        Returns:
            A context manager representing the span.
        """
        return self.tracer.span(name=name)
