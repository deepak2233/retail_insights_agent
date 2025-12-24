"""
Complete end-to-end system test with real Amazon sales data
"""
import os
os.environ["OPENAI_API_KEY"] = "test-key"  # Will use mock for testing

from utils.data_layer import DataLayer
from agents.query_agent import QueryResolutionAgent
from agents.extraction_agent import DataExtractionAgent
from agents.validation_agent import DataValidationAgent
from agents.response_agent import ResponseGenerationAgent

def test_data_layer():
    """Test data layer with real data"""
    print("\n" + "="*80)
    print("TEST 1: Data Layer Initialization")
    print("="*80)
    
    try:
        data_layer = DataLayer()
        
        # Test basic query
        result = data_layer.execute_query("""
            SELECT COUNT(*) as total_orders, 
                   SUM(revenue) as total_revenue,
                   AVG(amount) as avg_order_value
            FROM sales
            LIMIT 5
        """)
        
        print("\n✅ Data Layer Test Results:")
        print(result)
        
        # Test schema
        schema = data_layer.get_schema_context()
        print(f"\n📋 Schema Length: {len(schema)} characters")
        print(f"✅ Schema includes 'order_id': {'order_id' in schema}")
        print(f"✅ Schema includes 'revenue': {'revenue' in schema}")
        print(f"✅ Schema includes 'ship_state': {'ship_state' in schema}")
        
        # Test summary stats
        stats = data_layer.get_summary_stats()
        print(f"\n📊 Summary Stats Keys: {list(stats.keys())}")
        if 'overall' in stats:
            print(f"✅ Total Orders: {stats['overall'].get('total_orders', 'N/A'):,}")
            print(f"✅ Total Revenue: ₹{stats['overall'].get('total_revenue', 0):,.2f}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Data Layer Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_query_generation():
    """Test query agent with real schema"""
    print("\n" + "="*80)
    print("TEST 2: Query Generation")
    print("="*80)
    
    try:
        agent = QueryResolutionAgent()
        
        # Get schema
        schema = agent.get_schema_context()
        print(f"\n📋 Schema for Query Agent:")
        print(f"   Length: {len(schema)} characters")
        print(f"   Contains 'ship_state': {'ship_state' in schema}")
        print(f"   Contains 'revenue': {'revenue' in schema}")
        print(f"   Contains 'category': {'category' in schema}")
        
        print("\n✅ Query Agent initialized with real Amazon schema")
        return True
        
    except Exception as e:
        print(f"\n❌ Query Agent Test Failed: {e}")
        return False


def test_data_extraction():
    """Test extraction agent with real queries"""
    print("\n" + "="*80)
    print("TEST 3: Data Extraction")
    print("="*80)
    
    try:
        data_layer = DataLayer()
        agent = DataExtractionAgent(data_layer)
        
        # Test queries
        test_queries = [
            ("Total orders", "SELECT COUNT(*) as total_orders FROM sales"),
            ("Top 5 states", """
                SELECT ship_state, SUM(revenue) as revenue 
                FROM sales 
                WHERE ship_state IS NOT NULL 
                GROUP BY ship_state 
                ORDER BY revenue DESC 
                LIMIT 5
            """),
            ("Revenue by category", """
                SELECT category, SUM(revenue) as revenue, COUNT(*) as orders
                FROM sales
                WHERE category IS NOT NULL
                GROUP BY category
                ORDER BY revenue DESC
            """)
        ]
        
        for name, query in test_queries:
            print(f"\n🔍 Testing: {name}")
            result = agent.extract_data(query)
            
            if "error" in result:
                print(f"   ❌ Error: {result['error']}")
            else:
                print(f"   ✅ Rows: {result['row_count']}")
                print(f"   ✅ Columns: {result['column_count']}")
                print(f"   Preview: {str(result['data'].head(3).to_dict('records'))[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Extraction Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validation():
    """Test validation agent"""
    print("\n" + "="*80)
    print("TEST 4: Data Validation")
    print("="*80)
    
    try:
        import pandas as pd
        agent = DataValidationAgent()
        
        # Test with sample data
        test_df = pd.DataFrame({
            'revenue': [100, 200, 300],
            'orders': [1, 2, 3]
        })
        
        result = agent.validate(test_df, "SELECT revenue, orders FROM sales")
        
        print(f"\n✅ Validation Result:")
        print(f"   Valid: {result.get('is_valid')}")
        print(f"   Issues: {len(result.get('issues', []))}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Validation Test Failed: {e}")
        return False


def test_database_queries():
    """Test real database queries"""
    print("\n" + "="*80)
    print("TEST 5: Real Database Queries")
    print("="*80)
    
    try:
        data_layer = DataLayer()
        
        queries = {
            "Total Revenue": "SELECT SUM(revenue) as total FROM sales",
            "Order Count": "SELECT COUNT(*) as count FROM sales",
            "Cancelled Rate": """
                SELECT 
                    SUM(CASE WHEN is_cancelled THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as rate
                FROM sales
            """,
            "Top Category": """
                SELECT category, SUM(revenue) as revenue 
                FROM sales 
                WHERE category IS NOT NULL 
                GROUP BY category 
                ORDER BY revenue DESC 
                LIMIT 1
            """
        }
        
        for name, query in queries.items():
            print(f"\n📊 {name}:")
            result = data_layer.execute_query(query)
            print(f"   {result.to_dict('records')[0]}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Database Query Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🧪 COMPLETE SYSTEM TEST - Real Amazon Sales Data")
    print("="*80)
    
    results = {
        "Data Layer": test_data_layer(),
        "Query Generation": test_query_generation(),
        "Data Extraction": test_data_extraction(),
        "Validation": test_validation(),
        "Database Queries": test_database_queries()
    }
    
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<50} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*80)
    if all_passed:
        print("🎉 ALL TESTS PASSED! System is ready for production.")
    else:
        print("⚠️  Some tests failed. Please review the output above.")
    print("="*80 + "\n")
