"""
Simple test for data layer without LLM dependencies
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Direct imports without going through __init__.py
import duckdb
import pandas as pd
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleDataLayer:
    """Simplified data layer for testing"""
    
    def __init__(self):
        self.csv_path = "data/processed_sales_data.csv"
        self.db_path = ":memory:"
        self.conn = None
        self._initialize()
    
    def _initialize(self):
        """Initialize database"""
        self.conn = duckdb.connect(self.db_path)
        
        if os.path.exists(self.csv_path):
            logger.info(f"📊 Loading data from {self.csv_path}...")
            
            self.conn.execute(f"""
                CREATE OR REPLACE TABLE sales AS 
                SELECT * FROM read_csv_auto('{self.csv_path}', 
                    ignore_errors=true,
                    null_padding=true
                )
            """)
            
            row_count = self.conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
            logger.info(f"✅ Loaded {row_count:,} records")
            return True
        else:
            logger.error(f"❌ File not found: {self.csv_path}")
            return False
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute query"""
        return self.conn.execute(query).fetchdf()


def test_data_loading():
    """Test 1: Data Loading"""
    print("\n" + "="*80)
    print("TEST 1: Data Loading & Initialization")
    print("="*80)
    
    try:
        data_layer = SimpleDataLayer()
        
        # Basic query
        result = data_layer.execute_query("""
            SELECT COUNT(*) as total_orders
            FROM sales
        """)
        
        orders = result['total_orders'].iloc[0]
        print(f"\n✅ Total Orders: {orders:,}")
        
        return orders > 0
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_schema():
    """Test 2: Schema Validation"""
    print("\n" + "="*80)
    print("TEST 2: Schema Validation")
    print("="*80)
    
    try:
        data_layer = SimpleDataLayer()
        
        # Get column names
        schema = data_layer.execute_query("DESCRIBE sales")
        columns = schema['column_name'].tolist()
        
        print(f"\n📋 Found {len(columns)} columns")
        
        # Check key columns
        required_columns = [
            'order_id', 'date', 'status', 'category', 
            'state', 'amount', 'revenue', 'quantity'
        ]
        
        missing = []
        for col in required_columns:
            if col in columns:
                print(f"   ✅ {col}")
            else:
                print(f"   ❌ {col} (MISSING)")
                missing.append(col)
        
        return len(missing) == 0
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        return False


def test_basic_queries():
    """Test 3: Basic Analytics Queries"""
    print("\n" + "="*80)
    print("TEST 3: Basic Analytics Queries")
    print("="*80)
    
    try:
        data_layer = SimpleDataLayer()
        
        # Query 1: Overall Stats
        print("\n📊 Overall Statistics:")
        result = data_layer.execute_query("""
            SELECT 
                COUNT(*) as total_orders,
                SUM(revenue) as total_revenue,
                AVG(amount) as avg_order_value,
                SUM(CASE WHEN is_cancelled THEN 1 ELSE 0 END) as cancelled_orders
            FROM sales
        """)
        
        for col, val in result.iloc[0].items():
            if isinstance(val, float):
                print(f"   {col}: ₹{val:,.2f}" if 'revenue' in col or 'avg' in col else f"   {col}: {val:,.0f}")
            else:
                print(f"   {col}: {val:,}")
        
        # Query 2: Top States
        print("\n🏆 Top 5 States by Revenue:")
        result = data_layer.execute_query("""
            SELECT state, 
                   SUM(revenue) as revenue,
                   COUNT(*) as orders
            FROM sales
            WHERE state IS NOT NULL
            GROUP BY state
            ORDER BY revenue DESC
            LIMIT 5
        """)
        
        for idx, row in result.iterrows():
            print(f"   {idx+1}. {row['state']}: ₹{row['revenue']:,.2f} ({row['orders']:,} orders)")
        
        # Query 3: Category Performance
        print("\n📦 Revenue by Category:")
        result = data_layer.execute_query("""
            SELECT category,
                   SUM(revenue) as revenue,
                   COUNT(*) as orders
            FROM sales
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY revenue DESC
        """)
        
        for idx, row in result.iterrows():
            print(f"   {row['category']}: ₹{row['revenue']:,.2f} ({row['orders']:,} orders)")
        
        # Query 4: Monthly Trend
        print("\n📈 Monthly Revenue Trend:")
        result = data_layer.execute_query("""
            SELECT year, month,
                   SUM(revenue) as revenue,
                   COUNT(*) as orders
            FROM sales
            GROUP BY year, month
            ORDER BY year, month
            LIMIT 10
        """)
        
        for idx, row in result.iterrows():
            print(f"   {int(row['year'])}-{int(row['month']):02d}: ₹{row['revenue']:,.2f} ({row['orders']:,} orders)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_advanced_queries():
    """Test 4: Advanced Analytics"""
    print("\n" + "="*80)
    print("TEST 4: Advanced Analytics")
    print("="*80)
    
    try:
        data_layer = SimpleDataLayer()
        
        # Query 1: Cancellation Rate
        print("\n🚫 Cancellation Analysis:")
        result = data_layer.execute_query("""
            SELECT 
                SUM(CASE WHEN is_cancelled THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as cancellation_rate,
                SUM(CASE WHEN is_cancelled THEN 1 ELSE 0 END) as cancelled_orders,
                COUNT(*) - SUM(CASE WHEN is_cancelled THEN 1 ELSE 0 END) as fulfilled_orders
            FROM sales
        """)
        
        for col, val in result.iloc[0].items():
            if 'rate' in col:
                print(f"   {col}: {val:.2f}%")
            else:
                print(f"   {col}: {int(val):,}")
        
        # Query 2: B2B vs B2C
        print("\n💼 B2B vs B2C Analysis:")
        result = data_layer.execute_query("""
            SELECT 
                CASE WHEN is_b2b THEN 'B2B' ELSE 'B2C' END as customer_type,
                COUNT(*) as orders,
                SUM(revenue) as revenue,
                AVG(amount) as avg_order_value
            FROM sales
            GROUP BY is_b2b
        """)
        
        for idx, row in result.iterrows():
            print(f"   {row['customer_type']}: {int(row['orders']):,} orders, ₹{row['revenue']:,.2f} revenue, ₹{row['avg_order_value']:.2f} AOV")
        
        # Query 3: Fulfillment Analysis
        print("\n📦 Fulfillment Type Analysis:")
        result = data_layer.execute_query("""
            SELECT fulfilment,
                   COUNT(*) as orders,
                   SUM(revenue) as revenue
            FROM sales
            WHERE fulfilment IS NOT NULL
            GROUP BY fulfilment
            ORDER BY revenue DESC
        """)
        
        for idx, row in result.iterrows():
            print(f"   {row['fulfilment']}: {int(row['orders']):,} orders, ₹{row['revenue']:,.2f}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🧪 DATA LAYER TEST - Real Amazon Sales Data")
    print("="*80)
    
    tests = [
        ("Data Loading", test_data_loading),
        ("Schema Validation", test_schema),
        ("Basic Queries", test_basic_queries),
        ("Advanced Analytics", test_advanced_queries)
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ {name} crashed: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<50} {status}")
    
    all_passed = all(results.values())
    passed_count = sum(1 for p in results.values() if p)
    
    print("\n" + "="*80)
    print(f"Results: {passed_count}/{len(results)} tests passed")
    
    if all_passed:
        print("🎉 ALL TESTS PASSED! Data layer is working correctly with real data.")
    else:
        print("⚠️  Some tests failed. Please review the output above.")
    print("="*80 + "\n")
