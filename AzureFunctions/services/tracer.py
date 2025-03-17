"""
    Relative location: services/tracer.py

    This module provides the `AppTracer` class, which is a wrapper for the OpenCensus 
    tracer configured to export trace data to Application Insights. It allows for 
    integration with the logging library and supports customisable sampling rates.
    
    Classes:
        AppTracer: A wrapper for the OpenCensus tracer configured to export data to 
                   Application Insights.

    Usage example:
        tracer = AppTracer(instrumentation_key='your_instrumentation_key')
        with tracer.span('example_span'):
            # Your traced code here
"""

from opencensus.trace import config_integration
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.tracer import Tracer as OCTTracer
    # Alias to avoid conflict with built-in tracer

class AppTracer:
    """
    A class used to create and manage tracing spans for application performance monitoring.
    The AppTracer class integrates with Azure Application Insights to provide tracing capabilities.
    It allows you to create tracing spans which can be used to monitor the performance and 
    diagnose issues within your application.

    Attributes:
        tracer (OCTTracer): The tracer object used to create and manage spans.
        
    Methods:
        __init__(instrumentation_key, sampler_rate=1.0):
            Initializes the AppTracer with the given instrumentation key and sampler rate.
        span(name):
    """

    def __init__(self, instrumentation_key, sampler_rate=1.0):
        """
        Initialises the AppTracer with the given instrumentation key and sampler rate.
        
        Parameters:
            instrumentation_key (str): Your Application Insights instrumentation key.
            sampler_rate (float): Sampling rate (1.0 means 100% of traces are sampled).
        """
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
