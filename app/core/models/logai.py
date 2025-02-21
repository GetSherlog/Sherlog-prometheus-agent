"""
Models for LogAI integration.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field

class DrainConfig(BaseModel):
    """Configuration for Drain log parsing algorithm."""
    sim_th: float = Field(default=0.5, description="Similarity threshold")
    depth: int = Field(default=5, description="Maximum depth of the parse tree")
    max_children: int = Field(default=100, description="Maximum number of children for each node")
    max_clusters: int = Field(default=1000, description="Maximum number of clusters")

class AnomalyDetectionConfig(BaseModel):
    """Configuration for anomaly detection algorithms."""
    algorithm: str = Field(description="Algorithm name (e.g. 'isolation_forest', 'dbl', 'one_class_svm')")
    window_size: int = Field(default=60, description="Window size for time series analysis")
    contamination: float = Field(default=0.1, description="Expected proportion of anomalies")
    params: Dict[str, Any] = Field(default_factory=dict, description="Additional algorithm-specific parameters")

class ClusteringConfig(BaseModel):
    """Configuration for log clustering."""
    algorithm: str = Field(description="Clustering algorithm name (e.g. 'kmeans', 'dbscan')")
    n_clusters: Optional[int] = Field(default=None, description="Number of clusters (for algorithms like k-means)")
    params: Dict[str, Any] = Field(default_factory=dict, description="Additional algorithm-specific parameters")

class LogParsingResult(BaseModel):
    """Result from log parsing."""
    templates: List[str] = Field(description="Extracted log templates")
    groups: List[List[int]] = Field(description="Groups of log indices belonging to each template")
    parameters: List[Dict[str, List[str]]] = Field(description="Extracted parameters for each template")

class AnomalyDetectionResult(BaseModel):
    """Result from anomaly detection."""
    scores: List[float] = Field(description="Anomaly scores for each log/window")
    predictions: List[int] = Field(description="Binary predictions (0: normal, 1: anomaly)")
    timestamps: List[datetime] = Field(description="Timestamps for each prediction")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional algorithm-specific details")

class ClusteringResult(BaseModel):
    """Result from log clustering."""
    labels: List[int] = Field(description="Cluster labels for each log entry")
    centroids: Optional[List[List[float]]] = Field(default=None, description="Cluster centroids (if applicable)")
    silhouette_score: Optional[float] = Field(default=None, description="Clustering quality score")
    cluster_sizes: Dict[int, int] = Field(description="Number of logs in each cluster")
    cluster_examples: Dict[int, List[str]] = Field(description="Representative log examples for each cluster")

class LogAnalysisResult(BaseModel):
    """Combined result from multiple log analysis techniques."""
    parsing: Optional[LogParsingResult] = Field(default=None, description="Results from log parsing")
    anomalies: Optional[AnomalyDetectionResult] = Field(default=None, description="Results from anomaly detection")
    clusters: Optional[ClusteringResult] = Field(default=None, description="Results from clustering")
    summary: str = Field(description="Natural language summary of the analysis")
    recommendations: List[str] = Field(description="List of actionable recommendations") 