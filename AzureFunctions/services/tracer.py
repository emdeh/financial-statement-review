"""
    services/tracer.py
    Module to set up and configure OpenCensus tracing for Application Insights.
"""

from opencensus.trace import config_integration
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.tracer import Tracer

def init_tracer(instrumentation_key, sampler_rate=1.0):
    """
    Initializes and returns an OpenCensus tracer configured to export data to Application Insights.
    
    Parameters:
        instrumentation_key (str): Your Application Insights instrumentation key.
        sampler_rate (float): Sampling rate (1.0 for 100% sampling).
    
    Returns:
        Tracer: Configured OpenCensus tracer instance.
    """
    # Enable integration with the logging library so that log records can include trace information.
    config_integration.trace_integrations(['logging'])
    
    tracer = Tracer(
        sampler=ProbabilitySampler(sampler_rate),
        exporter=AzureExporter(
            connection_string=f'InstrumentationKey={instrumentation_key}'
        )
    )
    return tracer
