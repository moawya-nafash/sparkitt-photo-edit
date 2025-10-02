#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
معالج الصور المجمعة
Batch Image Processor
"""

import cv2
import numpy as np
import os
import json
import csv
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import threading
import time
from datetime import datetime
import argparse
from image_enhancer import ImageEnhancer
import logging

class BatchProcessor:
    def __init__(self, max_workers=4, use_multiprocessing=False):
        """
        تهيئة معالج الصور المجمعة
        
        Args:
            max_workers: عدد العمال المتوازيين
            use_multiprocessing: استخدام multiprocessing بدلاً من threading
        """
        self.max_workers = max_workers
        self.use_multiprocessing = use_multiprocessing
        self.enhancer = ImageEnhancer()
        self.results = []
        self.progress_callback = None
        self.total_images = 0
        self.processed_images = 0
        
        # إعداد logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('batch_processing.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def set_progress_callback(self, callback):
        """تعيين دالة callback لتتبع التقدم"""
        self.progress_callback = callback
    
    def get_supported_formats(self):
        """الحصول على صيغ الصور المدعومة"""
        return ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
    
    def find_images_in_directory(self, directory, recursive=True):
        """البحث عن الصور في مجلد"""
        directory = Path(directory)
        if not directory.exists():
            raise ValueError(f"المجلد غير موجود: {directory}")
        
        supported_formats = self.get_supported_formats()
        images = []
        
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"
        
        for file_path in directory.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in supported_formats:
                images.append(file_path)
        
        return sorted(images)
    
    def process_single_image(self, image_path, output_dir=None, save_enhanced=True):
        """
        معالجة صورة واحدة
        
        Args:
            image_path: مسار الصورة
            output_dir: مجلد الحفظ (اختياري)
            save_enhanced: حفظ الصورة المحسنة
        
        Returns:
            dict: نتائج المعالجة
        """
        try:
            image_path = Path(image_path)
            start_time = time.time()
            
            # تحميل الصورة
            image = self.enhancer.load_image(str(image_path))
            if image is None:
                return {
                    'image_path': str(image_path),
                    'status': 'failed',
                    'error': 'لا يمكن تحميل الصورة',
                    'processing_time': 0
                }
            
            # تحسين الصورة
            enhanced_image = self.enhancer.enhance_image_pipeline(image)
            
            # استخراج النصوص
            easyocr_results = self.enhancer.extract_text_easyocr(enhanced_image)
            tesseract_results = self.enhancer.extract_text_tesseract(enhanced_image)
            
            # حفظ الصورة المحسنة
            enhanced_path = None
            if save_enhanced and output_dir:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                enhanced_filename = f"enhanced_{image_path.name}"
                enhanced_path = output_dir / enhanced_filename
                cv2.imwrite(str(enhanced_path), enhanced_image)
            
            processing_time = time.time() - start_time
            
            result = {
                'image_path': str(image_path),
                'enhanced_path': str(enhanced_path) if enhanced_path else None,
                'status': 'success',
                'processing_time': processing_time,
                'easyocr_results': easyocr_results,
                'tesseract_results': tesseract_results,
                'total_texts_found': len(easyocr_results) + len(tesseract_results),
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"تمت معالجة الصورة: {image_path.name} في {processing_time:.2f} ثانية")
            return result
            
        except Exception as e:
            error_msg = f"خطأ في معالجة الصورة {image_path}: {str(e)}"
            self.logger.error(error_msg)
            return {
                'image_path': str(image_path),
                'status': 'failed',
                'error': str(e),
                'processing_time': 0,
                'timestamp': datetime.now().isoformat()
            }
    
    def process_images_batch(self, image_paths, output_dir=None, save_enhanced=True):
        """
        معالجة مجموعة من الصور
        
        Args:
            image_paths: قائمة مسارات الصور
            output_dir: مجلد الحفظ
            save_enhanced: حفظ الصور المحسنة
        
        Returns:
            list: قائمة النتائج
        """
        self.total_images = len(image_paths)
        self.processed_images = 0
        self.results = []
        
        self.logger.info(f"بدء معالجة {self.total_images} صورة")
        
        # اختيار نوع المعالجة المتوازية
        if self.use_multiprocessing:
            executor_class = ProcessPoolExecutor
        else:
            executor_class = ThreadPoolExecutor
        
        with executor_class(max_workers=self.max_workers) as executor:
            # إرسال المهام
            future_to_path = {
                executor.submit(
                    self.process_single_image, 
                    path, 
                    output_dir, 
                    save_enhanced
                ): path for path in image_paths
            }
            
            # جمع النتائج
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    result = future.result()
                    self.results.append(result)
                    self.processed_images += 1
                    
                    # تحديث التقدم
                    if self.progress_callback:
                        progress = (self.processed_images / self.total_images) * 100
                        self.progress_callback(progress, self.processed_images, self.total_images)
                    
                except Exception as e:
                    error_result = {
                        'image_path': str(path),
                        'status': 'failed',
                        'error': str(e),
                        'processing_time': 0,
                        'timestamp': datetime.now().isoformat()
                    }
                    self.results.append(error_result)
                    self.processed_images += 1
                    self.logger.error(f"خطأ في معالجة {path}: {e}")
        
        self.logger.info(f"تمت معالجة {self.processed_images} من {self.total_images} صورة")
        return self.results
    
    def process_directory(self, input_dir, output_dir=None, recursive=True, save_enhanced=True):
        """
        معالجة جميع الصور في مجلد
        
        Args:
            input_dir: مجلد الصور المدخلة
            output_dir: مجلد الحفظ
            recursive: البحث في المجلدات الفرعية
            save_enhanced: حفظ الصور المحسنة
        
        Returns:
            list: قائمة النتائج
        """
        # البحث عن الصور
        image_paths = self.find_images_in_directory(input_dir, recursive)
        
        if not image_paths:
            self.logger.warning(f"لم يتم العثور على صور في {input_dir}")
            return []
        
        self.logger.info(f"تم العثور على {len(image_paths)} صورة")
        
        # معالجة الصور
        return self.process_images_batch(image_paths, output_dir, save_enhanced)
    
    def save_results(self, results, output_file, format='json'):
        """
        حفظ النتائج في ملف
        
        Args:
            results: قائمة النتائج
            output_file: مسار ملف الحفظ
            format: تنسيق الحفظ ('json', 'csv', 'txt')
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
        
        elif format.lower() == 'csv':
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                if results:
                    writer = csv.DictWriter(f, fieldnames=results[0].keys())
                    writer.writeheader()
                    writer.writerows(results)
        
        elif format.lower() == 'txt':
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("نتائج معالجة الصور المجمعة\n")
                f.write("=" * 50 + "\n\n")
                
                for i, result in enumerate(results, 1):
                    f.write(f"الصورة {i}: {Path(result['image_path']).name}\n")
                    f.write(f"الحالة: {result['status']}\n")
                    f.write(f"وقت المعالجة: {result['processing_time']:.2f} ثانية\n")
                    
                    if result['status'] == 'success':
                        f.write(f"عدد النصوص المكتشفة: {result['total_texts_found']}\n")
                        
                        if result['easyocr_results']:
                            f.write("نتائج EasyOCR:\n")
                            for j, text_result in enumerate(result['easyocr_results'], 1):
                                f.write(f"  {j}. {text_result['text']} (الثقة: {text_result['confidence']:.2%})\n")
                        
                        if result['tesseract_results']:
                            f.write("نتائج Tesseract:\n")
                            for j, text_result in enumerate(result['tesseract_results'], 1):
                                f.write(f"  {j}. {text_result['text']} (الثقة: {text_result['confidence']:.2%})\n")
                    else:
                        f.write(f"الخطأ: {result['error']}\n")
                    
                    f.write("\n" + "-" * 30 + "\n\n")
        
        self.logger.info(f"تم حفظ النتائج في: {output_path}")
    
    def get_statistics(self, results):
        """الحصول على إحصائيات النتائج"""
        if not results:
            return {}
        
        total_images = len(results)
        successful = sum(1 for r in results if r['status'] == 'success')
        failed = total_images - successful
        
        total_processing_time = sum(r['processing_time'] for r in results)
        avg_processing_time = total_processing_time / total_images if total_images > 0 else 0
        
        total_texts = sum(r.get('total_texts_found', 0) for r in results if r['status'] == 'success')
        
        return {
            'total_images': total_images,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total_images) * 100 if total_images > 0 else 0,
            'total_processing_time': total_processing_time,
            'average_processing_time': avg_processing_time,
            'total_texts_found': total_texts,
            'average_texts_per_image': total_texts / successful if successful > 0 else 0
        }
    
    def print_statistics(self, results):
        """طباعة الإحصائيات"""
        stats = self.get_statistics(results)
        
        print("\n" + "=" * 60)
        print("Batch Processing Statistics")
        print("=" * 60)
        print(f"Total images: {stats['total_images']}")
        print(f"Successful: {stats['successful']}")
        print(f"Failed: {stats['failed']}")
        print(f"Success rate: {stats['success_rate']:.1f}%")
        print(f"Total processing time: {stats['total_processing_time']:.2f} seconds")
        print(f"Average processing time: {stats['average_processing_time']:.2f} seconds")
        print(f"Total texts found: {stats['total_texts_found']}")
        print(f"Average texts per image: {stats['average_texts_per_image']:.1f}")
        print("=" * 60)

def progress_callback(progress, processed, total):
    """دالة callback لتتبع التقدم"""
    print(f"\rProgress: {progress:.1f}% ({processed}/{total})", end='', flush=True)

def main():
    """الدالة الرئيسية"""
    parser = argparse.ArgumentParser(description='معالج الصور المجمعة')
    parser.add_argument('input', help='مسار الصورة أو المجلد')
    parser.add_argument('-o', '--output', help='مجلد الحفظ')
    parser.add_argument('-r', '--recursive', action='store_true', 
                       help='البحث في المجلدات الفرعية')
    parser.add_argument('-w', '--workers', type=int, default=4,
                       help='عدد العمال المتوازيين')
    parser.add_argument('--multiprocessing', action='store_true',
                       help='استخدام multiprocessing بدلاً من threading')
    parser.add_argument('--no-save', action='store_true',
                       help='عدم حفظ الصور المحسنة')
    parser.add_argument('--format', choices=['json', 'csv', 'txt'], 
                       default='json', help='تنسيق ملف النتائج')
    
    args = parser.parse_args()
    
    # إنشاء معالج الصور المجمعة
    processor = BatchProcessor(
        max_workers=args.workers,
        use_multiprocessing=args.multiprocessing
    )
    
    # تعيين callback للتقدم
    processor.set_progress_callback(progress_callback)
    
    # تحديد نوع المدخل
    input_path = Path(args.input)
    
    if input_path.is_file():
        # معالجة صورة واحدة
        print(f"معالجة صورة واحدة: {input_path}")
        results = [processor.process_single_image(
            input_path, 
            args.output, 
            not args.no_save
        )]
    elif input_path.is_dir():
        # معالجة مجلد
        print(f"معالجة مجلد: {input_path}")
        results = processor.process_directory(
            input_path,
            args.output,
            args.recursive,
            not args.no_save
        )
    else:
        print(f"خطأ: المسار غير صحيح: {input_path}")
        return
    
    # طباعة الإحصائيات
    processor.print_statistics(results)
    
    # حفظ النتائج
    if args.output:
        output_dir = Path(args.output)
        results_file = output_dir / f"results.{args.format}"
        processor.save_results(results, results_file, args.format)
        print(f"\nتم حفظ النتائج في: {results_file}")

if __name__ == "__main__":
    main()
