#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار بسيط للمعالجة المجمعة
Simple test for batch processing
"""

import cv2
import numpy as np
import os
from pathlib import Path
from batch_processor import BatchProcessor
import time

def create_test_images():
    """إنشاء صور اختبار بسيطة"""
    print("Creating test images...")
    
    # إنشاء مجلد للصور التجريبية
    test_dir = Path("test_batch_images")
    test_dir.mkdir(exist_ok=True)
    
    # إنشاء 3 صور بسيطة
    for i in range(3):
        # إنشاء صورة بيضاء
        img = np.ones((300, 500, 3), dtype=np.uint8) * 255
        
        # إضافة نص
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, f'Test Image {i+1}', (50, 150), 
                    font, 1, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(img, '1234567890', (50, 200), 
                    font, 1, (0, 0, 0), 2, cv2.LINE_AA)
        
        # إضافة بعض الضوضاء
        noise = np.random.randint(0, 20, img.shape, dtype=np.uint8)
        img = cv2.add(img, noise)
        
        # حفظ الصورة
        filename = f"test_{i+1}.png"
        filepath = test_dir / filename
        cv2.imwrite(str(filepath), img)
        print(f"Created: {filename}")
    
    print(f"Created 3 test images in: {test_dir}")
    return test_dir

def test_batch_processing():
    """اختبار المعالجة المجمعة"""
    print("="*50)
    print("Testing Batch Processing")
    print("="*50)
    
    # إنشاء صور اختبار
    test_dir = create_test_images()
    
    # إنشاء معالج الصور المجمعة
    processor = BatchProcessor(max_workers=2, use_multiprocessing=False)
    
    # دالة callback لتتبع التقدم
    def progress_callback(progress, processed, total):
        print(f"\rProgress: {progress:.1f}% ({processed}/{total})", end='', flush=True)
    
    processor.set_progress_callback(progress_callback)
    
    # إنشاء مجلد الإخراج
    output_dir = Path("test_batch_output")
    output_dir.mkdir(exist_ok=True)
    
    print(f"\nProcessing images in: {test_dir}")
    print(f"Output directory: {output_dir}")
    
    # معالجة الصور
    start_time = time.time()
    results = processor.process_directory(
        test_dir,
        output_dir,
        recursive=False,
        save_enhanced=True
    )
    end_time = time.time()
    
    print(f"\n\nProcessing completed in {end_time - start_time:.2f} seconds")
    
    # طباعة الإحصائيات
    processor.print_statistics(results)
    
    # حفظ النتائج
    results_file = output_dir / "results.json"
    processor.save_results(results, results_file, 'json')
    print(f"\nResults saved to: {results_file}")
    
    return results

def test_single_image():
    """اختبار معالجة صورة واحدة"""
    print("\n" + "="*50)
    print("Testing Single Image Processing")
    print("="*50)
    
    # إنشاء صورة اختبار
    test_dir = create_test_images()
    test_image = test_dir / "test_1.png"
    
    # إنشاء معالج
    processor = BatchProcessor(max_workers=1)
    
    # معالجة الصورة
    print(f"Processing single image: {test_image}")
    result = processor.process_single_image(test_image, save_enhanced=True)
    
    print(f"Status: {result['status']}")
    print(f"Processing time: {result['processing_time']:.2f} seconds")
    
    if result['status'] == 'success':
        print(f"Texts found: {result['total_texts_found']}")
        print("EasyOCR results:")
        for i, text_result in enumerate(result['easyocr_results'], 1):
            print(f"  {i}. {text_result['text']} (confidence: {text_result['confidence']:.2%})")
    
    return result

def main():
    """الدالة الرئيسية"""
    print("Batch Processing Test")
    print("="*50)
    
    try:
        # اختبار المعالجة المجمعة
        results1 = test_batch_processing()
        
        # اختبار معالجة صورة واحدة
        result2 = test_single_image()
        
        print("\n" + "="*50)
        print("All tests completed successfully!")
        print("="*50)
        print("\nFiles created:")
        print("- test_batch_images/: Test images")
        print("- test_batch_output/: Batch processing results")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
