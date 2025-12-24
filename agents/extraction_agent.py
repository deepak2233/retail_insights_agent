"""
Data Extraction Agent - Executes SQL queries and retrieves data
"""
import pandas as pd
from typing import Any, Dict
from utils.data_layer import get_data_layer
from agents.query_agent import AgentState


class DataExtractionAgent:
    """Agent that executes SQL queries and extracts data"""
    
    def __init__(self):
        self.data_layer = get_data_layer()
    
    def extract_data(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute SQL query and extract data
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with query results
        """
        try:
            query_intent = state.get("query_intent")
            
            if not query_intent:
                return {
                    **state,
                    "error": "No query intent provided",
                    "query_result": None
                }
            
            sql_query = query_intent.sql_query
            
            print(f"🔍 Executing SQL: {sql_query}")
            
            # Execute query
            result_df = self.data_layer.execute_query(sql_query)
            
            # Convert to dict for easier handling
            result_data = {
                "dataframe": result_df,
                "row_count": len(result_df),
                "columns": list(result_df.columns),
                "data": result_df.to_dict('records') if len(result_df) <= 100 else result_df.head(100).to_dict('records'),
                "summary": self._generate_summary(result_df)
            }
            
            print(f"✅ Query executed successfully. Retrieved {len(result_df)} rows.")
            
            return {
                **state,
                "query_result": result_data,
                "error": None
            }
            
        except Exception as e:
            error_msg = f"Data extraction error: {str(e)}"
            print(f"❌ {error_msg}")
            
            return {
                **state,
                "query_result": None,
                "error": error_msg
            }
    
    def _generate_summary(self, df: pd.DataFrame) -> str:
        """Generate a brief summary of the results"""
        if df.empty:
            return "No data found."
        
        summary = f"Retrieved {len(df)} records with {len(df.columns)} columns.\n"
        
        # Add numeric column summaries
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            summary += "Numeric summaries:\n"
            for col in numeric_cols[:5]:  # Limit to first 5 numeric columns
                summary += f"  - {col}: min={df[col].min():.2f}, max={df[col].max():.2f}, mean={df[col].mean():.2f}\n"
        
        return summary
