"""
Script to fix pickle compatibility issues by re-saving models
Run this inside Docker container: python fix_models.py
"""

import pickle
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def fix_pickle_models():
    """
    Fix pickle models for numpy compatibility
    """
    models_dir = Path(__file__).parent / 'job_recommendation' / 'models'
    
    tfidf_path = models_dir / 'tfidf_vectorizer_job_recommendation.pkl'
    rf_path = models_dir / 'rf_classifier_job_recommendation.pkl'
    
    print("🔧 Fixing pickle models for compatibility...")
    
    try:
        # Try to load with allow_pickle=True and fix_imports=True
        print(f"📂 Loading TF-IDF vectorizer from {tfidf_path}...")
        with open(tfidf_path, 'rb') as f:
            tfidf = pickle.load(f, encoding='latin1')
        print("✅ TF-IDF loaded successfully")
        
        print(f"📂 Loading Random Forest classifier from {rf_path}...")
        with open(rf_path, 'rb') as f:
            rf = pickle.load(f, encoding='latin1')
        print("✅ Random Forest loaded successfully")
        
        # Re-save with current Python/numpy version
        print("\n💾 Re-saving models with current numpy version...")
        
        with open(tfidf_path, 'wb') as f:
            pickle.dump(tfidf, f, protocol=pickle.HIGHEST_PROTOCOL)
        print("✅ TF-IDF re-saved")
        
        with open(rf_path, 'wb') as f:
            pickle.dump(rf, f, protocol=pickle.HIGHEST_PROTOCOL)
        print("✅ Random Forest re-saved")
        
        print("\n🎉 Models fixed successfully!")
        print("You can now use the job recommendation feature.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nThis might be a numpy version issue.")
        print("The models were created with numpy 2.0+, but you have an older version.")
        return False
    
    return True

if __name__ == "__main__":
    success = fix_pickle_models()
    sys.exit(0 if success else 1)

