#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YeuMoney Generator - Usage Guide
Interactive guide showing how to use all features
"""

import os
import time
from yeumoney import YeuMoneyGenerator

def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"🎯 {title}")
    print("=" * 60)

def print_section(title):
    """Print formatted section"""
    print(f"\n📌 {title}")
    print("-" * 40)

def show_welcome():
    """Show welcome message"""
    print_header("YEUMONEY CODE GENERATOR - USAGE GUIDE")
    print("Chào mừng bạn đến với hướng dẫn sử dụng YeuMoney Generator!")
    print("Công cụ này đã được nâng cấp hoàn toàn với nhiều tính năng mới.")

def show_available_scripts():
    """Show all available scripts"""
    print_section("CÁC SCRIPT KHẢ DỤNG")
    
    scripts = [
        ("yeumoney.py", "Phiên bản chính với giao diện terminal cải tiến", "python3 yeumoney.py"),
        ("yeumoney_enhanced.py", "Phiên bản UI đẹp (cần cài rich library)", "python3 yeumoney_enhanced.py"),
        ("quick.py", "Tool tạo mã nhanh qua command line", "python3 quick.py m88"),
        ("demo.py", "Script demo các tính năng", "python3 demo.py"),
        ("setup.sh", "Script cài đặt tự động", "./setup.sh"),
    ]
    
    for i, (script, desc, usage) in enumerate(scripts, 1):
        print(f"{i}. 📄 {script}")
        print(f"   📝 {desc}")
        print(f"   💻 {usage}")
        print()

def show_quest_types():
    """Show all quest types with details"""
    print_section("CÁC LOẠI QUEST ĐƯỢC HỖ TRỢ")
    
    generator = YeuMoneyGenerator()
    
    # Group by API type
    ma_quests = []
    md_quests = []
    
    for key, config in generator.TRAFFIC_CONFIGS.items():
        if config.api_type.name == "GET_MA":
            ma_quests.append((key, config))
        else:
            md_quests.append((key, config))
    
    print("🔵 GET_MA API (Traffic User API):")
    for key, config in ma_quests:
        print(f"   • {key:<12} - {config.name}")
    
    print("\n🟢 GET_MD API (Traffic Direct API):")
    for key, config in md_quests:
        print(f"   • {key:<12} - {config.name}")

def show_usage_examples():
    """Show usage examples"""
    print_section("VÍ DỤ SỬ DỤNG")
    
    examples = [
        ("Chế độ tương tác (Interactive)", "python3 yeumoney.py", "Chạy và làm theo hướng dẫn"),
        ("Tạo mã nhanh", "python3 quick.py m88", "Tạo mã cho quest m88 ngay lập tức"),
        ("Giao diện đẹp", "python3 yeumoney_enhanced.py", "Chạy với giao diện colorful (cần rich)"),
        ("Xem demo", "python3 demo.py", "Xem các tính năng demo"),
        ("Cài đặt dependencies", "./setup.sh", "Cài đặt tự động các thư viện cần thiết"),
    ]
    
    for i, (name, command, desc) in enumerate(examples, 1):
        print(f"{i}. {name}:")
        print(f"   💻 {command}")
        print(f"   📝 {desc}")
        print()

def show_features():
    """Show new features"""
    print_section("TÍNH NĂNG MỚI TRONG PHIÊN BẢN 2.0")
    
    features = [
        "✅ Cấu trúc code chuyên nghiệp với OOP",
        "✅ Xử lý lỗi toàn diện với retry mechanism", 
        "✅ Logging chi tiết vào file",
        "✅ Giao diện terminal thân thiện với màu sắc",
        "✅ Validation input và timeout handling",
        "✅ Session management để tối ưu performance",
        "✅ Type hints cho developer experience tốt hơn",
        "✅ Configuration management với JSON",
        "✅ Progress indicators và status updates",
        "✅ Graceful error handling và user feedback",
        "✅ Modular design cho easy maintenance",
        "✅ Comprehensive documentation và examples",
    ]
    
    for feature in features:
        print(f"   {feature}")

def show_installation():
    """Show installation instructions"""
    print_section("HƯỚNG DẪN CÀI ĐẶT")
    
    print("🚀 Cách 1: Cài đặt tự động (Khuyến nghị)")
    print("   chmod +x setup.sh")
    print("   ./setup.sh")
    print()
    
    print("🔧 Cách 2: Cài đặt thủ công")
    print("   # Cài đặt cơ bản")
    print("   pip3 install requests")
    print()
    print("   # Cài đặt nâng cao (UI đẹp)")
    print("   pip3 install requests rich colorama")

def show_troubleshooting():
    """Show troubleshooting guide"""
    print_section("TROUBLESHOOTING")
    
    issues = [
        ("Import Error (rich/colorama)", 
         "pip3 install rich colorama\nhoặc chỉ dùng phiên bản cơ bản"),
        ("Permission Denied (setup.sh)", 
         "chmod +x setup.sh"),
        ("Network Timeout", 
         "Kiểm tra kết nối internet\nChương trình sẽ tự retry 3 lần"),
        ("No Code Found", 
         "Bình thường, API có thể cần điều kiện đặc biệt\nThử quest khác hoặc thử lại sau"),
    ]
    
    for issue, solution in issues:
        print(f"❓ {issue}:")
        print(f"   💡 {solution}")
        print()

def interactive_demo():
    """Run interactive demo"""
    print_section("DEMO TƯƠNG TÁC")
    
    try:
        choice = input("Bạn có muốn xem demo tạo mã không? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            generator = YeuMoneyGenerator()
            
            print("\nDanh sách quest khả dụng:")
            for i, key in enumerate(list(generator.TRAFFIC_CONFIGS.keys())[:5], 1):
                print(f"  {i}. {key}")
            
            quest = input("\nNhập tên quest để demo (hoặc Enter để bỏ qua): ").strip()
            if quest and quest in generator.TRAFFIC_CONFIGS:
                print(f"\n🔄 Đang demo tạo mã cho {quest}...")
                success, message = generator.generate_code(quest)
                
                if success:
                    print(f"✅ {message}")
                else:
                    print(f"❌ {message}")
            elif quest:
                print(f"❌ Quest '{quest}' không hợp lệ")
                
    except KeyboardInterrupt:
        print("\n👋 Demo bị hủy bởi người dùng")

def main():
    """Main function"""
    show_welcome()
    show_available_scripts()
    show_quest_types()
    show_features()
    show_usage_examples()
    show_installation()
    show_troubleshooting()
    interactive_demo()
    
    print_header("KẾT THÚC HƯỚNG DẪN")
    print("🎉 Cảm ơn bạn đã xem hướng dẫn sử dụng YeuMoney Generator!")
    print("💡 Để bắt đầu, hãy chạy: python3 yeumoney.py")
    print("📧 Nếu có vấn đề, hãy kiểm tra file log hoặc README.md")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Hướng dẫn bị hủy bởi người dùng")
    except Exception as e:
        print(f"\n❌ Lỗi trong hướng dẫn: {str(e)}")
