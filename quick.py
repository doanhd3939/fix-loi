#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YeuMoney Quick Generator
Quick command-line tool for generating codes
Usage: python3 quick.py [quest_type]
"""

import sys
from yeumoney import YeuMoneyGenerator

def main():
    """Quick generator main function"""
    generator = YeuMoneyGenerator()
    
    # Check if quest type provided as argument
    if len(sys.argv) > 1:
        quest_type = sys.argv[1].strip()
        
        print(f"🎯 Quick generating code for: {quest_type}")
        print("⏳ Please wait...")
        
        success, message = generator.generate_code(quest_type)
        
        if success:
            print(f"✅ {message}")
            # Extract and display just the code
            code = message.split(": ")[-1]
            print(f"📋 Code to copy: {code}")
        else:
            print(f"❌ {message}")
            
        return 0 if success else 1
    
    else:
        # Show usage and available quests
        print("🎯 YeuMoney Quick Generator")
        print("=" * 40)
        print("Usage: python3 quick.py [quest_type]")
        print("\nAvailable quest types:")
        
        for i, (key, config) in enumerate(generator.TRAFFIC_CONFIGS.items(), 1):
            api_badge = "🔵" if config.api_type.name == "GET_MA" else "🟢"
            print(f"  {api_badge} {key:<12} - {config.name}")
        
        print("\nExamples:")
        print("  python3 quick.py m88")
        print("  python3 quick.py fb88")
        print("  python3 quick.py v9bet")
        
        return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
