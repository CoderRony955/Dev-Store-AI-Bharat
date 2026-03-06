"""
Test that all imports work correctly
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print("Testing imports...")

try:
    print("1. Importing HuggingFace fetcher...")
    from fetchers.huggingface_fetcher import HuggingFaceFetcher
    print("   ✓ Success")
    
    print("2. Importing OpenRouter fetcher...")
    from fetchers.openrouter_fetcher import OpenRouterFetcher
    print("   ✓ Success")
    
    print("3. Importing GitHub fetcher...")
    from fetchers.github_fetcher import GitHubFetcher
    print("   ✓ Success")
    
    print("\n✅ All imports successful!")
    print("\nYou can now run:")
    print("  python ingestion/run_ingestion.py")
    
except Exception as e:
    print(f"\n❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
