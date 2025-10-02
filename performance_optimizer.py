#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
محسن الأداء للمعالجة الكبيرة
Performance Optimizer for Large Scale Processing
"""

import os
import psutil
import time
import threading
from pathlib import Path
from typing import List, Dict, Optional, Callable
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import queue
import gc

class PerformanceOptimizer:
    def __init__(self):
        """تهيئة محسن الأداء"""
        self.logger = logging.getLogger(__name__)
        self.system_info = self.get_system_info()
        self.performance_metrics = {}
        
    def get_system_info(self) -> Dict:
        """الحصول على معلومات النظام"""
        try:
            return {
                'cpu_count': psutil.cpu_count(),
                'cpu_count_logical': psutil.cpu_count(logical=True),
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available,
                'disk_usage': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent,
                'platform': os.name
            }
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على معلومات النظام: {e}")
            return {}
    
    def calculate_optimal_workers(self, task_type: str = "cpu_intensive", 
                                memory_per_task: int = 100) -> int:
        """
        حساب العدد الأمثل للعمال
        
        Args:
            task_type: نوع المهمة ("cpu_intensive", "io_intensive", "memory_intensive")
            memory_per_task: الذاكرة المطلوبة لكل مهمة (MB)
        
        Returns:
            int: العدد الأمثل للعمال
        """
        cpu_count = self.system_info.get('cpu_count', 4)
        memory_total_gb = self.system_info.get('memory_total', 8 * 1024**3) / (1024**3)
        memory_available_gb = self.system_info.get('memory_available', 4 * 1024**3) / (1024**3)
        
        if task_type == "cpu_intensive":
            # للمهام المكثفة في المعالج
            optimal = min(cpu_count, int(memory_available_gb * 1024 / memory_per_task))
            return max(1, min(optimal, cpu_count * 2))
        
        elif task_type == "io_intensive":
            # للمهام المكثفة في الإدخال/الإخراج
            return min(cpu_count * 4, 32)
        
        elif task_type == "memory_intensive":
            # للمهام المكثفة في الذاكرة
            optimal = int(memory_available_gb * 1024 / memory_per_task)
            return max(1, min(optimal, cpu_count))
        
        else:
            # افتراضي
            return cpu_count
    
    def monitor_system_resources(self, duration: int = 60, interval: int = 1) -> Dict:
        """
        مراقبة موارد النظام
        
        Args:
            duration: مدة المراقبة (ثانية)
            interval: فترة المراقبة (ثانية)
        
        Returns:
            Dict: إحصائيات المراقبة
        """
        metrics = {
            'cpu_usage': [],
            'memory_usage': [],
            'disk_usage': [],
            'timestamps': []
        }
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            try:
                cpu_percent = psutil.cpu_percent(interval=interval)
                memory_percent = psutil.virtual_memory().percent
                disk_percent = psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent
                
                metrics['cpu_usage'].append(cpu_percent)
                metrics['memory_usage'].append(memory_percent)
                metrics['disk_usage'].append(disk_percent)
                metrics['timestamps'].append(time.time())
                
            except Exception as e:
                self.logger.error(f"خطأ في مراقبة النظام: {e}")
                break
        
        return metrics
    
    def optimize_memory_usage(self, target_memory_percent: int = 80) -> Dict:
        """
        تحسين استخدام الذاكرة
        
        Args:
            target_memory_percent: النسبة المستهدفة لاستخدام الذاكرة
        
        Returns:
            Dict: نتائج التحسين
        """
        results = {
            'before_memory': psutil.virtual_memory().percent,
            'after_memory': 0,
            'memory_freed': 0,
            'gc_collections': 0
        }
        
        try:
            # جمع القمامة
            collected = gc.collect()
            results['gc_collections'] = collected
            
            # إجبار جمع القمامة
            for generation in range(3):
                collected += gc.collect()
            
            # قياس الذاكرة بعد التحسين
            results['after_memory'] = psutil.virtual_memory().percent
            results['memory_freed'] = results['before_memory'] - results['after_memory']
            
            self.logger.info(f"تم تحسين الذاكرة: {results['memory_freed']:.1f}%")
            
        except Exception as e:
            self.logger.error(f"خطأ في تحسين الذاكرة: {e}")
        
        return results
    
    def create_processing_queue(self, items: List, batch_size: int = 100) -> List[List]:
        """
        إنشاء طابور معالجة مجزأة
        
        Args:
            items: العناصر المراد معالجتها
            batch_size: حجم الدفعة
        
        Returns:
            List[List]: قائمة الدفعات
        """
        batches = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batches.append(batch)
        
        return batches
    
    def adaptive_worker_scaling(self, current_workers: int, 
                              performance_metrics: Dict) -> int:
        """
        تحجيم العمال التكيفي
        
        Args:
            current_workers: عدد العمال الحالي
            performance_metrics: مقاييس الأداء
        
        Returns:
            int: عدد العمال المقترح
        """
        cpu_usage = performance_metrics.get('cpu_usage', [0])
        memory_usage = performance_metrics.get('memory_usage', [0])
        
        avg_cpu = sum(cpu_usage) / len(cpu_usage) if cpu_usage else 0
        avg_memory = sum(memory_usage) / len(memory_usage) if memory_usage else 0
        
        # إذا كان استخدام المعالج منخفض، زد العمال
        if avg_cpu < 50 and avg_memory < 80:
            return min(current_workers + 2, self.system_info.get('cpu_count', 4) * 2)
        
        # إذا كان استخدام المعالج عالي، قلل العمال
        elif avg_cpu > 90 or avg_memory > 90:
            return max(current_workers - 1, 1)
        
        # إذا كان الأداء متوازن، ابق على نفس العدد
        else:
            return current_workers
    
    def estimate_processing_time(self, total_items: int, 
                               avg_time_per_item: float,
                               workers: int) -> Dict:
        """
        تقدير وقت المعالجة
        
        Args:
            total_items: إجمالي العناصر
            avg_time_per_item: متوسط الوقت لكل عنصر
            workers: عدد العمال
        
        Returns:
            Dict: تقديرات الوقت
        """
        sequential_time = total_items * avg_time_per_item
        parallel_time = sequential_time / workers
        
        # إضافة وقت إضافي للتعامل مع التزامن
        overhead_factor = 1.1 + (workers * 0.05)
        estimated_time = parallel_time * overhead_factor
        
        return {
            'sequential_time': sequential_time,
            'parallel_time': parallel_time,
            'estimated_time': estimated_time,
            'overhead_factor': overhead_factor,
            'speedup': sequential_time / estimated_time
        }
    
    def create_performance_report(self, processing_results: List[Dict]) -> Dict:
        """
        إنشاء تقرير الأداء
        
        Args:
            processing_results: نتائج المعالجة
        
        Returns:
            Dict: تقرير الأداء
        """
        if not processing_results:
            return {}
        
        total_items = len(processing_results)
        successful_items = sum(1 for r in processing_results if r.get('status') == 'success')
        failed_items = total_items - successful_items
        
        processing_times = [r.get('processing_time', 0) for r in processing_results]
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        total_processing_time = sum(processing_times)
        
        return {
            'total_items': total_items,
            'successful_items': successful_items,
            'failed_items': failed_items,
            'success_rate': (successful_items / total_items) * 100 if total_items > 0 else 0,
            'total_processing_time': total_processing_time,
            'average_processing_time': avg_processing_time,
            'min_processing_time': min(processing_times) if processing_times else 0,
            'max_processing_time': max(processing_times) if processing_times else 0,
            'throughput': total_items / total_processing_time if total_processing_time > 0 else 0,
            'system_info': self.system_info
        }
    
    def optimize_for_large_scale(self, total_images: int, 
                               avg_image_size_mb: float = 2.0) -> Dict:
        """
        تحسين للمعالجة على نطاق واسع
        
        Args:
            total_images: إجمالي عدد الصور
            avg_image_size_mb: متوسط حجم الصورة (MB)
        
        Returns:
            Dict: توصيات التحسين
        """
        recommendations = {
            'optimal_workers': 0,
            'batch_size': 0,
            'memory_optimization': False,
            'disk_optimization': False,
            'processing_strategy': '',
            'estimated_time': 0
        }
        
        # حساب الذاكرة المطلوبة
        total_memory_gb = (total_images * avg_image_size_mb) / 1024
        available_memory_gb = self.system_info.get('memory_available', 4 * 1024**3) / (1024**3)
        
        # تحديد الاستراتيجية
        if total_images < 100:
            recommendations['processing_strategy'] = 'sequential'
            recommendations['optimal_workers'] = 1
            recommendations['batch_size'] = total_images
        
        elif total_images < 1000:
            recommendations['processing_strategy'] = 'parallel_threading'
            recommendations['optimal_workers'] = min(4, self.system_info.get('cpu_count', 4))
            recommendations['batch_size'] = 50
        
        elif total_images < 10000:
            recommendations['processing_strategy'] = 'parallel_multiprocessing'
            recommendations['optimal_workers'] = self.calculate_optimal_workers('cpu_intensive', 200)
            recommendations['batch_size'] = 100
            recommendations['memory_optimization'] = True
        
        else:
            recommendations['processing_strategy'] = 'batch_processing'
            recommendations['optimal_workers'] = self.calculate_optimal_workers('memory_intensive', 500)
            recommendations['batch_size'] = 200
            recommendations['memory_optimization'] = True
            recommendations['disk_optimization'] = True
        
        # تقدير الوقت
        avg_time_per_image = 2.0  # ثانية (تقدير)
        time_estimate = self.estimate_processing_time(
            total_images, avg_time_per_image, recommendations['optimal_workers']
        )
        recommendations['estimated_time'] = time_estimate['estimated_time']
        
        return recommendations
    
    def monitor_processing_performance(self, callback: Callable = None) -> Dict:
        """
        مراقبة أداء المعالجة
        
        Args:
            callback: دالة callback للنتائج
        
        Returns:
            Dict: مقاييس الأداء
        """
        start_time = time.time()
        start_memory = psutil.virtual_memory().percent
        start_cpu = psutil.cpu_percent()
        
        # مراقبة مستمرة
        def monitor():
            while True:
                current_time = time.time()
                elapsed_time = current_time - start_time
                
                current_memory = psutil.virtual_memory().percent
                current_cpu = psutil.cpu_percent()
                
                metrics = {
                    'elapsed_time': elapsed_time,
                    'memory_usage': current_memory,
                    'cpu_usage': current_cpu,
                    'memory_delta': current_memory - start_memory,
                    'cpu_delta': current_cpu - start_cpu
                }
                
                if callback:
                    callback(metrics)
                
                time.sleep(1)
        
        # تشغيل المراقبة في thread منفصل
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        
        return {
            'start_time': start_time,
            'start_memory': start_memory,
            'start_cpu': start_cpu,
            'monitor_thread': monitor_thread
        }
    
    def cleanup_resources(self):
        """تنظيف الموارد"""
        try:
            # جمع القمامة
            gc.collect()
            
            # إجبار جمع القمامة لجميع الأجيال
            for generation in range(3):
                gc.collect()
            
            self.logger.info("تم تنظيف الموارد")
            
        except Exception as e:
            self.logger.error(f"خطأ في تنظيف الموارد: {e}")

def main():
    """مثال على الاستخدام"""
    import argparse
    
    parser = argparse.ArgumentParser(description='محسن الأداء للمعالجة الكبيرة')
    parser.add_argument('--action', choices=['analyze', 'optimize', 'monitor'], 
                       default='analyze', help='الإجراء المطلوب')
    parser.add_argument('--images', type=int, default=5000, help='عدد الصور')
    parser.add_argument('--duration', type=int, default=60, help='مدة المراقبة')
    
    args = parser.parse_args()
    
    # إنشاء محسن الأداء
    optimizer = PerformanceOptimizer()
    
    if args.action == 'analyze':
        # تحليل النظام
        print("معلومات النظام:")
        print(f"عدد المعالجات: {optimizer.system_info.get('cpu_count', 'غير محدد')}")
        print(f"الذاكرة المتاحة: {optimizer.system_info.get('memory_available', 0) / (1024**3):.1f} GB")
        
        # توصيات التحسين
        recommendations = optimizer.optimize_for_large_scale(args.images)
        print(f"\nتوصيات التحسين لـ {args.images} صورة:")
        print(f"العدد الأمثل للعمال: {recommendations['optimal_workers']}")
        print(f"حجم الدفعة: {recommendations['batch_size']}")
        print(f"استراتيجية المعالجة: {recommendations['processing_strategy']}")
        print(f"الوقت المقدر: {recommendations['estimated_time']:.1f} ثانية")
    
    elif args.action == 'optimize':
        # تحسين الذاكرة
        results = optimizer.optimize_memory_usage()
        print(f"نتائج تحسين الذاكرة: {results}")
    
    elif args.action == 'monitor':
        # مراقبة النظام
        print(f"مراقبة النظام لمدة {args.duration} ثانية...")
        metrics = optimizer.monitor_system_resources(args.duration)
        print(f"متوسط استخدام المعالج: {sum(metrics['cpu_usage']) / len(metrics['cpu_usage']):.1f}%")
        print(f"متوسط استخدام الذاكرة: {sum(metrics['memory_usage']) / len(metrics['memory_usage']):.1f}%")

if __name__ == "__main__":
    main()
