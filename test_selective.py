#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار المعالجة الانتقائية
Test Selective Processing
"""

import cv2
import numpy as np
import os
from pathlib import Path
from selective_processor import SelectiveProcessor
from folder_manager import FolderManager
from performance_optimizer import PerformanceOptimizer
import time

def create_large_test_dataset(num_images=100):
    """إنشاء مجموعة بيانات كبيرة للاختبار"""
    print(f"Creating {num_images} test images...")
    
    # إنشاء مجلد للصور التجريبية
    test_dir = Path("large_test_dataset")
    test_dir.mkdir(exist_ok=True)
    
    # نصوص مختلفة للاختبار
    texts = [
        "Document 1 - Important Information",
        "Report 2024 - Financial Analysis",
        "Meeting Notes - Project Discussion",
        "Contract Agreement - Terms and Conditions",
        "Invoice #12345 - Payment Due",
        "Receipt - Purchase Confirmation",
        "Certificate - Achievement Award",
        "License - Software Agreement",
        "Manual - User Guide",
        "Form - Application Submission"
    ]
    
    for i in range(num_images):
        # إنشاء صورة
        img = np.ones((400, 600, 3), dtype=np.uint8) * 255
        
        # إضافة نص
        text = texts[i % len(texts)]
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # إضافة النص الرئيسي
        cv2.putText(img, text, (50, 150), font, 1, (0, 0, 0), 2, cv2.LINE_AA)
        
        # إضافة رقم الصورة
        cv2.putText(img, f"Image {i+1:04d}", (50, 200), font, 0.7, (100, 100, 100), 2, cv2.LINE_AA)
        
        # إضافة بعض الضوضاء والتموج
        noise = np.random.randint(0, 30, img.shape, dtype=np.uint8)
        img = cv2.add(img, noise)
        
        # إضافة تموج خفيف
        rows, cols = img.shape[:2]
        for row in range(rows):
            for col in range(cols):
                offset_x = int(2 * np.sin(row * 0.05))
                offset_y = int(1 * np.cos(col * 0.05))
                if 0 <= row + offset_y < rows and 0 <= col + offset_x < cols:
                    img[row, col] = img[row + offset_y, col + offset_x]
        
        # حفظ الصورة
        filename = f"test_image_{i+1:04d}.png"
        filepath = test_dir / filename
        cv2.imwrite(str(filepath), img)
        
        if (i + 1) % 10 == 0:
            print(f"Created {i+1}/{num_images} images")
    
    print(f"Created {num_images} test images in: {test_dir}")
    return test_dir

def test_selective_processing():
    """اختبار المعالجة الانتقائية"""
    print("="*60)
    print("Testing Selective Processing")
    print("="*60)
    
    # إنشاء مجموعة بيانات كبيرة
    test_dir = create_large_test_dataset(50)
    
    # إنشاء معالج الصور الانتقائي
    processor = SelectiveProcessor(max_workers=4, use_multiprocessing=False)
    
    # دالة callback لتتبع التقدم
    def progress_callback(progress, processed, total):
        print(f"\rProgress: {progress:.1f}% ({processed}/{total})", end='', flush=True)
    
    processor.set_progress_callback(progress_callback)
    
    # إنشاء مجلد الإخراج
    output_dir = Path("selective_output")
    output_dir.mkdir(exist_ok=True)
    
    print(f"\nProcessing images in: {test_dir}")
    print(f"Output directory: {output_dir}")
    
    # اختيار الصور بناءً على النمط
    selected_images = processor.select_images_by_pattern(test_dir, "test_image_", True)
    print(f"\nSelected {len(selected_images)} images by pattern")
    
    # معالجة الصور المختارة
    start_time = time.time()
    results = processor.process_selected_images(
        selected_images,
        output_dir,
        save_enhanced=True,
        structure_type="by_size"
    )
    end_time = time.time()
    
    print(f"\n\nProcessing completed in {end_time - start_time:.2f} seconds")
    
    # طباعة الإحصائيات
    processor.print_statistics(results)
    
    # حفظ النتائج
    results_file = output_dir / "selective_results.json"
    processor.save_results(results, results_file, 'json')
    print(f"\nResults saved to: {results_file}")
    
    return results

def test_folder_management():
    """اختبار إدارة المجلدات"""
    print("\n" + "="*60)
    print("Testing Folder Management")
    print("="*60)
    
    # إنشاء مدير المجلدات
    manager = FolderManager()
    
    # إنشاء مجلد للاختبار
    test_dir = Path("folder_test")
    test_dir.mkdir(exist_ok=True)
    
    # إنشاء بعض الملفات التجريبية
    for i in range(10):
        test_file = test_dir / f"test_{i}.txt"
        test_file.write_text(f"Test content {i}")
    
    # إنشاء تقرير المجلد
    report_file = test_dir / "folder_report.json"
    success = manager.create_folder_report(test_dir, report_file)
    print(f"Folder report created: {success}")
    
    # إنشاء مخطط هيكل المجلدات
    diagram_file = test_dir / "folder_diagram.txt"
    success = manager.create_folder_structure_diagram(test_dir, diagram_file)
    print(f"Folder diagram created: {success}")
    
    # تنظيف المجلدات الفارغة
    deleted_count = manager.cleanup_empty_folders(test_dir)
    print(f"Empty folders deleted: {deleted_count}")
    
    # حساب حجم المجلد
    folder_size = manager.get_folder_size(test_dir)
    print(f"Folder size: {manager.format_size(folder_size)}")
    
    return test_dir

def test_performance_optimization():
    """اختبار تحسين الأداء"""
    print("\n" + "="*60)
    print("Testing Performance Optimization")
    print("="*60)
    
    # إنشاء محسن الأداء
    optimizer = PerformanceOptimizer()
    
    # تحليل النظام
    print("System Information:")
    print(f"CPU Count: {optimizer.system_info.get('cpu_count', 'Unknown')}")
    print(f"Available Memory: {optimizer.system_info.get('memory_available', 0) / (1024**3):.1f} GB")
    
    # حساب العدد الأمثل للعمال
    optimal_workers = optimizer.calculate_optimal_workers("cpu_intensive", 200)
    print(f"Optimal workers for CPU intensive tasks: {optimal_workers}")
    
    # تحسين للمعالجة على نطاق واسع
    recommendations = optimizer.optimize_for_large_scale(5000, 2.0)
    print(f"\nOptimization recommendations for 5000 images:")
    print(f"Optimal workers: {recommendations['optimal_workers']}")
    print(f"Batch size: {recommendations['batch_size']}")
    print(f"Processing strategy: {recommendations['processing_strategy']}")
    print(f"Estimated time: {recommendations['estimated_time']:.1f} seconds")
    
    # تحسين الذاكرة
    memory_results = optimizer.optimize_memory_usage()
    print(f"\nMemory optimization results: {memory_results}")
    
    return recommendations

def test_large_scale_processing():
    """اختبار المعالجة على نطاق واسع"""
    print("\n" + "="*60)
    print("Testing Large Scale Processing")
    print("="*60)
    
    # إنشاء مجموعة بيانات كبيرة
    test_dir = create_large_test_dataset(100)
    
    # إنشاء محسن الأداء
    optimizer = PerformanceOptimizer()
    
    # الحصول على التوصيات
    recommendations = optimizer.optimize_for_large_scale(100, 2.0)
    
    # إنشاء معالج الصور الانتقائي
    processor = SelectiveProcessor(
        max_workers=recommendations['optimal_workers'],
        use_multiprocessing=(recommendations['processing_strategy'] == 'parallel_multiprocessing')
    )
    
    # دالة callback لتتبع التقدم
    def progress_callback(progress, processed, total):
        print(f"\rProgress: {progress:.1f}% ({processed}/{total})", end='', flush=True)
    
    processor.set_progress_callback(progress_callback)
    
    # إنشاء مجلد الإخراج
    output_dir = Path("large_scale_output")
    output_dir.mkdir(exist_ok=True)
    
    # اختيار الصور
    selected_images = processor.select_images_interactive(test_dir, 50)
    print(f"\nSelected {len(selected_images)} images for processing")
    
    # معالجة الصور
    start_time = time.time()
    results = processor.process_selected_images(
        selected_images,
        output_dir,
        save_enhanced=True,
        structure_type="by_date"
    )
    end_time = time.time()
    
    print(f"\n\nLarge scale processing completed in {end_time - start_time:.2f} seconds")
    
    # إنشاء تقرير الأداء
    performance_report = optimizer.create_performance_report(results)
    print(f"\nPerformance Report:")
    print(f"Total items: {performance_report['total_items']}")
    print(f"Success rate: {performance_report['success_rate']:.1f}%")
    print(f"Throughput: {performance_report['throughput']:.2f} items/second")
    
    return results

def main():
    """الدالة الرئيسية"""
    print("Selective Processing Test Suite")
    print("="*60)
    
    try:
        # 1. اختبار المعالجة الانتقائية
        results1 = test_selective_processing()
        
        # 2. اختبار إدارة المجلدات
        test_dir = test_folder_management()
        
        # 3. اختبار تحسين الأداء
        recommendations = test_performance_optimization()
        
        # 4. اختبار المعالجة على نطاق واسع
        results2 = test_large_scale_processing()
        
        print("\n" + "="*60)
        print("All tests completed successfully!")
        print("="*60)
        print("\nFiles and directories created:")
        print("- large_test_dataset/: Test images")
        print("- selective_output/: Selective processing results")
        print("- folder_test/: Folder management test")
        print("- large_scale_output/: Large scale processing results")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
