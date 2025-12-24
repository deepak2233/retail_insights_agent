"""
Response Generation Agent - Creates human-readable responses
"""
from typing import Dict, Any
try:
    from langchain_core.prompts import ChatPromptTemplate
except ImportError:
    from langchain.prompts import ChatPromptTemplate
from agents.query_agent import AgentState
from utils.llm_utils import get_llm, create_prompt_template
import pandas as pd


class ResponseAgent:
    """Agent that generates natural language responses from query results"""
    
    def __init__(self):
        self.llm = get_llm(temperature=0.3)  # Slightly higher for more natural responses
    
    def generate_response(self, state: AgentState) -> Dict[str, Any]:
        """
        Generate natural language response from query results
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with final answer
        """
        try:
            # Check if validation passed
            if not state.get("validation_passed"):
                error = state.get("error", "Unknown error")
                return {
                    **state,
                    "final_answer": f"I encountered an issue processing your query: {error}"
                }
            
            query_result = state.get("query_result")
            query_intent = state.get("query_intent")
            question = state.get("question")
            
            if not query_result or not query_intent:
                return {
                    **state,
                    "final_answer": "I couldn't process your query. Please try rephrasing your question."
                }
            
            # Format the data for the LLM
            data_summary = self._format_results(query_result)
            
            # Create prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", create_prompt_template(
                    "Retail Analytics Response Specialist",
                    """You provide clear, insightful answers to business questions about retail sales data.
                    
Your responses should:
1. Directly answer the user's question
2. Highlight key insights and trends
3. Use specific numbers and percentages
4. Be concise but comprehensive
5. Provide context and business implications when relevant
6. Format data clearly (use bullet points, tables, or structured text)

If the data shows trends, explain what they mean for the business.
If comparing values, clearly state the differences and their significance.
"""
                )),
                ("user", """
Original Question: {question}

Query Explanation: {explanation}

Data Retrieved:
{data_summary}

Please provide a clear, business-focused answer to the original question based on this data.
""")
            ])
            
            chain = prompt | self.llm
            
            response = chain.invoke({
                "question": question,
                "explanation": query_intent.explanation,
                "data_summary": data_summary
            })
            
            final_answer = response.content
            
            print(f"✅ Response generated successfully")
            
            return {
                **state,
                "final_answer": final_answer
            }
            
        except Exception as e:
            error_msg = f"Response generation error: {str(e)}"
            print(f"❌ {error_msg}")
            
            return {
                **state,
                "final_answer": f"I encountered an error generating the response: {error_msg}"
            }
    
    def _format_results(self, query_result: Dict[str, Any]) -> str:
        """Format query results for LLM consumption"""
        df = query_result.get("dataframe")
        
        if df is None or df.empty:
            return "No data found matching the query criteria."
        
        formatted = f"Results: {len(df)} records\n\n"
        
        # If small dataset, show all rows
        if len(df) <= 20:
            formatted += df.to_string(index=False)
        else:
            # Show summary statistics and sample
            formatted += "Summary Statistics:\n"
            formatted += df.describe().to_string()
            formatted += "\n\nTop 10 Results:\n"
            formatted += df.head(10).to_string(index=False)
            
            if len(df) > 10:
                formatted += f"\n\n(Showing 10 of {len(df)} total records)"
        
        return formatted
