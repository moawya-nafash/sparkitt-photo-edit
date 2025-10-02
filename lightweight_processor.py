#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
معالج خفيف للصور - بدون EasyOCR
Lightweight Image Processor - Without EasyOCR
"""

import cv2
import numpy as np
import os
from pathlib import Path
import argparse
import time

class LightweightProcessor:
    def __init__(self):
        """تهيئة المعالج الخفيف"""
        pass
    
    def load_image(self, image_path):
        """تحميل الصورة"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"لا يمكن تحميل الصورة: {image_path}")
            return image
        except Exception as e:
            print(f"خطأ في تحميل الصورة: {e}")
            return None
    
    def resize_image_if_needed(self, image, max_size=1024):
        """تغيير حجم الصورة إذا كانت كبيرة جداً"""
        height, width = image.shape[:2]
        
        if max(height, width) > max_size:
            ratio = max_size / max(height, width)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            
            resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            print(f"تم تغيير حجم الصورة من {width}x{height} إلى {new_width}x{new_height}")
            return resized
        
        return image
    
    def enhance_image(self, image):
        """تحسين الصورة"""
        try:
            # تحويل إلى grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # إزالة الضوضاء
            denoised = cv2.GaussianBlur(gray, (3, 3), 0)
            denoised = cv2.medianBlur(denoised, 3)
            
            # تحسين التباين
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)
            
            # تطبيق thresholding
            thresh = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY, 11, 2)
            
            # توضيح الصورة
            kernel = np.array([[-1,-1,-1], [-1, 9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(thresh, -1, kernel)
            sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
            
            return sharpened
            
        except Exception as e:
            print(f"خطأ في تحسين الصورة: {e}")
            return None
    
    def extract_text_tesseract(self, image):
        """استخراج النص باستخدام Tesseract فقط"""
        try:
            import pytesseract
            
            # إعداد Tesseract
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
            
            return extracted_text, text
            
        except Exception as e:
            print(f"خطأ في Tesseract: {e}")
            return [], ""
    
    def process_image(self, image_path, output_path=None, max_size=1024):
        """معالجة صورة واحدة"""
        print(f"معالجة الصورة: {image_path}")
        
        # تحميل الصورة
        image = self.load_image(image_path)
        if image is None:
            return None
        
        # تغيير الحجم إذا لزم الأمر
        image = self.resize_image_if_needed(image, max_size)
        
        # تحسين الصورة
        enhanced = self.enhance_image(image)
        if enhanced is None:
            return None
        
        # استخراج النصوص
        text_results, full_text = self.extract_text_tesseract(enhanced)
        
        # حفظ الصورة المحسنة
        if output_path:
            cv2.imwrite(output_path, enhanced)
            print(f"تم حفظ الصورة المحسنة في: {output_path}")
        
        # طباعة النتائج
        print("\n" + "="*50)
        print("نتائج استخراج النصوص")
        print("="*50)
        
        if text_results:
            print(f"عدد النصوص المكتشفة: {len(text_results)}")
            for i, result in enumerate(text_results, 1):
                print(f"{i}. النص: {result['text']}")
                print(f"   الثقة: {result['confidence']:.2%}")
                print()
        else:
            print("لم يتم العثور على نصوص")
        
        if full_text.strip():
            print("النص الكامل:")
            print("-" * 30)
            print(full_text)
        
        return {
            'enhanced_image': enhanced,
            'text_results': text_results,
            'full_text': full_text
        }
    
    def process_directory(self, input_dir, output_dir=None, max_size=1024):
        """معالجة مجلد كامل"""
        input_path = Path(input_dir)
        if not input_path.exists():
            print(f"المجلد غير موجود: {input_dir}")
            return
        
        # إنشاء مجلد الإخراج
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            output_path = input_path / "enhanced"
            output_path.mkdir(exist_ok=True)
        
        # البحث عن الصور
        supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
        images = []
        
        for file_path in input_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_formats:
                images.append(file_path)
        
        if not images:
            print("لم يتم العثور على صور في المجلد")
            return
        
        print(f"تم العثور على {len(images)} صورة")
        
        # معالجة الصور
        successful = 0
        failed = 0
        
        for i, image_path in enumerate(images, 1):
            try:
                print(f"\nمعالجة الصورة {i}/{len(images)}: {image_path.name}")
                
                # مسار الإخراج
                output_file = output_path / f"enhanced_{image_path.name}"
                
                # معالجة الصورة
                result = self.process_image(str(image_path), str(output_file), max_size)
                
                if result:
                    successful += 1
                else:
                    failed += 1
                    
            except Exception as e:
                print(f"خطأ في معالجة {image_path.name}: {e}")
                failed += 1
        
        print(f"\n" + "="*50)
        print("نتائج المعالجة")
        print("="*50)
        print(f"إجمالي الصور: {len(images)}")
        print(f"نجحت: {successful}")
        print(f"فشلت: {failed}")
        print(f"معدل النجاح: {(successful/len(images)*100):.1f}%")

def main():
    """الدالة الرئيسية"""
    parser = argparse.ArgumentParser(description='معالج خفيف للصور')
    parser.add_argument('input', help='مسار الصورة أو المجلد')
    parser.add_argument('-o', '--output', help='مسار الإخراج')
    parser.add_argument('-s', '--size', type=int, default=1024, help='الحد الأقصى لحجم الصورة')
    
    args = parser.parse_args()
    
    # إنشاء المعالج
    processor = LightweightProcessor()
    
    # تحديد نوع المدخل
    input_path = Path(args.input)
    
    if input_path.is_file():
        # معالجة صورة واحدة
        output_file = args.output or f"enhanced_{input_path.name}"
        processor.process_image(str(input_path), output_file, args.size)
    elif input_path.is_dir():
        # معالجة مجلد
        processor.process_directory(str(input_path), args.output, args.size)
    else:
        print(f"خطأ: المسار غير صحيح: {input_path}")

if __name__ == "__main__":
    main()
