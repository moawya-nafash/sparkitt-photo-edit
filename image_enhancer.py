#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
برنامج تحسين الصور للتعرف على النصوص
Image Enhancement for OCR/Text Recognition
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance
import matplotlib.pyplot as plt
from skimage import filters, restoration, exposure
import easyocr
import pytesseract
import os
from pathlib import Path
import argparse

class ImageEnhancer:
    def __init__(self):
        """تهيئة معزز الصور"""
        self.reader = easyocr.Reader(['ar', 'en'])  # دعم العربية والإنجليزية
        
    def load_image(self, image_path):
        """تحميل الصورة"""
        try:
            # تحميل الصورة باستخدام OpenCV
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"لا يمكن تحميل الصورة: {image_path}")
            return image
        except Exception as e:
            print(f"خطأ في تحميل الصورة: {e}")
            return None
    
    def preprocess_image(self, image):
        """معالجة أولية للصورة"""
        # تحويل إلى grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        return gray
    
    def remove_noise(self, image):
        """إزالة الضوضاء من الصورة"""
        # استخدام Gaussian blur لإزالة الضوضاء
        denoised = cv2.GaussianBlur(image, (3, 3), 0)
        
        # استخدام Median filter لإزالة الضوضاء الإضافية
        denoised = cv2.medianBlur(denoised, 3)
        
        return denoised
    
    def enhance_contrast(self, image):
        """تحسين التباين باستخدام CLAHE"""
        # تطبيق CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        
        return enhanced
    
    def apply_threshold(self, image, method='adaptive'):
        """تطبيق thresholding لتحويل الصورة إلى أبيض وأسود"""
        if method == 'adaptive':
            # Adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
        elif method == 'otsu':
            # Otsu's thresholding
            _, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            # Simple thresholding
            _, thresh = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
        
        return thresh
    
    def sharpen_image(self, image):
        """توضيح الصورة"""
        # إنشاء kernel للتوضيح
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        
        # تطبيق التوضيح
        sharpened = cv2.filter2D(image, -1, kernel)
        
        # التأكد من أن القيم في النطاق الصحيح
        sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
        
        return sharpened
    
    def enhance_image_pipeline(self, image):
        """خط أنابيب تحسين الصورة الكامل"""
        print("بدء معالجة الصورة...")
        
        # 1. معالجة أولية
        processed = self.preprocess_image(image)
        print("✓ تحويل إلى grayscale")
        
        # 2. إزالة الضوضاء
        processed = self.remove_noise(processed)
        print("✓ إزالة الضوضاء")
        
        # 3. تحسين التباين
        processed = self.enhance_contrast(processed)
        print("✓ تحسين التباين")
        
        # 4. تطبيق thresholding
        processed = self.apply_threshold(processed, method='adaptive')
        print("✓ تطبيق thresholding")
        
        # 5. توضيح الصورة
        processed = self.sharpen_image(processed)
        print("✓ توضيح الصورة")
        
        return processed
    
    def extract_text_easyocr(self, image):
        """استخراج النص باستخدام EasyOCR"""
        try:
            print("استخراج النص باستخدام EasyOCR...")
            results = self.reader.readtext(image)
            
            extracted_text = []
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # تصفية النتائج ذات الثقة المنخفضة
                    extracted_text.append({
                        'text': text,
                        'confidence': confidence,
                        'bbox': bbox
                    })
            
            return extracted_text
        except Exception as e:
            print(f"خطأ في EasyOCR: {e}")
            return []
    
    def extract_text_tesseract(self, image):
        """استخراج النص باستخدام Tesseract"""
        try:
            print("استخراج النص باستخدام Tesseract...")
            
            # إعداد Tesseract للعربية والإنجليزية
            custom_config = r'--oem 3 --psm 6 -l ara+eng'
            
            # استخراج النص
            text = pytesseract.image_to_string(image, config=custom_config)
            
            # الحصول على معلومات مفصلة
            data = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DICT)
            
            extracted_text = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 30 and data['text'][i].strip():
                    extracted_text.append({
                        'text': data['text'][i],
                        'confidence': int(data['conf'][i]) / 100.0,
                        'bbox': (data['left'][i], data['top'][i], 
                                data['width'][i], data['height'][i])
                    })
            
            return extracted_text
        except Exception as e:
            print(f"خطأ في Tesseract: {e}")
            return []
    
    def visualize_results(self, original, enhanced, easyocr_results, tesseract_results):
        """عرض النتائج بصرياً"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('نتائج تحسين الصورة واستخراج النصوص', fontsize=16, fontweight='bold')
        
        # الصورة الأصلية
        axes[0, 0].imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
        axes[0, 0].set_title('الصورة الأصلية')
        axes[0, 0].axis('off')
        
        # الصورة المحسنة
        axes[0, 1].imshow(enhanced, cmap='gray')
        axes[0, 1].set_title('الصورة المحسنة')
        axes[0, 1].axis('off')
        
        # نتائج EasyOCR
        axes[1, 0].imshow(enhanced, cmap='gray')
        axes[1, 0].set_title(f'نتائج EasyOCR ({len(easyocr_results)} نص)')
        axes[1, 0].axis('off')
        
        # رسم bounding boxes لـ EasyOCR
        for result in easyocr_results:
            bbox = result['bbox']
            pts = np.array(bbox, np.int32)
            pts = pts.reshape((-1, 1, 2))
            axes[1, 0].plot(pts[:, 0, 0], pts[:, 0, 1], 'r-', linewidth=2)
        
        # نتائج Tesseract
        axes[1, 1].imshow(enhanced, cmap='gray')
        axes[1, 1].set_title(f'نتائج Tesseract ({len(tesseract_results)} نص)')
        axes[1, 1].axis('off')
        
        # رسم bounding boxes لـ Tesseract
        for result in tesseract_results:
            bbox = result['bbox']
            x, y, w, h = bbox
            rect = plt.Rectangle((x, y), w, h, fill=False, edgecolor='blue', linewidth=2)
            axes[1, 1].add_patch(rect)
        
        plt.tight_layout()
        plt.show()
    
    def print_results(self, easyocr_results, tesseract_results):
        """طباعة النتائج في وحدة التحكم"""
        print("\n" + "="*60)
        print("نتائج استخراج النصوص")
        print("="*60)
        
        print("\n📝 نتائج EasyOCR:")
        print("-" * 30)
        if easyocr_results:
            for i, result in enumerate(easyocr_results, 1):
                print(f"{i}. النص: {result['text']}")
                print(f"   الثقة: {result['confidence']:.2%}")
                print()
        else:
            print("لم يتم العثور على نصوص")
        
        print("\n📝 نتائج Tesseract:")
        print("-" * 30)
        if tesseract_results:
            for i, result in enumerate(tesseract_results, 1):
                print(f"{i}. النص: {result['text']}")
                print(f"   الثقة: {result['confidence']:.2%}")
                print()
        else:
            print("لم يتم العثور على نصوص")
        
        print("\n📊 إحصائيات:")
        print(f"عدد النصوص المكتشفة بـ EasyOCR: {len(easyocr_results)}")
        print(f"عدد النصوص المكتشفة بـ Tesseract: {len(tesseract_results)}")
    
    def save_enhanced_image(self, enhanced_image, output_path):
        """حفظ الصورة المحسنة"""
        try:
            cv2.imwrite(output_path, enhanced_image)
            print(f"✓ تم حفظ الصورة المحسنة في: {output_path}")
        except Exception as e:
            print(f"خطأ في حفظ الصورة: {e}")
    
    def process_image(self, image_path, save_enhanced=True, show_results=True):
        """معالجة صورة واحدة كاملة"""
        print(f"معالجة الصورة: {image_path}")
        print("="*50)
        
        # تحميل الصورة
        original_image = self.load_image(image_path)
        if original_image is None:
            return
        
        # تحسين الصورة
        enhanced_image = self.enhance_image_pipeline(original_image)
        
        # استخراج النصوص
        easyocr_results = self.extract_text_easyocr(enhanced_image)
        tesseract_results = self.extract_text_tesseract(enhanced_image)
        
        # طباعة النتائج
        self.print_results(easyocr_results, tesseract_results)
        
        # حفظ الصورة المحسنة
        if save_enhanced:
            output_path = f"enhanced_{Path(image_path).name}"
            self.save_enhanced_image(enhanced_image, output_path)
        
        # عرض النتائج بصرياً
        if show_results:
            self.visualize_results(original_image, enhanced_image, 
                                 easyocr_results, tesseract_results)
        
        return {
            'enhanced_image': enhanced_image,
            'easyocr_results': easyocr_results,
            'tesseract_results': tesseract_results
        }

def main():
    """الدالة الرئيسية"""
    parser = argparse.ArgumentParser(description='برنامج تحسين الصور للتعرف على النصوص')
    parser.add_argument('image_path', help='مسار الصورة المراد معالجتها')
    parser.add_argument('--no-save', action='store_true', help='عدم حفظ الصورة المحسنة')
    parser.add_argument('--no-show', action='store_true', help='عدم عرض النتائج بصرياً')
    
    args = parser.parse_args()
    
    # التحقق من وجود الصورة
    if not os.path.exists(args.image_path):
        print(f"خطأ: الصورة غير موجودة: {args.image_path}")
        return
    
    # إنشاء معزز الصور
    enhancer = ImageEnhancer()
    
    # معالجة الصورة
    results = enhancer.process_image(
        args.image_path,
        save_enhanced=not args.no_save,
        show_results=not args.no_show
    )
    
    if results:
        print("\n✅ تمت معالجة الصورة بنجاح!")

if __name__ == "__main__":
    main()
