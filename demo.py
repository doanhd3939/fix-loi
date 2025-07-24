#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YeuMoney Generator - Demo Script
Demonstrates how to use the generator programmatically
"""

from yeumoney import YeuMoneyGenerator
import time

def demo_single_quest():
    """Demo generating a single quest code"""
    print("🎯 Demo: Generating single quest code")
    print("=" * 40)
    
    generator = YeuMoneyGenerator()
    
    # Generate code for m88
    quest_type = "m88"
    print(f"Generating code for: {quest_type}")
    
    success, message = generator.generate_code(quest_type)
    
    if success:
        print(f"✅ Success: {message}")
    else:
        print(f"❌ Failed: {message}")
    
    print("=" * 40)

def demo_multiple_quests():
    """Demo generating multiple quest codes"""
    print("\n🎯 Demo: Generating multiple quest codes")
    print("=" * 40)
    
    generator = YeuMoneyGenerator()
    
    # List of quests to try
    quest_types = ["m88", "fb88", "invalid_quest"]
    
    for quest_type in quest_types:
        print(f"\nTrying quest: {quest_type}")
        success, message = generator.generate_code(quest_type)
        
        if success:
            print(f"✅ {message}")
            # Save to log
            generator.save_generation_log(quest_type, True, message.split(": ")[-1])
        else:
            print(f"❌ {message}")
            # Save to log
            generator.save_generation_log(quest_type, False)
        
        # Small delay between requests
        time.sleep(1)
    
    print("=" * 40)

def demo_available_configs():
    """Demo showing available configurations"""
    print("\n🎯 Demo: Available quest configurations")
    print("=" * 50)
    
    generator = YeuMoneyGenerator()
    
    print(f"{'STT':<4} {'Quest':<12} {'API':<6} {'Name':<20}")
    print("-" * 50)
    
    for i, (key, config) in enumerate(generator.TRAFFIC_CONFIGS.items(), 1):
        api_type = config.api_type.value
        print(f"{i:<4} {key:<12} {api_type:<6} {config.name:<20}")
    
    print("=" * 50)

if __name__ == "__main__":
    print("🚀 YeuMoney Generator - Demo Script")
    print("This script demonstrates how to use the generator programmatically\n")
    
    try:
        # Run demos
        demo_available_configs()
        demo_single_quest()
        # Uncomment the line below to test multiple quests (will take longer)
        # demo_multiple_quests()
        
        print("\n✅ Demo completed successfully!")
        print("💡 To run the interactive version, use: python3 yeumoney.py")
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
