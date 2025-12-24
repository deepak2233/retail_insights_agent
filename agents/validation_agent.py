"""
Validation Agent - Validates query results and data quality with confidence scoring
"""
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass
from agents.query_agent import AgentState


@dataclass
class ValidationResult:
    """Detailed validation result"""
    passed: bool
    confidence: float  # 0.0 to 1.0
    issues: List[str]
    warnings: List[str]
    data_quality_score: float
    completeness_score: float
    consistency_score: float


class ConfidenceScorer:
    """Calculates confidence scores for query results"""
    
    def score(self, df: pd.DataFrame, query_intent: Any = None) -> Dict[str, float]:
        """
        Calculate confidence scores for the result
        
        Args:
            df: Query result DataFrame
            query_intent: The original query intent
            
        Returns:
            Dictionary of confidence scores
        """
        if df is None or df.empty:
            return {
                "data_quality": 0.5,  # Empty might be valid
                "completeness": 0.0,
                "consistency": 1.0,  # Empty is consistent
                "overall": 0.3
            }
        
        data_quality = self._score_data_quality(df)
        completeness = self._score_completeness(df)
        consistency = self._score_consistency(df)
        
        # Weighted overall score
        overall = (
            data_quality * 0.4 +
            completeness * 0.3 +
            consistency * 0.3
        )
        
        return {
            "data_quality": data_quality,
            "completeness": completeness,
            "consistency": consistency,
            "overall": overall
        }
    
    def _score_data_quality(self, df: pd.DataFrame) -> float:
        """Score based on data quality metrics"""
        score = 1.0
        
        # Penalize for null values
        null_ratio = df.isnull().sum().sum() / (len(df) * len(df.columns))
        score -= null_ratio * 0.5
        
        # Penalize for suspicious patterns
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            # Check for negative values in typically positive columns
            if col in ['revenue', 'quantity', 'amount', 'orders']:
                if (df[col] < 0).any():
                    score -= 0.1
            
            # Check for extreme outliers (>5 std from mean)
            if len(df[col].dropna()) > 10:
                mean = df[col].mean()
                std = df[col].std()
                if std > 0:
                    outliers = ((df[col] - mean).abs() > 5 * std).sum()
                    if outliers > 0:
                        score -= 0.05 * min(outliers, 5)
        
        return max(0.0, min(1.0, score))
    
    def _score_completeness(self, df: pd.DataFrame) -> float:
        """Score based on data completeness"""
        if df.empty:
            return 0.0
        
        # Calculate non-null ratio
        non_null_ratio = 1 - (df.isnull().sum().sum() / (len(df) * len(df.columns)))
        
        # Bonus for having expected columns
        expected_cols = ['revenue', 'orders', 'count', 'total', 'sum', 'avg']
        col_names_lower = [c.lower() for c in df.columns]
        has_expected = sum(1 for e in expected_cols if any(e in c for c in col_names_lower))
        expected_bonus = min(has_expected * 0.1, 0.2)
        
        return min(1.0, non_null_ratio + expected_bonus)
    
    def _score_consistency(self, df: pd.DataFrame) -> float:
        """Score based on data consistency"""
        score = 1.0
        
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        for col in numeric_cols:
            # Check for consistent data types
            if df[col].dtype == 'object':
                score -= 0.1
            
            # Check for reasonable value ranges
            if len(df[col].dropna()) > 0:
                min_val = df[col].min()
                max_val = df[col].max()
                
                # Very large ranges might indicate issues
                if max_val > 0 and min_val > 0:
                    if max_val / min_val > 10000:
                        score -= 0.1
        
        return max(0.0, min(1.0, score))


class ValidationAgent:
    """Agent that validates query results with enhanced checks and confidence scoring"""
    
    def __init__(self):
        self.validation_rules = {
            "min_rows": 0,  # Allow empty results
            "max_rows": 1000000,  # Sanity check
            "required_numeric_cols": ["revenue", "profit", "total"],  # At least one of these
        }
        self.confidence_scorer = ConfidenceScorer()
    
    def validate(self, state: AgentState) -> Dict[str, Any]:
        """
        Validate query results with comprehensive checks
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with validation status and confidence scores
        """
        try:
            query_result = state.get("query_result")
            
            if not query_result:
                return {
                    **state,
                    "validation_passed": False,
                    "confidence_scores": {"overall": 0.0},
                    "error": "No query result to validate"
                }
            
            # Check if there was an error in extraction
            if state.get("error"):
                return {
                    **state,
                    "validation_passed": False,
                    "confidence_scores": {"overall": 0.0}
                }
            
            df = query_result.get("dataframe")
            
            if df is None:
                return {
                    **state,
                    "validation_passed": False,
                    "confidence_scores": {"overall": 0.0},
                    "error": "No dataframe in query result"
                }
            
            # Perform comprehensive validation
            validation_result = self._comprehensive_validation(df, state.get("query_intent"))
            
            # Calculate confidence scores
            confidence_scores = self.confidence_scorer.score(df, state.get("query_intent"))
            
            # Determine if validation passed
            validation_passed = validation_result.passed
            
            if not validation_passed:
                error_msg = "Validation failed: " + "; ".join(validation_result.issues)
                print(f"❌ {error_msg}")
                return {
                    **state,
                    "validation_passed": False,
                    "confidence_scores": confidence_scores,
                    "validation_warnings": validation_result.warnings,
                    "error": error_msg
                }
            
            # Log warnings if any
            if validation_result.warnings:
                for warning in validation_result.warnings:
                    print(f"⚠️  Warning: {warning}")
            
            row_count = len(df)
            confidence_pct = confidence_scores['overall'] * 100
            print(f"✅ Validation passed: {row_count} rows, {len(df.columns)} columns, confidence: {confidence_pct:.1f}%")
            
            return {
                **state,
                "validation_passed": True,
                "confidence_scores": confidence_scores,
                "validation_warnings": validation_result.warnings,
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            print(f"❌ {error_msg}")
            
            return {
                **state,
                "validation_passed": False,
                "confidence_scores": {"overall": 0.0},
                "error": error_msg
            }
    
    def _comprehensive_validation(self, df: pd.DataFrame, 
                                   query_intent: Any = None) -> ValidationResult:
        """
        Perform comprehensive validation checks
        
        Args:
            df: DataFrame to validate
            query_intent: Query intent for context
            
        Returns:
            ValidationResult with detailed information
        """
        issues = []
        warnings = []
        
        row_count = len(df)
        
        # Check 1: Row count bounds
        if row_count > self.validation_rules["max_rows"]:
            issues.append(f"Too many rows: {row_count}")
        
        # Check 2: Empty result handling
        if row_count == 0:
            warnings.append("Query returned no results - this might be expected")
        
        # Check 3: Data type validation
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) == 0:
            categorical_cols = ['region', 'category', 'product', 'month', 'quarter', 'state', 'status']
            if not any(col in df.columns for col in categorical_cols):
                warnings.append("No numeric columns found in result")
        
        # Check 4: Null value analysis
        null_counts = df.isnull().sum()
        total_nulls = null_counts.sum()
        if total_nulls > 0:
            null_cols = null_counts[null_counts > 0].index.tolist()
            null_pct = (total_nulls / (len(df) * len(df.columns))) * 100
            if null_pct > 50:
                issues.append(f"High null ratio: {null_pct:.1f}%")
            elif null_pct > 10:
                warnings.append(f"Null values in columns: {null_cols}")
        
        # Check 5: Negative value validation
        for col in numeric_cols:
            if col.lower() in ['revenue', 'quantity', 'unit_price', 'amount', 'orders', 'count']:
                neg_count = (df[col] < 0).sum()
                if neg_count > 0:
                    if col.lower() in ['revenue', 'quantity', 'amount']:
                        issues.append(f"Negative values in {col}: {neg_count}")
                    else:
                        warnings.append(f"Negative values in {col}: {neg_count}")
        
        # Check 6: Duplicate detection
        if len(df) > 0:
            dup_count = df.duplicated().sum()
            if dup_count > 0:
                dup_pct = (dup_count / len(df)) * 100
                if dup_pct > 50:
                    warnings.append(f"High duplicate ratio: {dup_pct:.1f}%")
        
        # Check 7: Outlier detection
        for col in numeric_cols:
            if len(df[col].dropna()) > 10:
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                if iqr > 0:
                    outliers = ((df[col] < q1 - 3*iqr) | (df[col] > q3 + 3*iqr)).sum()
                    if outliers > len(df) * 0.1:
                        warnings.append(f"Many outliers detected in {col}")
        
        # Check 8: SQL injection patterns (paranoia check)
        for col in df.columns:
            if any(pattern in str(col).lower() for pattern in ['drop', 'delete', ';--', 'exec']):
                issues.append(f"Suspicious column name detected: {col}")
        
        # Calculate component scores
        data_quality_score = 1.0 - (len(issues) * 0.2) - (len(warnings) * 0.05)
        completeness_score = 1.0 - (total_nulls / max(len(df) * len(df.columns), 1))
        consistency_score = 1.0 if len(issues) == 0 else 0.5
        
        return ValidationResult(
            passed=len(issues) == 0,
            confidence=max(0.0, data_quality_score),
            issues=issues,
            warnings=warnings,
            data_quality_score=max(0.0, data_quality_score),
            completeness_score=max(0.0, completeness_score),
            consistency_score=consistency_score
        )
    
    def _format_validation_report(self, df: pd.DataFrame) -> str:
        """Format a validation report"""
        report = "Validation Report:\n"
        report += f"  Rows: {len(df)}\n"
        report += f"  Columns: {len(df.columns)}\n"
        report += f"  Columns: {', '.join(df.columns)}\n"
        
        # Check for nulls
        null_counts = df.isnull().sum()
        if null_counts.any():
            report += "\n  Null Values:\n"
            for col, count in null_counts[null_counts > 0].items():
                report += f"    {col}: {count}\n"
        
        return report
