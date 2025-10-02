#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مثال توضيحي لاستخدام برنامج تحسين الصور
Demo script for Image Enhancement
"""

import cv2
import numpy as np
from image_enhancer import ImageEnhancer
import matplotlib.pyplot as plt

def create_sample_text_image():
    """إنشاء صورة نصية تجريبية"""
    # إنشاء صورة بيضاء
    img = np.ones((400, 800, 3), dtype=np.uint8) * 255
    
    # إضافة نصوص
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # نص عربي
    cv2.putText(img, 'مرحبا بك في برنامج تحسين الصور', (50, 100), 
                font, 1, (0, 0, 0), 2, cv2.LINE_AA)
    
    # نص إنجليزي
    cv2.putText(img, 'Welcome to Image Enhancement Program', (50, 150), 
                font, 1, (0, 0, 0), 2, cv2.LINE_AA)
    
    # أرقام
    cv2.putText(img, '1234567890', (50, 200), 
                font, 1, (0, 0, 0), 2, cv2.LINE_AA)
    
    # إضافة بعض الضوضاء
    noise = np.random.randint(0, 50, img.shape, dtype=np.uint8)
    img = cv2.add(img, noise)
    
    # إضافة تموج
    rows, cols = img.shape[:2]
    for i in range(rows):
        for j in range(cols):
            offset_x = int(3 * np.sin(i * 0.1))
            offset_y = int(2 * np.cos(j * 0.1))
            if 0 <= i + offset_y < rows and 0 <= j + offset_x < cols:
                img[i, j] = img[i + offset_y, j + offset_x]
    
    return img

def demo_basic_usage():
    """مثال على الاستخدام الأساسي"""
    print("="*60)
    print("مثال على الاستخدام الأساسي")
    print("="*60)
    
    # إنشاء صورة تجريبية
    print("إنشاء صورة نصية تجريبية...")
    sample_image = create_sample_text_image()
    
    # حفظ الصورة التجريبية
    cv2.imwrite("sample_text.png", sample_image)
    print("تم حفظ الصورة التجريبية: sample_text.png")
    
    # إنشاء معزز الصور
    enhancer = ImageEnhancer()
    
    # معالجة الصورة
    print("\nبدء معالجة الصورة...")
    results = enhancer.process_image("sample_text.png", save_enhanced=True, show_results=False)
    
    if results:
        print("\nتمت المعالجة بنجاح!")
        print(f"عدد النصوص المكتشفة بـ EasyOCR: {len(results['easyocr_results'])}")
        print(f"عدد النصوص المكتشفة بـ Tesseract: {len(results['tesseract_results'])}")
    
    return results

def demo_step_by_step():
    """مثال على المعالجة خطوة بخطوة"""
    print("\n" + "="*60)
    print("مثال على المعالجة خطوة بخطوة")
    print("="*60)
    
    # تحميل الصورة
    image = cv2.imread("sample_text.png")
    if image is None:
        print("خطأ: لم يتم العثور على الصورة التجريبية")
        return
    
    enhancer = ImageEnhancer()
    
    # خطوات المعالجة
    steps = []
    step_names = []
    
    # 1. الصورة الأصلية
    steps.append(image.copy())
    step_names.append("الصورة الأصلية")
    
    # 2. تحويل إلى grayscale
    gray = enhancer.preprocess_image(image)
    steps.append(gray)
    step_names.append("تحويل إلى Grayscale")
    
    # 3. إزالة الضوضاء
    denoised = enhancer.remove_noise(gray)
    steps.append(denoised)
    step_names.append("إزالة الضوضاء")
    
    # 4. تحسين التباين
    enhanced = enhancer.enhance_contrast(denoised)
    steps.append(enhanced)
    step_names.append("تحسين التباين")
    
    # 5. تطبيق thresholding
    thresh = enhancer.apply_threshold(enhanced)
    steps.append(thresh)
    step_names.append("تطبيق Thresholding")
    
    # 6. توضيح الصورة
    sharpened = enhancer.sharpen_image(thresh)
    steps.append(sharpened)
    step_names.append("توضيح الصورة")
    
    # عرض النتائج
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('خطوات معالجة الصورة', fontsize=16, fontweight='bold')
    
    for i, (step, name) in enumerate(zip(steps, step_names)):
        row = i // 3
        col = i % 3
        
        if len(step.shape) == 3:
            axes[row, col].imshow(cv2.cvtColor(step, cv2.COLOR_BGR2RGB))
        else:
            axes[row, col].imshow(step, cmap='gray')
        
        axes[row, col].set_title(name)
        axes[row, col].axis('off')
    
    plt.tight_layout()
    plt.show()
    
    return sharpened

def demo_ocr_comparison():
    """مقارنة بين EasyOCR و Tesseract"""
    print("\n" + "="*60)
    print("مقارنة بين EasyOCR و Tesseract")
    print("="*60)
    
    # تحميل الصورة المحسنة
    enhanced_image = cv2.imread("enhanced_sample_text.png", cv2.IMREAD_GRAYSCALE)
    if enhanced_image is None:
        print("خطأ: لم يتم العثور على الصورة المحسنة")
        return
    
    enhancer = ImageEnhancer()
    
    # استخراج النصوص
    print("استخراج النصوص باستخدام EasyOCR...")
    easyocr_results = enhancer.extract_text_easyocr(enhanced_image)
    
    print("استخراج النصوص باستخدام Tesseract...")
    tesseract_results = enhancer.extract_text_tesseract(enhanced_image)
    
    # مقارنة النتائج
    print("\n📊 مقارنة النتائج:")
    print("-" * 40)
    
    print(f"EasyOCR: {len(easyocr_results)} نص")
    for i, result in enumerate(easyocr_results, 1):
        print(f"  {i}. {result['text']} (الثقة: {result['confidence']:.2%})")
    
    print(f"\nTesseract: {len(tesseract_results)} نص")
    for i, result in enumerate(tesseract_results, 1):
        print(f"  {i}. {result['text']} (الثقة: {result['confidence']:.2%})")
    
    return easyocr_results, tesseract_results

def demo_custom_parameters():
    """مثال على استخدام معاملات مخصصة"""
    print("\n" + "="*60)
    print("مثال على استخدام معاملات مخصصة")
    print("="*60)
    
    # تحميل الصورة
    image = cv2.imread("sample_text.png")
    if image is None:
        print("خطأ: لم يتم العثور على الصورة التجريبية")
        return
    
    enhancer = ImageEnhancer()
    
    # معالجة مخصصة
    gray = enhancer.preprocess_image(image)
    
    # إزالة ضوضاء أقوى
    denoised = cv2.medianBlur(gray, 5)  # kernel أكبر
    
    # تحسين تباين أقوى
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)
    
    # thresholding مختلف
    thresh = enhancer.apply_threshold(enhanced, method='otsu')
    
    # حفظ النتيجة
    cv2.imwrite("custom_enhanced.png", thresh)
    print("تم حفظ الصورة المحسنة المخصصة: custom_enhanced.png")
    
    # استخراج النصوص
    easyocr_results = enhancer.extract_text_easyocr(thresh)
    print(f"عدد النصوص المكتشفة: {len(easyocr_results)}")
    
    return thresh

def main():
    """الدالة الرئيسية للتجربة"""
    print("بدء التجربة التوضيحية لبرنامج تحسين الصور")
    print("="*60)
    
    try:
        # 1. الاستخدام الأساسي
        results = demo_basic_usage()
        
        # 2. المعالجة خطوة بخطوة
        enhanced = demo_step_by_step()
        
        # 3. مقارنة OCR
        easyocr_results, tesseract_results = demo_ocr_comparison()
        
        # 4. معاملات مخصصة
        custom_enhanced = demo_custom_parameters()
        
        print("\n" + "="*60)
        print("تمت جميع التجارب بنجاح!")
        print("="*60)
        print("\nالملفات المُنشأة:")
        print("- sample_text.png: الصورة التجريبية")
        print("- enhanced_sample_text.png: الصورة المحسنة")
        print("- custom_enhanced.png: الصورة المحسنة المخصصة")
        
    except Exception as e:
        print(f"خطأ في التجربة: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
