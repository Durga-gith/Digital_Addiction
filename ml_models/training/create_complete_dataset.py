"""
Combine all chatbot training data into single comprehensive dataset
"""
import pandas as pd
import os
from pathlib import Path
import json

class ChatbotDatasetBuilder:
    def __init__(self):
        self.data_dir = Path(__file__).parent / "data"
        self.output_file = self.data_dir / "chatbot_complete_dataset.csv"
        self.kb_file = Path(__file__).parent.parent / "chatbot_knowledge_base.json"
        
    def load_all_datasets(self):
        """Load all CSV training files"""
        datasets = []
        
        main_data = self.data_dir / "chatbot_training_data.csv"
        if main_data.exists():
            df_main = pd.read_csv(main_data)
            datasets.append(df_main)
            print(f" Loaded main data: {len(df_main)} rows")
        
        fr_data = self.data_dir / "chatbot_training_fr.csv"
        if fr_data.exists():
            df_fr = pd.read_csv(fr_data)
            datasets.append(df_fr)
            print(f" Loaded French data: {len(df_fr)} rows")
        

        psych_data = self.data_dir / "chatbot_psychology.csv"
        if psych_data.exists():
            df_psych = pd.read_csv(psych_data)
            datasets.append(df_psych)
            print(f" Loaded psychology data: {len(df_psych)} rows")
        

        behav_data = self.data_dir / "chatbot_behavioral.csv"
        if behav_data.exists():
            df_behav = pd.read_csv(behav_data)
            datasets.append(df_behav)
            print(f" Loaded behavioral data: {len(df_behav)} rows")
        
        quick_data = self.data_dir / "chatbot_quick_responses.csv"
        if quick_data.exists():
            df_quick = pd.read_csv(quick_data)
            datasets.append(df_quick)
            print(f" Loaded quick responses: {len(df_quick)} rows")
        
        existing_files = [
            "train_psychological.csv",
            "train_recommendation.csv",
            "train_future.csv"
        ]
        
        for file in existing_files:
            file_path = self.data_dir / file
            if file_path.exists():
                try:
                    df_existing = pd.read_csv(file_path)
                    
                    if 'question' not in df_existing.columns:
                        
                        if 'depression' in df_existing.columns:
                            questions = [
                                f"What does depression score {row['depression']} mean?"
                                for _, row in df_existing.iterrows()
                            ]
                            answers = [
                                f"Depression score of {row['depression']}/30 indicates {'mild' if row['depression'] < 10 else 'moderate' if row['depression'] < 20 else 'severe'} level. Consider {'maintaining current habits' if row['depression'] < 10 else 'implementing stress reduction techniques' if row['depression'] < 20 else 'seeking professional help'}."
                                for _, row in df_existing.iterrows()
                            ]
                            df_converted = pd.DataFrame({
                                'question': questions,
                                'answer': answers,
                                'category': 'psychology',
                                'confidence': 0.85,
                                'language': 'en',
                                'tags': 'depression,score',
                                'context_variables': 'depression_level'
                            })
                            datasets.append(df_converted)
                            print(f" Converted {file}: {len(df_converted)} rows")
                except Exception as e:
                    print(f" Could not convert {file}: {e}")
        
       
        if datasets:
            combined_df = pd.concat(datasets, ignore_index=True)
            print(f"\n Total combined data: {len(combined_df)} rows")
            print(f" Languages: {combined_df['language'].value_counts().to_dict()}")
            print(f" Categories: {combined_df['category'].value_counts().to_dict()}")
            return combined_df
        else:
            print(" No training data found!")
            return None
    
    def create_knowledge_base(self, df):
        """Create structured knowledge base from training data"""
        print("\n Creating knowledge base...")
        
        kb = {
            "metadata": {
                "created_date": pd.Timestamp.now().isoformat(),
                "total_samples": len(df),
                "languages": df['language'].nunique(),
                "categories": df['category'].nunique()
            },
            "categories": {},
            "quick_responses": {},
            "assessment_context": {},
            "language_mappings": {}
        }
        

        for category in df['category'].unique():
            cat_data = df[df['category'] == category]
            kb["categories"][category] = {
                "sample_count": len(cat_data),
                "languages": cat_data['language'].unique().tolist(),
                "sample_questions": cat_data['question'].head(5).tolist()
            }
        
        assessment_data = df[df['category'] == 'assessment']
        if not assessment_data.empty:
            kb["assessment_context"] = {
                "score_ranges": {
                    "normal": "0-33%: Healthy digital habits",
                    "moderate": "34-66%: Early warning stage",
                    "addicted": "67-100%: High risk, needs intervention"
                },
                "factors": [
                    "Psychological (depression, anxiety, stress, self-esteem)",
                    "Behavioral (screen time, app usage, data usage)",
                    "Demographic (age)"
                ]
            }
        
        quick_data = df[df['category'].isin(['greeting', 'farewell', 'help'])]
        for _, row in quick_data.iterrows():
            lang = row['language']
            cat = row['category']
            if lang not in kb["quick_responses"]:
                kb["quick_responses"][lang] = {}
            if cat not in kb["quick_responses"][lang]:
                kb["quick_responses"][lang][cat] = []
            kb["quick_responses"][lang][cat].append(row['answer'])
        
        with open(self.kb_file, 'w', encoding='utf-8') as f:
            json.dump(kb, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Knowledge base saved to: {self.kb_file}")
        return kb
    
    def validate_dataset(self, df):
        """Validate the combined dataset"""
        print("\n🔍 Validating dataset...")
        
        validation_results = {
            "total_rows": len(df),
            "missing_values": {},
            "unique_values": {},
            "issues": []
        }
        
        for column in df.columns:
            missing = df[column].isnull().sum()
            if missing > 0:
                validation_results["missing_values"][column] = missing
                validation_results["issues"].append(f"Missing values in {column}: {missing}")
        

        for column in ['category', 'language', 'tags']:
            if column in df.columns:
                validation_results["unique_values"][column] = df[column].nunique()
        

        if 'confidence' in df.columns:
            if df['confidence'].min() < 0 or df['confidence'].max() > 1:
                validation_results["issues"].append("Confidence scores outside 0-1 range")
        

        print(f"✓ Total rows: {validation_results['total_rows']}")
        print(f"✓ Categories: {validation_results['unique_values'].get('category', 'N/A')}")
        print(f"✓ Languages: {validation_results['unique_values'].get('language', 'N/A')}")
        
        if validation_results['issues']:
            print("\n⚠️ Issues found:")
            for issue in validation_results['issues']:
                print(f"  - {issue}")
        else:
            print(" Dataset validation passed!")
        
        return validation_results
    
    def build_complete_dataset(self):
        """Main function to build complete dataset"""
        print("=" * 60)
        print(" CHATBOT TRAINING DATASET BUILDER")
        print("=" * 60)
        

        df = self.load_all_datasets()
        
        if df is None:
            print(" No data to process!")
            return None
        

        df_clean = df.drop_duplicates(subset=['question', 'language'], keep='first')
        print(f" After deduplication: {len(df_clean)} rows")
        

        if 'confidence' in df_clean.columns:
            df_clean['confidence'] = df_clean['confidence'].fillna(0.8)
        if 'language' in df_clean.columns:
            df_clean['language'] = df_clean['language'].fillna('en')
        

        validation = self.validate_dataset(df_clean)
        

        df_clean.to_csv(self.output_file, index=False, encoding='utf-8')
        print(f"\n Combined dataset saved to: {self.output_file}")
        

        kb = self.create_knowledge_base(df_clean)
        

        print("\n" + "=" * 60)
        print(" DATASET SUMMARY")
        print("=" * 60)
        print(f"Total Q&A pairs: {len(df_clean)}")
        print(f"Languages: {df_clean['language'].value_counts().to_dict()}")
        print(f"Categories: {df_clean['category'].value_counts().to_dict()}")
        print(f"Average confidence: {df_clean['confidence'].mean():.2f}")
        print(f"Output file: {self.output_file}")
        print(f"Knowledge base: {self.kb_file}")
        print("=" * 60)
        
        return df_clean, kb

def main():
    """Run dataset builder"""
    builder = ChatbotDatasetBuilder()
    dataset, kb = builder.build_complete_dataset()
    
    if dataset is not None:

        print("\n Sample from dataset:")
        print(dataset[['question', 'category', 'language']].head(5).to_string())
        
        print("\n To train chatbot model:")
        print("python training/train_chatbot.py")
    
    return dataset, kb

if __name__ == "__main__":
    main()