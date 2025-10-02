#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار بسيط للبرنامج
Simple test for the program
"""

import cv2
import numpy as np
import os

def create_test_image():
    """إنشاء صورة اختبار بسيطة"""
    # إنشاء صورة بيضاء
    img = np.ones((300, 600, 3), dtype=np.uint8) * 255
    
    # إضافة نص
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, 'Hello World', (50, 150), 
                font, 2, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(img, '1234567890', (50, 200), 
                font, 1, (0, 0, 0), 2, cv2.LINE_AA)
    
    return img

def test_basic_functionality():
    """اختبار الوظائف الأساسية"""
    print("Testing basic functionality...")
    
    # إنشاء صورة اختبار
    test_img = create_test_image()
    cv2.imwrite("test_image.png", test_img)
    print("Test image created: test_image.png")
    
    # اختبار تحميل الصورة
    loaded_img = cv2.imread("test_image.png")
    if loaded_img is not None:
        print("Image loading: OK")
    else:
        print("Image loading: FAILED")
        return False
    
    # اختبار تحويل إلى grayscale
    gray = cv2.cvtColor(loaded_img, cv2.COLOR_BGR2GRAY)
    if gray is not None:
        print("Grayscale conversion: OK")
    else:
        print("Grayscale conversion: FAILED")
        return False
    
    # اختبار إزالة الضوضاء
    denoised = cv2.GaussianBlur(gray, (3, 3), 0)
    if denoised is not None:
        print("Noise removal: OK")
    else:
        print("Noise removal: FAILED")
        return False
    
    # اختبار تحسين التباين
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)
    if enhanced is not None:
        print("Contrast enhancement: OK")
    else:
        print("Contrast enhancement: FAILED")
        return False
    
    # اختبار thresholding
    thresh = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                  cv2.THRESH_BINARY, 11, 2)
    if thresh is not None:
        print("Thresholding: OK")
    else:
        print("Thresholding: FAILED")
        return False
    
    # حفظ النتيجة
    cv2.imwrite("test_enhanced.png", thresh)
    print("Enhanced image saved: test_enhanced.png")
    
    return True

def test_imports():
    """اختبار استيراد المكتبات"""
    print("Testing imports...")
    
    try:
        import cv2
        print("OpenCV: OK")
    except ImportError:
        print("OpenCV: FAILED")
        return False
    
    try:
        import numpy as np
        print("NumPy: OK")
    except ImportError:
        print("NumPy: FAILED")
        return False
    
    try:
        from PIL import Image
        print("Pillow: OK")
    except ImportError:
        print("Pillow: FAILED")
        return False
    
    try:
        import matplotlib.pyplot as plt
        print("Matplotlib: OK")
    except ImportError:
        print("Matplotlib: FAILED")
        return False
    
    try:
        from skimage import filters
        print("Scikit-image: OK")
    except ImportError:
        print("Scikit-image: FAILED")
        return False
    
    try:
        import easyocr
        print("EasyOCR: OK")
    except ImportError:
        print("EasyOCR: FAILED")
        return False
    
    try:
        import pytesseract
        print("Pytesseract: OK")
    except ImportError:
        print("Pytesseract: FAILED")
        return False
    
    return True

def main():
    """الدالة الرئيسية"""
    print("="*50)
    print("Simple Test for Image Enhancement Program")
    print("="*50)
    
    # اختبار الاستيراد
    if not test_imports():
        print("\nSome imports failed. Please install missing packages.")
        return
    
    print("\nAll imports successful!")
    
    # اختبار الوظائف الأساسية
    if test_basic_functionality():
        print("\nBasic functionality test: PASSED")
    else:
        print("\nBasic functionality test: FAILED")
        return
    
    print("\n" + "="*50)
    print("All tests completed successfully!")
    print("="*50)
    print("\nFiles created:")
    print("- test_image.png: Original test image")
    print("- test_enhanced.png: Enhanced test image")

if __name__ == "__main__":
    main()
