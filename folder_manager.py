#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير المجلدات والتنظيم
Folder Manager and Organization
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import json
import csv
from typing import List, Dict, Optional
import logging

class FolderManager:
    def __init__(self):
        """تهيئة مدير المجلدات"""
        self.logger = logging.getLogger(__name__)
    
    def create_output_structure(self, base_dir: Path, structure_type: str, 
                              metadata: Dict = None) -> Path:
        """
        إنشاء هيكل مجلدات الإخراج
        
        Args:
            base_dir: المجلد الأساسي
            structure_type: نوع الهيكل
            metadata: معلومات إضافية
        
        Returns:
            Path: مسار المجلد النهائي
        """
        base_dir = Path(base_dir)
        base_dir.mkdir(parents=True, exist_ok=True)
        
        if structure_type == "flat":
            return base_dir
        
        elif structure_type == "by_date":
            date_folder = datetime.now().strftime("%Y-%m-%d")
            output_dir = base_dir / date_folder
            output_dir.mkdir(exist_ok=True)
            return output_dir
        
        elif structure_type == "by_name":
            name_folder = "selected_images"
            output_dir = base_dir / name_folder
            output_dir.mkdir(exist_ok=True)
            return output_dir
        
        elif structure_type == "by_size":
            if metadata and 'total_images' in metadata:
                size_folder = f"batch_{metadata['total_images']}"
            else:
                size_folder = "batch_unknown"
            output_dir = base_dir / size_folder
            output_dir.mkdir(exist_ok=True)
            return output_dir
        
        elif structure_type == "by_type":
            # تنظيم حسب نوع الملف
            type_folder = "by_file_type"
            output_dir = base_dir / type_folder
            output_dir.mkdir(exist_ok=True)
            return output_dir
        
        elif structure_type == "by_source":
            # تنظيم حسب مصدر الصور
            if metadata and 'source_folder' in metadata:
                source_name = Path(metadata['source_folder']).name
                source_folder = f"from_{source_name}"
            else:
                source_folder = "from_unknown"
            output_dir = base_dir / source_folder
            output_dir.mkdir(exist_ok=True)
            return output_dir
        
        elif structure_type == "custom":
            # هيكل مخصص
            if metadata and 'custom_name' in metadata:
                custom_folder = metadata['custom_name']
            else:
                custom_folder = "custom_batch"
            output_dir = base_dir / custom_folder
            output_dir.mkdir(exist_ok=True)
            return output_dir
        
        return base_dir
    
    def organize_by_file_type(self, images: List[Path], output_dir: Path) -> Dict[str, List[Path]]:
        """
        تنظيم الصور حسب نوع الملف
        
        Args:
            images: قائمة الصور
            output_dir: مجلد الإخراج
        
        Returns:
            Dict: قاموس الصور المنظمة حسب النوع
        """
        organized = {}
        
        for image_path in images:
            file_extension = image_path.suffix.lower()
            
            if file_extension not in organized:
                organized[file_extension] = []
                # إنشاء مجلد للنوع
                type_dir = output_dir / file_extension[1:]  # إزالة النقطة
                type_dir.mkdir(exist_ok=True)
            
            organized[file_extension].append(image_path)
        
        return organized
    
    def organize_by_size(self, images: List[Path], output_dir: Path, 
                        size_ranges: List[tuple] = None) -> Dict[str, List[Path]]:
        """
        تنظيم الصور حسب الحجم
        
        Args:
            images: قائمة الصور
            output_dir: مجلد الإخراج
            size_ranges: نطاقات الحجم (min, max, name)
        
        Returns:
            Dict: قاموس الصور المنظمة حسب الحجم
        """
        if size_ranges is None:
            size_ranges = [
                (0, 1024 * 1024, "small"),  # أقل من 1MB
                (1024 * 1024, 5 * 1024 * 1024, "medium"),  # 1-5MB
                (5 * 1024 * 1024, float('inf'), "large")  # أكبر من 5MB
            ]
        
        organized = {}
        
        for image_path in images:
            try:
                file_size = image_path.stat().st_size
                
                for min_size, max_size, size_name in size_ranges:
                    if min_size <= file_size < max_size:
                        if size_name not in organized:
                            organized[size_name] = []
                            # إنشاء مجلد للحجم
                            size_dir = output_dir / size_name
                            size_dir.mkdir(exist_ok=True)
                        
                        organized[size_name].append(image_path)
                        break
            except OSError:
                continue
        
        return organized
    
    def organize_by_date(self, images: List[Path], output_dir: Path, 
                        date_format: str = "%Y-%m-%d") -> Dict[str, List[Path]]:
        """
        تنظيم الصور حسب التاريخ
        
        Args:
            images: قائمة الصور
            output_dir: مجلد الإخراج
            date_format: تنسيق التاريخ
        
        Returns:
            Dict: قاموس الصور المنظمة حسب التاريخ
        """
        organized = {}
        
        for image_path in images:
            try:
                file_time = datetime.fromtimestamp(image_path.stat().st_mtime)
                date_folder = file_time.strftime(date_format)
                
                if date_folder not in organized:
                    organized[date_folder] = []
                    # إنشاء مجلد للتاريخ
                    date_dir = output_dir / date_folder
                    date_dir.mkdir(exist_ok=True)
                
                organized[date_folder].append(image_path)
            except OSError:
                continue
        
        return organized
    
    def create_backup(self, source_dir: Path, backup_dir: Path) -> bool:
        """
        إنشاء نسخة احتياطية من المجلد
        
        Args:
            source_dir: المجلد المصدر
            backup_dir: مجلد النسخة الاحتياطية
        
        Returns:
            bool: نجح أم فشل
        """
        try:
            source_dir = Path(source_dir)
            backup_dir = Path(backup_dir)
            
            # إنشاء مجلد النسخة الاحتياطية
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # نسخ المجلد
            shutil.copytree(source_dir, backup_dir / source_dir.name, dirs_exist_ok=True)
            
            self.logger.info(f"تم إنشاء نسخة احتياطية من {source_dir} إلى {backup_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء النسخة الاحتياطية: {e}")
            return False
    
    def cleanup_empty_folders(self, directory: Path) -> int:
        """
        تنظيف المجلدات الفارغة
        
        Args:
            directory: المجلد المراد تنظيفه
        
        Returns:
            int: عدد المجلدات المحذوفة
        """
        deleted_count = 0
        
        try:
            for root, dirs, files in os.walk(directory, topdown=False):
                for dir_name in dirs:
                    dir_path = Path(root) / dir_name
                    try:
                        if not any(dir_path.iterdir()):  # مجلد فارغ
                            dir_path.rmdir()
                            deleted_count += 1
                            self.logger.info(f"تم حذف المجلد الفارغ: {dir_path}")
                    except OSError:
                        continue
            
        except Exception as e:
            self.logger.error(f"خطأ في تنظيف المجلدات: {e}")
        
        return deleted_count
    
    def get_folder_size(self, directory: Path) -> int:
        """
        حساب حجم المجلد
        
        Args:
            directory: المجلد
        
        Returns:
            int: الحجم بالبايت
        """
        total_size = 0
        
        try:
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except OSError:
            pass
        
        return total_size
    
    def format_size(self, size_bytes: int) -> str:
        """
        تنسيق الحجم بصيغة مقروءة
        
        Args:
            size_bytes: الحجم بالبايت
        
        Returns:
            str: الحجم المنسق
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def create_folder_report(self, directory: Path, output_file: Path) -> bool:
        """
        إنشاء تقرير عن محتويات المجلد
        
        Args:
            directory: المجلد المراد تحليله
            output_file: ملف التقرير
        
        Returns:
            bool: نجح أم فشل
        """
        try:
            directory = Path(directory)
            output_file = Path(output_file)
            
            # جمع المعلومات
            files_info = []
            total_size = 0
            
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    try:
                        stat = file_path.stat()
                        file_info = {
                            'path': str(file_path.relative_to(directory)),
                            'name': file_path.name,
                            'size': stat.st_size,
                            'size_formatted': self.format_size(stat.st_size),
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'extension': file_path.suffix.lower()
                        }
                        files_info.append(file_info)
                        total_size += stat.st_size
                    except OSError:
                        continue
            
            # إنشاء التقرير
            report = {
                'directory': str(directory),
                'total_files': len(files_info),
                'total_size': total_size,
                'total_size_formatted': self.format_size(total_size),
                'generated_at': datetime.now().isoformat(),
                'files': files_info
            }
            
            # حفظ التقرير
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"تم إنشاء تقرير المجلد: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء تقرير المجلد: {e}")
            return False
    
    def create_folder_structure_diagram(self, directory: Path, output_file: Path, 
                                      max_depth: int = 3) -> bool:
        """
        إنشاء مخطط هيكل المجلدات
        
        Args:
            directory: المجلد المراد تحليله
            output_file: ملف المخطط
            max_depth: العمق الأقصى
        
        Returns:
            bool: نجح أم فشل
        """
        try:
            directory = Path(directory)
            output_file = Path(output_file)
            
            def create_tree(path: Path, prefix: str = "", depth: int = 0) -> str:
                if depth > max_depth:
                    return ""
                
                tree = ""
                items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
                
                for i, item in enumerate(items):
                    is_last = i == len(items) - 1
                    current_prefix = "└── " if is_last else "├── "
                    tree += f"{prefix}{current_prefix}{item.name}\n"
                    
                    if item.is_dir() and depth < max_depth:
                        next_prefix = prefix + ("    " if is_last else "│   ")
                        tree += create_tree(item, next_prefix, depth + 1)
                
                return tree
            
            # إنشاء المخطط
            diagram = f"هيكل المجلد: {directory}\n"
            diagram += "=" * 50 + "\n\n"
            diagram += create_tree(directory)
            diagram += f"\nتم إنشاؤه في: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            # حفظ المخطط
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(diagram)
            
            self.logger.info(f"تم إنشاء مخطط هيكل المجلدات: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء مخطط هيكل المجلدات: {e}")
            return False
    
    def optimize_folder_structure(self, directory: Path, 
                                optimization_type: str = "size") -> Dict[str, any]:
        """
        تحسين هيكل المجلدات
        
        Args:
            directory: المجلد المراد تحسينه
            optimization_type: نوع التحسين
        
        Returns:
            Dict: نتائج التحسين
        """
        results = {
            'optimization_type': optimization_type,
            'original_size': self.get_folder_size(directory),
            'optimized_size': 0,
            'space_saved': 0,
            'files_moved': 0,
            'folders_created': 0,
            'errors': []
        }
        
        try:
            directory = Path(directory)
            
            if optimization_type == "size":
                # تنظيم حسب الحجم
                organized = self.organize_by_size(list(directory.glob('*')), directory)
                results['folders_created'] = len(organized)
                
            elif optimization_type == "type":
                # تنظيم حسب النوع
                organized = self.organize_by_file_type(list(directory.glob('*')), directory)
                results['folders_created'] = len(organized)
                
            elif optimization_type == "date":
                # تنظيم حسب التاريخ
                organized = self.organize_by_date(list(directory.glob('*')), directory)
                results['folders_created'] = len(organized)
            
            # حساب النتائج
            results['optimized_size'] = self.get_folder_size(directory)
            results['space_saved'] = results['original_size'] - results['optimized_size']
            
            self.logger.info(f"تم تحسين هيكل المجلد: {directory}")
            
        except Exception as e:
            results['errors'].append(str(e))
            self.logger.error(f"خطأ في تحسين هيكل المجلد: {e}")
        
        return results

def main():
    """مثال على الاستخدام"""
    import argparse
    
    parser = argparse.ArgumentParser(description='مدير المجلدات والتنظيم')
    parser.add_argument('directory', help='المجلد المراد إدارته')
    parser.add_argument('--action', choices=['report', 'optimize', 'cleanup', 'backup'], 
                       default='report', help='الإجراء المطلوب')
    parser.add_argument('--output', help='ملف الإخراج')
    parser.add_argument('--optimization-type', choices=['size', 'type', 'date'], 
                       default='size', help='نوع التحسين')
    
    args = parser.parse_args()
    
    # إنشاء مدير المجلدات
    manager = FolderManager()
    
    directory = Path(args.directory)
    
    if args.action == 'report':
        output_file = args.output or directory / 'folder_report.json'
        success = manager.create_folder_report(directory, output_file)
        if success:
            print(f"تم إنشاء تقرير المجلد: {output_file}")
        else:
            print("فشل في إنشاء تقرير المجلد")
    
    elif args.action == 'optimize':
        results = manager.optimize_folder_structure(directory, args.optimization_type)
        print(f"نتائج التحسين: {results}")
    
    elif args.action == 'cleanup':
        deleted_count = manager.cleanup_empty_folders(directory)
        print(f"تم حذف {deleted_count} مجلد فارغ")
    
    elif args.action == 'backup':
        backup_dir = args.output or directory.parent / 'backup'
        success = manager.create_backup(directory, backup_dir)
        if success:
            print(f"تم إنشاء نسخة احتياطية في: {backup_dir}")
        else:
            print("فشل في إنشاء النسخة الاحتياطية")

if __name__ == "__main__":
    main()
