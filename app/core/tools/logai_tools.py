"""
Tools for intelligent log analysis using LogAI integration.

These tools provide advanced log analysis capabilities that can be selected
based on the type of analysis needed:

1. Template extraction - For understanding log patterns and standardization
2. Anomaly detection - For finding unusual behavior in logs
3. Clustering - For grouping similar log messages
4. Comprehensive analysis - For full analysis using multiple techniques
"""

from datetime import datetime
from typing import List, Optional
import pandas as pd
import numpy as np
from sklearn.metrics import silhouette_score as sk_silhouette_score
from sklearn.cluster import KMeans as SkKMeans
from pydantic_ai import RunContext

from logai.algorithms.parsing_algo.drain import Drain, DrainParams
from logai.algorithms.anomaly_detection_algo.isolation_forest import IsolationForestDetector, IsolationForestParams
from logai.preprocess.preprocessor import Preprocessor, PreprocessorConfig
from logai.information_extraction.feature_extractor import FeatureExtractor, FeatureExtractorConfig

from ..models.observability import ObservabilityContext, LogsQuery
from ..models.logai import (
    DrainConfig,
    AnomalyDetectionConfig,
    ClusteringConfig,
    LogParsingResult,
    AnomalyDetectionResult,
    ClusteringResult,
    LogAnalysisResult
)

def setup_logai_tools(agent):
    """Set up the LogAI analysis tools for the agent."""
    
    @agent.tool
    async def parse_logs_with_drain(
        ctx: RunContext[ObservabilityContext],
        logs: List[str],
        config: Optional[DrainConfig] = None
    ) -> LogParsingResult:
        """
        Extract log templates and patterns using the Drain algorithm.
        
        Use this tool when you need to:
        - Understand the different types of log messages in the system
        - Extract common patterns from log messages
        - Find parameters that vary within similar log messages
        - Standardize log formats
        - Get an overview of logging patterns
        
        Args:
            ctx: The run context
            logs: List of raw log messages to analyze
            config: Optional configuration for the Drain algorithm
                   - sim_th: Similarity threshold (default: 0.5)
                   - depth: Parse tree depth (default: 5)
                   - max_children: Max children per node (default: 100)
                   - max_clusters: Max number of clusters (default: 1000)
            
        Returns:
            LogParsingResult containing:
            - templates: List of extracted log templates
            - groups: Groups of logs matching each template
            - parameters: Variable parameters extracted from each template
        """
        if config is None:
            config = DrainConfig()
            
        drain_params = DrainParams(
            sim_th=config.sim_th,
            depth=config.depth,
            max_children=config.max_children,
            max_clusters=config.max_clusters
        )
        parser = Drain(drain_params)
        
        logs_series = pd.Series(logs)
        parser.fit(logs_series)
        parsed_results = parser.parse(logs_series)
        
        return LogParsingResult(
            templates=list(parsed_results['templates']),
            groups=list(parsed_results['groups']),
            parameters=list(parsed_results['parameters'])
        )

    @agent.tool
    async def detect_time_series_anomalies(
        ctx: RunContext[ObservabilityContext],
        logs: List[str],
        timestamps: List[datetime],
        config: Optional[AnomalyDetectionConfig] = None
    ) -> AnomalyDetectionResult:
        """
        Detect unusual patterns and anomalies in log time series data.
        
        Use this tool when you need to:
        - Find unusual spikes or drops in log frequency
        - Detect abnormal system behavior
        - Identify potential incidents or issues
        - Monitor for unexpected changes in logging patterns
        - Get early warning of system problems
        
        Args:
            ctx: The run context
            logs: Log messages to analyze
            timestamps: Corresponding timestamps for each log
            config: Optional anomaly detection configuration
                   - algorithm: Detection algorithm (default: 'isolation_forest')
                   - window_size: Analysis window in seconds (default: 60)
                   - contamination: Expected anomaly ratio (default: 0.1)
                   - params: Additional algorithm parameters
            
        Returns:
            AnomalyDetectionResult containing:
            - scores: Anomaly scores for each window
            - predictions: Binary anomaly labels (0: normal, 1: anomaly)
            - timestamps: Timestamps for predictions
            - details: Additional detection details
        """
        if config is None:
            config = AnomalyDetectionConfig(algorithm='isolation_forest')
            
        feature_config = FeatureExtractorConfig(
            group_by_time=f"{config.window_size}s",
            max_feature_len=100
        )
        feature_extractor = FeatureExtractor(feature_config)
        features = feature_extractor.convert_to_feature_vector(
            pd.Series(logs),
            timestamps=pd.Series(timestamps),
            attributes=pd.DataFrame()
        )
        
        detector_params = IsolationForestParams(
            contamination=str(config.contamination),
            **config.params
        )
        detector = IsolationForestDetector(detector_params)
        
        detector.fit(features)
        scores = detector.predict(features)
        predictions = [1 if score < 0 else 0 for score in scores]
        
        return AnomalyDetectionResult(
            scores=scores.tolist() if isinstance(scores, (pd.Series, np.ndarray)) else list(scores),
            predictions=predictions,
            timestamps=timestamps,
            details={"algorithm": "isolation_forest"}
        )

    @agent.tool  
    async def cluster_logs(
        ctx: RunContext[ObservabilityContext],
        logs: List[str],
        config: Optional[ClusteringConfig] = None
    ) -> ClusteringResult:
        """
        Group similar log messages into clusters for pattern analysis.
        
        Use this tool when you need to:
        - Find groups of related log messages
        - Identify common error patterns
        - Analyze system behavior patterns
        - Reduce log complexity by grouping
        - Get an overview of log categories
        
        Args:
            ctx: The run context
            logs: Log messages to cluster
            config: Optional clustering configuration
                   - algorithm: Clustering algorithm (default: 'kmeans')
                   - n_clusters: Number of clusters (default: 10)
                   - params: Additional algorithm parameters
            
        Returns:
            ClusteringResult containing:
            - labels: Cluster assignments for each log
            - centroids: Cluster centers (if applicable)
            - silhouette_score: Clustering quality score
            - cluster_sizes: Number of logs in each cluster
            - cluster_examples: Representative examples from each cluster
        """
        if config is None:
            config = ClusteringConfig(algorithm='kmeans', n_clusters=10)
            
        preprocessor = Preprocessor(PreprocessorConfig())
        clean_logs = preprocessor.clean_log(pd.Series(logs))
        
        feature_extractor = FeatureExtractor(FeatureExtractorConfig())
        features = feature_extractor.convert_to_feature_vector(
            clean_logs,
            timestamps=pd.Series(range(len(clean_logs))),
            attributes=pd.DataFrame()
        )
        
        n_clusters = 10 if config.n_clusters is None else config.n_clusters
        clusterer = SkKMeans(n_clusters=n_clusters, **config.params)
        
        clusterer.fit(features)
        labels = clusterer.predict(features)
        
        cluster_sizes = {}
        cluster_examples = {}
        labels_list = labels.tolist()
        for label in set(labels_list):
            indices = [i for i, l in enumerate(labels_list) if l == label]
            cluster_sizes[label] = len(indices)
            cluster_examples[label] = [logs[i] for i in indices[:3]]
            
        return ClusteringResult(
            labels=labels_list,
            centroids=clusterer.cluster_centers_.tolist() if hasattr(clusterer, 'cluster_centers_') else None,
            silhouette_score=float(sk_silhouette_score(features, labels)) if len(set(labels_list)) > 1 else 0.0,
            cluster_sizes=cluster_sizes,
            cluster_examples=cluster_examples
        )

    @agent.tool
    async def analyze_logs_comprehensive(
        ctx: RunContext[ObservabilityContext],
        query: LogsQuery
    ) -> LogAnalysisResult:
        """
        Perform comprehensive log analysis using multiple techniques.
        
        Use this tool when you need to:
        - Get a complete analysis of log patterns
        - Find both anomalies and patterns
        - Generate actionable insights
        - Get recommendations for improvement
        - Understand overall log health
        
        Args:
            ctx: The run context
            query: Query to select logs for analysis
                  - query: The log query string
                  - time_range: Optional time range
            
        Returns:
            LogAnalysisResult containing:
            - parsing: Results from template extraction
            - anomalies: Results from anomaly detection
            - clusters: Results from clustering
            - summary: Natural language summary
            - recommendations: Actionable recommendations
        """
        logs_backend = ctx.deps.backend.get_logs_backend()
        if not logs_backend:
            raise ValueError("Logs backend not available")
            
        logs_response = await logs_backend.query(query.query)
        
        logs = []
        timestamps = []
        for stream in logs_response.results:
            for value in stream.values:
                timestamps.append(value[0])
                logs.append(value[1])
                
        logs_response.logs = logs
        logs_response.timestamps = timestamps
        
        parsing_result = await parse_logs_with_drain(ctx, logs)
        anomaly_result = await detect_time_series_anomalies(ctx, logs, timestamps)
        clustering_result = await cluster_logs(ctx, logs)
        
        summary = _generate_analysis_summary(
            parsing_result,
            anomaly_result,
            clustering_result
        )
        recommendations = _generate_recommendations(
            parsing_result,
            anomaly_result,
            clustering_result
        )
        
        return LogAnalysisResult(
            parsing=parsing_result,
            anomalies=anomaly_result,
            clusters=clustering_result,
            summary=summary,
            recommendations=recommendations
        )

def _generate_analysis_summary(
    parsing: LogParsingResult,
    anomalies: AnomalyDetectionResult,
    clusters: ClusteringResult
) -> str:
    """Generate a natural language summary of the analysis results."""
    template_count = len(parsing.templates)
    anomaly_count = sum(anomalies.predictions)
    cluster_count = len(clusters.cluster_sizes)
    
    return (
        f"Analysis found {template_count} distinct log patterns. "
        f"Detected {anomaly_count} anomalous events across the time period. "
        f"Logs were grouped into {cluster_count} clusters based on similarity."
    )

def _generate_recommendations(
    parsing: LogParsingResult,
    anomalies: AnomalyDetectionResult,
    clusters: ClusteringResult
) -> List[str]:
    """Generate actionable recommendations based on the analysis."""
    recommendations = []
    
    if len(parsing.templates) > 100:
        recommendations.append(
            "Large number of distinct log patterns detected. Consider standardizing logging formats."
        )
        
    anomaly_ratio = sum(anomalies.predictions) / len(anomalies.predictions)
    if anomaly_ratio > 0.1:
        recommendations.append(
            "High rate of anomalous events detected. Investigate system stability and error handling."
        )
        
    small_clusters = sum(1 for size in clusters.cluster_sizes.values() if size < 5)
    if small_clusters > len(clusters.cluster_sizes) / 2:
        recommendations.append(
            "Many small log clusters found. Review logging practices for consistency."
        )
        
    return recommendations 