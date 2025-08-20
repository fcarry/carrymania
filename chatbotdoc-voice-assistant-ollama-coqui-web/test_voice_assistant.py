#!/usr/bin/env python3
"""
Simple test script to verify the voice assistant components work
"""
import sys
import tempfile
import os

# Test imports
def test_imports():
    print("Testing imports...")
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import speech_recognition as sr
        print("✅ SpeechRecognition imported successfully")
    except ImportError as e:
        print(f"⚠️ SpeechRecognition not available: {e}")
    
    try:
        from TTS.api import TTS
        print("✅ Coqui TTS imported successfully")
    except ImportError as e:
        print(f"⚠️ Coqui TTS not available: {e}")
    
    try:
        import requests
        print("✅ Requests imported successfully")
    except ImportError as e:
        print(f"❌ Requests import failed: {e}")
        return False
    
    return True

def test_ollama_connection():
    print("\nTesting Ollama connection...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("✅ Ollama is running and accessible")
            models = response.json().get('models', [])
            print(f"Available models: {[m.get('name', 'unknown') for m in models]}")
            return True
        else:
            print(f"⚠️ Ollama responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️ Ollama not accessible: {e}")
        return False

def test_app_structure():
    print("\nTesting application structure...")
    app_file = "chatbotdoc-voice-assistant-ollama-coqui-web.py"
    
    if os.path.exists(app_file):
        print(f"✅ Main application file {app_file} exists")
        
        # Try to compile the file
        try:
            import py_compile
            py_compile.compile(app_file, doraise=True)
            print("✅ Application file compiles without syntax errors")
            return True
        except py_compile.PyCompileError as e:
            print(f"❌ Syntax error in application: {e}")
            return False
    else:
        print(f"❌ Main application file {app_file} not found")
        return False

def main():
    print("🎤 Voice Assistant Test Suite")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 3
    
    if test_imports():
        tests_passed += 1
    
    if test_ollama_connection():
        tests_passed += 1
    
    if test_app_structure():
        tests_passed += 1
    
    print("\n" + "=" * 40)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Voice assistant is ready to run.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above for issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())