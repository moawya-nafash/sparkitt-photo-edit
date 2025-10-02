#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مثال توضيحي للمعالجة المجمعة
Batch Processing Demo
"""

import cv2
import numpy as np
import os
from pathlib import Path
from batch_processor import BatchProcessor
import time

def create_sample_images(num_images=5):
    """إنشاء صور تجريبية متعددة"""
    print(f"إنشاء {num_images} صور تجريبية...")
    
    # إنشاء مجلد للصور التجريبية
    sample_dir = Path("sample_images")
    sample_dir.mkdir(exist_ok=True)
    
    # نصوص مختلفة للاختبار
    texts = [
        "مرحبا بك في برنامج تحسين الصور",
        "Welcome to Image Enhancement Program",
        "1234567890",
        "نص عربي مع أرقام 123",
        "English text with numbers 456",
        "مختلط Mixed Text 789",
        "وثيقة مهمة Document",
        "تقرير Report 2024",
        "ملاحظات Notes",
        "قائمة List Items"
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
        cv2.putText(img, f"Image {i+1}", (50, 200), font, 0.7, (100, 100, 100), 2, cv2.LINE_AA)
        
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
        filename = f"sample_{i+1:02d}.png"
        filepath = sample_dir / filename
        cv2.imwrite(str(filepath), img)
        print(f"تم إنشاء: {filename}")
    
    print(f"تم إنشاء {num_images} صورة في مجلد: {sample_dir}")
    return sample_dir

def demo_batch_processing():
    """مثال على المعالجة المجمعة"""
    print("="*60)
    print("مثال على المعالجة المجمعة")
    print("="*60)
    
    # إنشاء صور تجريبية
    sample_dir = create_sample_images(8)
    
    # إنشاء معالج الصور المجمعة
    processor = BatchProcessor(max_workers=4, use_multiprocessing=False)
    
    # دالة callback لتتبع التقدم
    def progress_callback(progress, processed, total):
        print(f"\rالتقدم: {progress:.1f}% ({processed}/{total})", end='', flush=True)
    
    processor.set_progress_callback(progress_callback)
    
    # إنشاء مجلد الإخراج
    output_dir = Path("batch_output")
    output_dir.mkdir(exist_ok=True)
    
    print(f"\nبدء معالجة الصور في: {sample_dir}")
    print(f"مجلد الإخراج: {output_dir}")
    
    # معالجة الصور
    start_time = time.time()
    results = processor.process_directory(
        sample_dir,
        output_dir,
        recursive=False,
        save_enhanced=True
    )
    end_time = time.time()
    
    print(f"\n\nتمت المعالجة في {end_time - start_time:.2f} ثانية")
    
    # طباعة الإحصائيات
    processor.print_statistics(results)
    
    # حفظ النتائج
    results_file = output_dir / "results.json"
    processor.save_results(results, results_file, 'json')
    print(f"\nتم حفظ النتائج في: {results_file}")
    
    return results

def demo_parallel_vs_sequential():
    """مقارنة المعالجة المتوازية مع المتسلسلة"""
    print("\n" + "="*60)
    print("مقارنة المعالجة المتوازية مع المتسلسلة")
    print("="*60)
    
    # إنشاء صور تجريبية
    sample_dir = create_sample_images(6)
    
    # إنشاء مجلدات الإخراج
    parallel_output = Path("parallel_output")
    sequential_output = Path("sequential_output")
    parallel_output.mkdir(exist_ok=True)
    sequential_output.mkdir(exist_ok=True)
    
    # المعالجة المتوازية
    print("\n1. المعالجة المتوازية (4 عمال):")
    parallel_processor = BatchProcessor(max_workers=4, use_multiprocessing=False)
    
    start_time = time.time()
    parallel_results = parallel_processor.process_directory(
        sample_dir, parallel_output, recursive=False, save_enhanced=True
    )
    parallel_time = time.time() - start_time
    
    print(f"الوقت: {parallel_time:.2f} ثانية")
    
    # المعالجة المتسلسلة
    print("\n2. المعالجة المتسلسلة (1 عامل):")
    sequential_processor = BatchProcessor(max_workers=1, use_multiprocessing=False)
    
    start_time = time.time()
    sequential_results = sequential_processor.process_directory(
        sample_dir, sequential_output, recursive=False, save_enhanced=True
    )
    sequential_time = time.time() - start_time
    
    print(f"الوقت: {sequential_time:.2f} ثانية")
    
    # مقارنة النتائج
    print("\n" + "="*40)
    print("مقارنة النتائج:")
    print("="*40)
    print(f"المعالجة المتوازية: {parallel_time:.2f} ثانية")
    print(f"المعالجة المتسلسلة: {sequential_time:.2f} ثانية")
    print(f"تحسن السرعة: {((sequential_time - parallel_time) / sequential_time) * 100:.1f}%")
    
    return parallel_results, sequential_results

def demo_multiprocessing_vs_threading():
    """مقارنة multiprocessing مع threading"""
    print("\n" + "="*60)
    print("مقارنة Multiprocessing مع Threading")
    print("="*60)
    
    # إنشاء صور تجريبية
    sample_dir = create_sample_images(4)
    
    # إنشاء مجلدات الإخراج
    threading_output = Path("threading_output")
    multiprocessing_output = Path("multiprocessing_output")
    threading_output.mkdir(exist_ok=True)
    multiprocessing_output.mkdir(exist_ok=True)
    
    # Threading
    print("\n1. Threading (4 عمال):")
    threading_processor = BatchProcessor(max_workers=4, use_multiprocessing=False)
    
    start_time = time.time()
    threading_results = threading_processor.process_directory(
        sample_dir, threading_output, recursive=False, save_enhanced=True
    )
    threading_time = time.time() - start_time
    
    print(f"الوقت: {threading_time:.2f} ثانية")
    
    # Multiprocessing
    print("\n2. Multiprocessing (4 عمال):")
    multiprocessing_processor = BatchProcessor(max_workers=4, use_multiprocessing=True)
    
    start_time = time.time()
    multiprocessing_results = multiprocessing_processor.process_directory(
        sample_dir, multiprocessing_output, recursive=False, save_enhanced=True
    )
    multiprocessing_time = time.time() - start_time
    
    print(f"الوقت: {multiprocessing_time:.2f} ثانية")
    
    # مقارنة النتائج
    print("\n" + "="*40)
    print("مقارنة النتائج:")
    print("="*40)
    print(f"Threading: {threading_time:.2f} ثانية")
    print(f"Multiprocessing: {multiprocessing_time:.2f} ثانية")
    
    if threading_time < multiprocessing_time:
        print(f"Threading أسرع بـ {((multiprocessing_time - threading_time) / multiprocessing_time) * 100:.1f}%")
    else:
        print(f"Multiprocessing أسرع بـ {((threading_time - multiprocessing_time) / threading_time) * 100:.1f}%")
    
    return threading_results, multiprocessing_results

def demo_different_formats():
    """مثال على تصدير النتائج بصيغ مختلفة"""
    print("\n" + "="*60)
    print("مثال على تصدير النتائج بصيغ مختلفة")
    print("="*60)
    
    # إنشاء صور تجريبية
    sample_dir = create_sample_images(3)
    
    # معالجة الصور
    processor = BatchProcessor(max_workers=2)
    results = processor.process_directory(sample_dir, recursive=False, save_enhanced=False)
    
    # إنشاء مجلد للنتائج
    results_dir = Path("export_results")
    results_dir.mkdir(exist_ok=True)
    
    # تصدير بصيغ مختلفة
    formats = ['json', 'csv', 'txt']
    
    for format_type in formats:
        output_file = results_dir / f"results.{format_type}"
        processor.save_results(results, output_file, format_type)
        print(f"تم تصدير النتائج بصيغة {format_type.upper()}: {output_file}")
    
    return results

def main():
    """الدالة الرئيسية"""
    print("بدء التجربة التوضيحية للمعالجة المجمعة")
    print("="*60)
    
    try:
        # 1. المعالجة المجمعة الأساسية
        results1 = demo_batch_processing()
        
        # 2. مقارنة المعالجة المتوازية مع المتسلسلة
        results2, results3 = demo_parallel_vs_sequential()
        
        # 3. مقارنة multiprocessing مع threading
        results4, results5 = demo_multiprocessing_vs_threading()
        
        # 4. تصدير النتائج بصيغ مختلفة
        results6 = demo_different_formats()
        
        print("\n" + "="*60)
        print("تمت جميع التجارب بنجاح!")
        print("="*60)
        print("\nالمجلدات والملفات المُنشأة:")
        print("- sample_images/: الصور التجريبية")
        print("- batch_output/: نتائج المعالجة المجمعة")
        print("- parallel_output/: نتائج المعالجة المتوازية")
        print("- sequential_output/: نتائج المعالجة المتسلسلة")
        print("- threading_output/: نتائج Threading")
        print("- multiprocessing_output/: نتائج Multiprocessing")
        print("- export_results/: النتائج بصيغ مختلفة")
        
    except Exception as e:
        print(f"خطأ في التجربة: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
