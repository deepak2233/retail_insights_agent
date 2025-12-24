"""
Quick demo script to test the system without UI
Run this to verify everything works before launching Streamlit
"""
import sys
from agents.orchestrator import get_orchestrator
from utils.data_layer import get_data_layer


def run_demo():
    """Run a quick demonstration of the system"""
    
    print("="*80)
    print("🛍️  RETAIL INSIGHTS ASSISTANT - DEMO")
    print("="*80)
    
    print("\n📊 Step 1: Loading data and initializing system...")
    try:
        data_layer = get_data_layer()
        print("✅ Data layer initialized")
        
        # Show basic stats
        stats = data_layer.get_summary_stats()
        if "overall" in stats:
            overall = stats["overall"]
            print(f"\n📈 Dataset Overview:")
            print(f"   • Total Transactions: {overall['total_transactions']:,}")
            print(f"   • Total Revenue: ${overall['total_revenue']:,.2f}")
            print(f"   • Total Profit: ${overall['total_profit']:,.2f}")
            print(f"   • Date Range: {overall['date_range']}")
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        print("\n💡 Make sure you've generated sample data first:")
        print("   python data/generate_data.py")
        return
    
    print("\n🤖 Step 2: Initializing multi-agent system...")
    try:
        orchestrator = get_orchestrator()
        print("✅ Agent orchestrator initialized")
    except Exception as e:
        print(f"❌ Error initializing agents: {e}")
        print("\n💡 Make sure you've configured your API key in .env file")
        return
    
    # Test questions
    test_questions = [
        "What were total sales in 2023?",
        "Which region performed best?",
        "Top 3 categories by revenue?"
    ]
    
    print("\n🔍 Step 3: Testing with sample questions...")
    print("\nNote: This will make API calls to your configured LLM provider\n")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}/{len(test_questions)}")
        print(f"{'='*80}")
        
        try:
            answer = orchestrator.process_query(question)
            print(f"\n✅ Answer:\n{answer}\n")
        except Exception as e:
            print(f"❌ Error: {e}")
            if "API key" in str(e) or "authentication" in str(e).lower():
                print("\n💡 Tip: Check your API key configuration in .env")
            break
    
    print("\n" + "="*80)
    print("✅ DEMO COMPLETE!")
    print("="*80)
    print("\n🚀 Next steps:")
    print("   1. Run the full UI: streamlit run app.py")
    print("   2. Try more complex questions")
    print("   3. Generate summary reports")
    print("\n")


if __name__ == "__main__":
    run_demo()
