#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
معالج الصور الانتقائي
Selective Image Processor
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
from typing import List, Dict, Optional, Callable

class SelectiveProcessor:
    def __init__(self, max_workers=4, use_multiprocessing=False):
        """
        تهيئة معالج الصور الانتقائي
        
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
        self.selected_images = []
        
        # إعداد logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('selective_processing.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def set_progress_callback(self, callback: Callable):
        """تعيين دالة callback لتتبع التقدم"""
        self.progress_callback = callback
    
    def get_supported_formats(self):
        """الحصول على صيغ الصور المدعومة"""
        return ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
    
    def find_images_in_directory(self, directory: Path, recursive: bool = True) -> List[Path]:
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
    
    def select_images_by_pattern(self, directory: Path, pattern: str, recursive: bool = True) -> List[Path]:
        """اختيار الصور بناءً على نمط معين"""
        all_images = self.find_images_in_directory(directory, recursive)
        selected = []
        
        for image_path in all_images:
            if pattern.lower() in image_path.name.lower():
                selected.append(image_path)
        
        return selected
    
    def select_images_by_size(self, directory: Path, min_size: int = 0, max_size: int = float('inf'), 
                            recursive: bool = True) -> List[Path]:
        """اختيار الصور بناءً على الحجم"""
        all_images = self.find_images_in_directory(directory, recursive)
        selected = []
        
        for image_path in all_images:
            try:
                file_size = image_path.stat().st_size
                if min_size <= file_size <= max_size:
                    selected.append(image_path)
            except OSError:
                continue
        
        return selected
    
    def select_images_by_date(self, directory: Path, start_date: datetime = None, 
                            end_date: datetime = None, recursive: bool = True) -> List[Path]:
        """اختيار الصور بناءً على تاريخ الإنشاء"""
        all_images = self.find_images_in_directory(directory, recursive)
        selected = []
        
        for image_path in all_images:
            try:
                file_time = datetime.fromtimestamp(image_path.stat().st_mtime)
                if start_date and file_time < start_date:
                    continue
                if end_date and file_time > end_date:
                    continue
                selected.append(image_path)
            except OSError:
                continue
        
        return selected
    
    def select_images_by_list(self, image_paths: List[str]) -> List[Path]:
        """اختيار الصور من قائمة مسارات"""
        selected = []
        
        for path_str in image_paths:
            path = Path(path_str)
            if path.exists() and path.suffix.lower() in self.get_supported_formats():
                selected.append(path)
            else:
                self.logger.warning(f"صورة غير موجودة أو غير مدعومة: {path}")
        
        return selected
    
    def select_images_interactive(self, directory: Path, max_images: int = 5000) -> List[Path]:
        """اختيار الصور بشكل تفاعلي"""
        all_images = self.find_images_in_directory(directory, True)
        
        if len(all_images) <= max_images:
            return all_images
        
        # إذا كان عدد الصور أكبر من الحد الأقصى، اختر عشوائياً
        import random
        return random.sample(all_images, max_images)
    
    def create_output_structure(self, base_output_dir: Path, structure_type: str = "flat") -> Path:
        """
        إنشاء هيكل مجلدات الإخراج
        
        Args:
            base_output_dir: المجلد الأساسي للإخراج
            structure_type: نوع الهيكل ("flat", "by_date", "by_name", "by_size")
        """
        base_output_dir = Path(base_output_dir)
        base_output_dir.mkdir(parents=True, exist_ok=True)
        
        if structure_type == "flat":
            return base_output_dir
        
        elif structure_type == "by_date":
            date_folder = datetime.now().strftime("%Y-%m-%d")
            output_dir = base_output_dir / date_folder
            output_dir.mkdir(exist_ok=True)
            return output_dir
        
        elif structure_type == "by_name":
            name_folder = "selected_images"
            output_dir = base_output_dir / name_folder
            output_dir.mkdir(exist_ok=True)
            return output_dir
        
        elif structure_type == "by_size":
            size_folder = f"batch_{len(self.selected_images)}"
            output_dir = base_output_dir / size_folder
            output_dir.mkdir(exist_ok=True)
            return output_dir
        
        return base_output_dir
    
    def process_single_image(self, image_path: Path, output_dir: Path = None, 
                           save_enhanced: bool = True, custom_filename: str = None) -> Dict:
        """
        معالجة صورة واحدة
        
        Args:
            image_path: مسار الصورة
            output_dir: مجلد الحفظ
            save_enhanced: حفظ الصورة المحسنة
            custom_filename: اسم ملف مخصص
        
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
                
                if custom_filename:
                    enhanced_filename = custom_filename
                else:
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
    
    def process_selected_images(self, selected_images: List[Path], output_dir: Path = None, 
                              save_enhanced: bool = True, structure_type: str = "flat") -> List[Dict]:
        """
        معالجة الصور المختارة
        
        Args:
            selected_images: قائمة الصور المختارة
            output_dir: مجلد الحفظ
            save_enhanced: حفظ الصور المحسنة
            structure_type: نوع هيكل المجلدات
        
        Returns:
            list: قائمة النتائج
        """
        self.selected_images = selected_images
        self.total_images = len(selected_images)
        self.processed_images = 0
        self.results = []
        
        if not selected_images:
            self.logger.warning("لا توجد صور مختارة للمعالجة")
            return []
        
        self.logger.info(f"بدء معالجة {self.total_images} صورة مختارة")
        
        # إنشاء هيكل مجلدات الإخراج
        if output_dir:
            final_output_dir = self.create_output_structure(output_dir, structure_type)
        else:
            final_output_dir = None
        
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
                    final_output_dir, 
                    save_enhanced
                ): path for path in selected_images
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
    
    def save_results(self, results: List[Dict], output_file: Path, format: str = 'json'):
        """حفظ النتائج في ملف"""
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
                f.write("نتائج معالجة الصور المختارة\n")
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
    
    def get_statistics(self, results: List[Dict]) -> Dict:
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
    
    def print_statistics(self, results: List[Dict]):
        """طباعة الإحصائيات"""
        stats = self.get_statistics(results)
        
        print("\n" + "=" * 60)
        print("Selective Processing Statistics")
        print("=" * 60)
        print(f"Total selected images: {stats['total_images']}")
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
    parser = argparse.ArgumentParser(description='معالج الصور الانتقائي')
    parser.add_argument('input', help='مسار الصورة أو المجلد')
    parser.add_argument('-o', '--output', help='مجلد الحفظ')
    parser.add_argument('-p', '--pattern', help='نمط اختيار الصور')
    parser.add_argument('-s', '--size', help='حجم الصور (min-max)')
    parser.add_argument('-d', '--date', help='تاريخ الصور (start-end)')
    parser.add_argument('-l', '--list', help='قائمة مسارات الصور')
    parser.add_argument('-m', '--max', type=int, default=5000, help='الحد الأقصى للصور')
    parser.add_argument('-r', '--recursive', action='store_true', 
                       help='البحث في المجلدات الفرعية')
    parser.add_argument('-w', '--workers', type=int, default=4,
                       help='عدد العمال المتوازيين')
    parser.add_argument('--multiprocessing', action='store_true',
                       help='استخدام multiprocessing بدلاً من threading')
    parser.add_argument('--no-save', action='store_true',
                       help='عدم حفظ الصور المحسنة')
    parser.add_argument('--structure', choices=['flat', 'by_date', 'by_name', 'by_size'], 
                       default='flat', help='نوع هيكل مجلدات الإخراج')
    parser.add_argument('--format', choices=['json', 'csv', 'txt'], 
                       default='json', help='تنسيق ملف النتائج')
    
    args = parser.parse_args()
    
    # إنشاء معالج الصور الانتقائي
    processor = SelectiveProcessor(
        max_workers=args.workers,
        use_multiprocessing=args.multiprocessing
    )
    
    # تعيين callback للتقدم
    processor.set_progress_callback(progress_callback)
    
    # تحديد الصور المختارة
    input_path = Path(args.input)
    selected_images = []
    
    if input_path.is_file():
        # معالجة صورة واحدة
        selected_images = [input_path]
    elif input_path.is_dir():
        # اختيار الصور بناءً على المعايير
        if args.pattern:
            selected_images = processor.select_images_by_pattern(input_path, args.pattern, args.recursive)
        elif args.size:
            min_size, max_size = map(int, args.size.split('-'))
            selected_images = processor.select_images_by_size(input_path, min_size, max_size, args.recursive)
        elif args.list:
            with open(args.list, 'r') as f:
                image_paths = [line.strip() for line in f if line.strip()]
            selected_images = processor.select_images_by_list(image_paths)
        else:
            # اختيار جميع الصور مع حد أقصى
            all_images = processor.find_images_in_directory(input_path, args.recursive)
            if len(all_images) > args.max:
                selected_images = processor.select_images_interactive(input_path, args.max)
            else:
                selected_images = all_images
    else:
        print(f"خطأ: المسار غير صحيح: {input_path}")
        return
    
    if not selected_images:
        print("لم يتم العثور على صور للمعالجة")
        return
    
    print(f"تم اختيار {len(selected_images)} صورة للمعالجة")
    
    # معالجة الصور المختارة
    results = processor.process_selected_images(
        selected_images,
        args.output,
        not args.no_save,
        args.structure
    )
    
    # طباعة الإحصائيات
    processor.print_statistics(results)
    
    # حفظ النتائج
    if args.output:
        output_dir = Path(args.output)
        results_file = output_dir / f"selective_results.{args.format}"
        processor.save_results(results, results_file, args.format)
        print(f"\nتم حفظ النتائج في: {results_file}")

if __name__ == "__main__":
    main()
