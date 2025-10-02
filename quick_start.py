#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
دليل البدء السريع
Quick Start Guide
"""

import os
import sys
from pathlib import Path

def show_menu():
    """عرض القائمة الرئيسية"""
    print("="*60)
    print("برنامج تحسين الصور للتعرف على النصوص")
    print("Image Enhancement for OCR/Text Recognition")
    print("="*60)
    print()
    print("اختر طريقة التشغيل:")
    print()
    print("1. الواجهة الرسومية العادية (صورة واحدة)")
    print("2. الواجهة الرسومية للمعالجة المجمعة (5000 صورة)")
    print("3. معالجة صورة واحدة من سطر الأوامر")
    print("4. معالجة مجلد كامل من سطر الأوامر")
    print("5. معالجة 5000 صورة مختارة")
    print("6. اختبار البرنامج")
    print("7. عرض المساعدة")
    print("8. خروج")
    print()

def run_gui_app():
    """تشغيل الواجهة الرسومية العادية"""
    try:
        import gui_app
        print("تشغيل الواجهة الرسومية العادية...")
        gui_app.main()
    except ImportError:
        print("خطأ: لا يمكن العثور على ملف gui_app.py")
    except Exception as e:
        print(f"خطأ في تشغيل الواجهة الرسومية: {e}")

def run_selective_gui():
    """تشغيل الواجهة الرسومية للمعالجة المجمعة"""
    try:
        import selective_gui
        print("تشغيل الواجهة الرسومية للمعالجة المجمعة...")
        selective_gui.main()
    except ImportError:
        print("خطأ: لا يمكن العثور على ملف selective_gui.py")
    except Exception as e:
        print(f"خطأ في تشغيل الواجهة الرسومية: {e}")

def run_single_image():
    """معالجة صورة واحدة من سطر الأوامر"""
    image_path = input("أدخل مسار الصورة: ").strip()
    if not image_path:
        print("لم يتم إدخال مسار الصورة")
        return
    
    if not os.path.exists(image_path):
        print(f"الصورة غير موجودة: {image_path}")
        return
    
    try:
        from image_enhancer import ImageEnhancer
        enhancer = ImageEnhancer()
        results = enhancer.process_image(image_path, save_enhanced=True, show_results=True)
        print("تمت معالجة الصورة بنجاح!")
    except Exception as e:
        print(f"خطأ في معالجة الصورة: {e}")

def run_batch_processing():
    """معالجة مجلد كامل من سطر الأوامر"""
    input_dir = input("أدخل مسار مجلد الصور: ").strip()
    output_dir = input("أدخل مسار مجلد الإخراج: ").strip()
    
    if not input_dir or not output_dir:
        print("لم يتم إدخال المسارات المطلوبة")
        return
    
    if not os.path.exists(input_dir):
        print(f"مجلد الإدخال غير موجود: {input_dir}")
        return
    
    try:
        from batch_processor import BatchProcessor
        processor = BatchProcessor(max_workers=4)
        results = processor.process_directory(input_dir, output_dir, recursive=True, save_enhanced=True)
        processor.print_statistics(results)
        print("تمت معالجة المجلد بنجاح!")
    except Exception as e:
        print(f"خطأ في معالجة المجلد: {e}")

def run_selective_processing():
    """معالجة 5000 صورة مختارة"""
    input_dir = input("أدخل مسار مجلد الصور: ").strip()
    output_dir = input("أدخل مسار مجلد الإخراج: ").strip()
    max_images = input("عدد الصور المطلوب (افتراضي 5000): ").strip()
    
    if not max_images:
        max_images = 5000
    else:
        try:
            max_images = int(max_images)
        except ValueError:
            max_images = 5000
    
    if not input_dir or not output_dir:
        print("لم يتم إدخال المسارات المطلوبة")
        return
    
    if not os.path.exists(input_dir):
        print(f"مجلد الإدخال غير موجود: {input_dir}")
        return
    
    try:
        from selective_processor import SelectiveProcessor
        processor = SelectiveProcessor(max_workers=4)
        
        # اختيار الصور
        all_images = processor.find_images_in_directory(Path(input_dir), recursive=True)
        if len(all_images) > max_images:
            selected_images = processor.select_images_interactive(Path(input_dir), max_images)
        else:
            selected_images = all_images
        
        print(f"تم اختيار {len(selected_images)} صورة للمعالجة")
        
        # معالجة الصور
        results = processor.process_selected_images(selected_images, Path(output_dir), save_enhanced=True)
        processor.print_statistics(results)
        print("تمت معالجة الصور المختارة بنجاح!")
    except Exception as e:
        print(f"خطأ في معالجة الصور: {e}")

def run_test():
    """اختبار البرنامج"""
    print("تشغيل اختبار البرنامج...")
    try:
        import test_simple
        test_simple.main()
    except ImportError:
        print("خطأ: لا يمكن العثور على ملف test_simple.py")
    except Exception as e:
        print(f"خطأ في الاختبار: {e}")

def show_help():
    """عرض المساعدة"""
    print("="*60)
    print("دليل الاستخدام")
    print("="*60)
    print()
    print("1. الواجهة الرسومية العادية:")
    print("   - مناسبة لمعالجة صورة واحدة")
    print("   - واجهة سهلة الاستخدام")
    print("   - عرض النتائج بصرياً")
    print()
    print("2. الواجهة الرسومية للمعالجة المجمعة:")
    print("   - مناسبة لمعالجة آلاف الصور")
    print("   - اختيار الصور المحددة")
    print("   - إحصائيات مفصلة")
    print()
    print("3. معالجة صورة واحدة:")
    print("   - مناسبة للاختبار السريع")
    print("   - معالجة مباشرة")
    print()
    print("4. معالجة مجلد كامل:")
    print("   - معالجة جميع الصور في مجلد")
    print("   - معالجة متوازية")
    print()
    print("5. معالجة 5000 صورة مختارة:")
    print("   - اختيار الصور بناءً على معايير")
    print("   - معالجة على نطاق واسع")
    print()
    print("6. اختبار البرنامج:")
    print("   - اختبار الوظائف الأساسية")
    print("   - إنشاء صور تجريبية")
    print()
    print("ملاحظات:")
    print("- تأكد من تثبيت جميع المتطلبات")
    print("- استخدم مسارات صحيحة للملفات")
    print("- ابدأ بعدد صغير من الصور للاختبار")
    print()

def main():
    """الدالة الرئيسية"""
    while True:
        show_menu()
        choice = input("اختر رقم (1-8): ").strip()
        
        if choice == "1":
            run_gui_app()
        elif choice == "2":
            run_selective_gui()
        elif choice == "3":
            run_single_image()
        elif choice == "4":
            run_batch_processing()
        elif choice == "5":
            run_selective_processing()
        elif choice == "6":
            run_test()
        elif choice == "7":
            show_help()
        elif choice == "8":
            print("شكراً لاستخدام البرنامج!")
            break
        else:
            print("اختيار غير صحيح، يرجى المحاولة مرة أخرى")
        
        input("\nاضغط Enter للمتابعة...")
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
