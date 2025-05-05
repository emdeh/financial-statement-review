"""
    Relative location: services/tracer.py
    Module for tracing service to monitor application performance and diagnose issues.

    This module provides a tracer class to handle tracing operations using
    OpenCensus and Azure Application Insights. It includes methods to create
    and manage tracing spans, allowing you to monitor the performance of
    different parts of your application. The tracer class integrates with
    Azure Application Insights to provide tracing capabilities, enabling you
    to track the performance of your application and diagnose issues.

    Classes:
    --------
        AppTracer: A class to handle tracing operations.
"""

from opencensus.trace import config_integration
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.tracer import Tracer as OCTTracer
    # Alias to avoid conflict with built-in tracer

class AppTracer:
    """
    A class to handle tracing operations using OpenCensus and Azure Application Insights.
    This class includes methods to create and manage tracing spans, allowing
    you to monitor the performance of different parts of your application.

    Attributes
    ----------
        tracer (OCTTracer): The OpenCensus tracer instance.
        instrumentation_key (str): The instrumentation key for Azure Application Insights.
        sampler_rate (float): The sampling rate for tracing (default is 1.0, meaning 100% of traces are sampled).

    Methods
    -------
        __init__(): Initialises the AppTracer with the given instrumentation key and sampler rate.
        span(): Creates a tracing span with the given name.
    """

    def __init__(self, instrumentation_key, sampler_rate=1.0):
        """
        Initialises the AppTracer with the given instrumentation key and sampler rate.
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

        Args:
            name (str): The name of the span.
        
        Returns:
            span (Span): The created span object.

        Raises:
            None
        """
        return self.tracer.span(name=name)
