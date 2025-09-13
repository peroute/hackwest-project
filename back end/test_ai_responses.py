#!/usr/bin/env python3
"""
Test AI educational responses
"""
import requests
import json

def test_ai_responses():
    """Test AI educational responses"""
    base_url = "http://127.0.0.1:8000"
    
    print("🧠 Testing AI Educational Responses")
    print("=" * 50)
    
    # Test cases for educational questions
    test_cases = [
        ("What is photosynthesis?", "Should give educational explanation"),
        ("How can I improve my study habits?", "Should give study advice"),
        ("What are effective time management techniques?", "Should give practical tips"),
        ("How do I prepare for exams?", "Should give exam preparation advice"),
        ("What is the difference between mitosis and meiosis?", "Should explain biological concepts"),
    ]
    
    for question, expected in test_cases:
        try:
            ask_data = {"question": question}
            response = requests.post(f"{base_url}/api/v1/ask/", json=ask_data)
            
            if response.status_code == 200:
                result = response.json()
                resource_count = len(result.get('relevant_resources', []))
                answer = result['answer']
                
                print(f"\n📝 Question: '{question}'")
                print(f"   Expected: {expected}")
                print(f"   Resources found: {resource_count}")
                print(f"   Answer length: {len(answer)} chars")
                print(f"   Answer preview: {answer[:200]}...")
                
                # Check if it's working as expected
                if resource_count == 0 and len(answer) > 100:
                    print("   ✅ AI provided educational response without searching")
                else:
                    print("   🤔 Response needs adjustment")
                    
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_ai_responses()
