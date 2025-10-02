#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
واجهة مستخدم رسومية للمعالجة المجمعة
Batch Processing GUI Application
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from pathlib import Path
import json
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from batch_processor import BatchProcessor

class BatchProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("معالج الصور المجمعة - Batch Image Processor")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # متغيرات
        self.processor = None
        self.results = []
        self.is_processing = False
        self.input_paths = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        # العنوان الرئيسي
        title_label = tk.Label(
            self.root, 
            text="معالج الصور المجمعة - Batch Image Processor",
            font=("Arial", 16, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title_label.pack(pady=10)
        
        # إطار الإعدادات
        settings_frame = tk.LabelFrame(self.root, text="إعدادات المعالجة", font=("Arial", 12, "bold"))
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # صف الإدخال
        input_frame = tk.Frame(settings_frame)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(input_frame, text="المدخل:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(input_frame, textvariable=self.input_var, width=50)
        self.input_entry.pack(side=tk.LEFT, padx=5)
        
        self.browse_btn = tk.Button(
            input_frame,
            text="تصفح",
            command=self.browse_input,
            bg='#3498db',
            fg='white',
            font=("Arial", 10)
        )
        self.browse_btn.pack(side=tk.LEFT, padx=5)
        
        # صف الإخراج
        output_frame = tk.Frame(settings_frame)
        output_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(output_frame, text="الإخراج:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.output_var = tk.StringVar()
        self.output_entry = tk.Entry(output_frame, textvariable=self.output_var, width=50)
        self.output_entry.pack(side=tk.LEFT, padx=5)
        
        self.browse_output_btn = tk.Button(
            output_frame,
            text="تصفح",
            command=self.browse_output,
            bg='#3498db',
            fg='white',
            font=("Arial", 10)
        )
        self.browse_output_btn.pack(side=tk.LEFT, padx=5)
        
        # صف الخيارات
        options_frame = tk.Frame(settings_frame)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # عدد العمال
        tk.Label(options_frame, text="عدد العمال:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.workers_var = tk.IntVar(value=4)
        workers_spinbox = tk.Spinbox(options_frame, from_=1, to=16, textvariable=self.workers_var, width=5)
        workers_spinbox.pack(side=tk.LEFT, padx=5)
        
        # البحث في المجلدات الفرعية
        self.recursive_var = tk.BooleanVar(value=True)
        recursive_check = tk.Checkbutton(
            options_frame, 
            text="البحث في المجلدات الفرعية", 
            variable=self.recursive_var,
            font=("Arial", 10)
        )
        recursive_check.pack(side=tk.LEFT, padx=10)
        
        # حفظ الصور المحسنة
        self.save_enhanced_var = tk.BooleanVar(value=True)
        save_check = tk.Checkbutton(
            options_frame, 
            text="حفظ الصور المحسنة", 
            variable=self.save_enhanced_var,
            font=("Arial", 10)
        )
        save_check.pack(side=tk.LEFT, padx=10)
        
        # استخدام multiprocessing
        self.multiprocessing_var = tk.BooleanVar(value=False)
        mp_check = tk.Checkbutton(
            options_frame, 
            text="استخدام Multiprocessing", 
            variable=self.multiprocessing_var,
            font=("Arial", 10)
        )
        mp_check.pack(side=tk.LEFT, padx=10)
        
        # إطار الأزرار
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=10)
        
        # زر بدء المعالجة
        self.start_btn = tk.Button(
            button_frame,
            text="بدء المعالجة",
            command=self.start_processing,
            bg='#27ae60',
            fg='white',
            font=("Arial", 12, "bold"),
            padx=20,
            pady=5
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        # زر إيقاف المعالجة
        self.stop_btn = tk.Button(
            button_frame,
            text="إيقاف المعالجة",
            command=self.stop_processing,
            bg='#e74c3c',
            fg='white',
            font=("Arial", 12, "bold"),
            padx=20,
            pady=5,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # زر تصدير النتائج
        self.export_btn = tk.Button(
            button_frame,
            text="تصدير النتائج",
            command=self.export_results,
            bg='#f39c12',
            fg='white',
            font=("Arial", 12, "bold"),
            padx=20,
            pady=5,
            state=tk.DISABLED
        )
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        # شريط التقدم
        progress_frame = tk.Frame(self.root, bg='#f0f0f0')
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(progress_frame, text="التقدم:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.progress_var = tk.StringVar(value="0% (0/0)")
        self.progress_label = tk.Label(progress_frame, textvariable=self.progress_var, font=("Arial", 10))
        self.progress_label.pack(side=tk.LEFT, padx=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=400)
        self.progress_bar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # إطار المحتوى الرئيسي
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # تبويبات
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # تبويب النتائج
        results_frame = ttk.Frame(notebook)
        notebook.add(results_frame, text="النتائج")
        
        # قائمة النتائج
        self.results_tree = ttk.Treeview(results_frame, columns=('status', 'time', 'texts'), show='tree headings')
        self.results_tree.heading('#0', text='اسم الملف')
        self.results_tree.heading('status', text='الحالة')
        self.results_tree.heading('time', text='وقت المعالجة')
        self.results_tree.heading('texts', text='عدد النصوص')
        
        self.results_tree.column('#0', width=300)
        self.results_tree.column('status', width=100)
        self.results_tree.column('time', width=100)
        self.results_tree.column('texts', width=100)
        
        # شريط تمرير للنتائج
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ربط حدث النقر على النتائج
        self.results_tree.bind('<Double-1>', self.show_image_details)
        
        # تبويب الإحصائيات
        stats_frame = ttk.Frame(notebook)
        notebook.add(stats_frame, text="الإحصائيات")
        
        # نص الإحصائيات
        self.stats_text = scrolledtext.ScrolledText(
            stats_frame, 
            wrap=tk.WORD, 
            height=20,
            font=("Arial", 10)
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # تبويب الرسائل
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="سجل المعالجة")
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            wrap=tk.WORD, 
            height=15,
            font=("Arial", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # شريط الحالة
        self.status_label = tk.Label(
            self.root, 
            text="جاهز للمعالجة",
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg='#ecf0f1'
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    def browse_input(self):
        """تصفح مجلد أو ملف الإدخال"""
        choice = messagebox.askyesnocancel("اختيار المدخل", 
                                         "هل تريد اختيار مجلد؟\nنعم = مجلد\nلا = ملف واحد\nإلغاء = إلغاء")
        
        if choice is True:  # مجلد
            folder = filedialog.askdirectory(title="اختر مجلد الصور")
            if folder:
                self.input_var.set(folder)
        elif choice is False:  # ملف
            file = filedialog.askopenfilename(
                title="اختر صورة",
                filetypes=[
                    ("ملفات الصور", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
                    ("جميع الملفات", "*.*")
                ]
            )
            if file:
                self.input_var.set(file)
    
    def browse_output(self):
        """تصفح مجلد الإخراج"""
        folder = filedialog.askdirectory(title="اختر مجلد الإخراج")
        if folder:
            self.output_var.set(folder)
    
    def start_processing(self):
        """بدء المعالجة"""
        input_path = self.input_var.get().strip()
        if not input_path:
            messagebox.showerror("خطأ", "يرجى اختيار مجلد أو ملف الإدخال")
            return
        
        if not os.path.exists(input_path):
            messagebox.showerror("خطأ", "مسار الإدخال غير موجود")
            return
        
        # إنشاء معالج الصور المجمعة
        self.processor = BatchProcessor(
            max_workers=self.workers_var.get(),
            use_multiprocessing=self.multiprocessing_var.get()
        )
        
        # تعيين callback للتقدم
        self.processor.set_progress_callback(self.update_progress)
        
        # تعطيل الأزرار
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.is_processing = True
        
        # مسح النتائج السابقة
        self.results = []
        self.results_tree.delete(*self.results_tree.get_children())
        self.stats_text.delete(1.0, tk.END)
        self.log_text.delete(1.0, tk.END)
        
        # بدء المعالجة في thread منفصل
        thread = threading.Thread(target=self._process_images_thread)
        thread.daemon = True
        thread.start()
    
    def _process_images_thread(self):
        """معالجة الصور في thread منفصل"""
        try:
            input_path = Path(self.input_var.get())
            output_path = self.output_var.get() if self.output_var.get() else None
            
            if input_path.is_file():
                # معالجة صورة واحدة
                self.log_message(f"بدء معالجة صورة واحدة: {input_path.name}")
                results = [self.processor.process_single_image(
                    input_path, 
                    output_path, 
                    self.save_enhanced_var.get()
                )]
            else:
                # معالجة مجلد
                self.log_message(f"بدء معالجة مجلد: {input_path}")
                results = self.processor.process_directory(
                    input_path,
                    output_path,
                    self.recursive_var.get(),
                    self.save_enhanced_var.get()
                )
            
            # تحديث الواجهة
            self.root.after(0, lambda: self._processing_completed(results))
            
        except Exception as e:
            self.root.after(0, lambda: self._processing_failed(str(e)))
    
    def update_progress(self, progress, processed, total):
        """تحديث شريط التقدم"""
        self.root.after(0, lambda: self._update_progress_ui(progress, processed, total))
    
    def _update_progress_ui(self, progress, processed, total):
        """تحديث واجهة التقدم"""
        self.progress_var.set(f"{progress:.1f}% ({processed}/{total})")
        self.progress_bar['value'] = progress
        self.status_label.config(text=f"جاري المعالجة... {processed}/{total}")
    
    def log_message(self, message):
        """إضافة رسالة إلى السجل"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.root.after(0, lambda: self._add_log_message(log_entry))
    
    def _add_log_message(self, message):
        """إضافة رسالة إلى واجهة السجل"""
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
    
    def _processing_completed(self, results):
        """انتهاء المعالجة بنجاح"""
        self.results = results
        self.is_processing = False
        
        # تحديث الأزرار
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.export_btn.config(state=tk.NORMAL)
        
        # تحديث شريط التقدم
        self.progress_bar['value'] = 100
        self.status_label.config(text="تمت المعالجة بنجاح")
        
        # تحديث النتائج
        self.update_results_display()
        
        # تحديث الإحصائيات
        self.update_statistics()
        
        # رسالة نجاح
        stats = self.processor.get_statistics(results)
        messagebox.showinfo("نجح", 
                           f"تمت معالجة {stats['successful']} من {stats['total_images']} صورة بنجاح!\n"
                           f"معدل النجاح: {stats['success_rate']:.1f}%")
    
    def _processing_failed(self, error_message):
        """فشل المعالجة"""
        self.is_processing = False
        
        # تحديث الأزرار
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        # تحديث الحالة
        self.status_label.config(text="فشلت المعالجة")
        
        # رسالة خطأ
        messagebox.showerror("خطأ", f"فشلت المعالجة: {error_message}")
    
    def stop_processing(self):
        """إيقاف المعالجة"""
        self.is_processing = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="تم إيقاف المعالجة")
        messagebox.showinfo("إيقاف", "تم إيقاف المعالجة")
    
    def update_results_display(self):
        """تحديث عرض النتائج"""
        # مسح النتائج السابقة
        self.results_tree.delete(*self.results_tree.get_children())
        
        # إضافة النتائج الجديدة
        for result in self.results:
            filename = Path(result['image_path']).name
            status = "نجح" if result['status'] == 'success' else "فشل"
            time_str = f"{result['processing_time']:.2f}s"
            texts_count = result.get('total_texts_found', 0)
            
            # لون الصف حسب الحالة
            item = self.results_tree.insert('', 'end', text=filename, 
                                          values=(status, time_str, texts_count))
            
            if result['status'] == 'failed':
                self.results_tree.set(item, 'status', f"فشل: {result.get('error', '')}")
    
    def update_statistics(self):
        """تحديث الإحصائيات"""
        if not self.results:
            return
        
        stats = self.processor.get_statistics(self.results)
        
        stats_text = f"""
إحصائيات معالجة الصور المجمعة
{'='*50}

إجمالي الصور: {stats['total_images']}
نجحت: {stats['successful']}
فشلت: {stats['failed']}
معدل النجاح: {stats['success_rate']:.1f}%

وقت المعالجة:
- إجمالي: {stats['total_processing_time']:.2f} ثانية
- متوسط: {stats['average_processing_time']:.2f} ثانية

النصوص المكتشفة:
- إجمالي: {stats['total_texts_found']}
- متوسط لكل صورة: {stats['average_texts_per_image']:.1f}

تفاصيل النتائج:
"""
        
        # إضافة تفاصيل النتائج
        for i, result in enumerate(self.results, 1):
            filename = Path(result['image_path']).name
            stats_text += f"\n{i}. {filename}\n"
            stats_text += f"   الحالة: {result['status']}\n"
            stats_text += f"   وقت المعالجة: {result['processing_time']:.2f} ثانية\n"
            
            if result['status'] == 'success':
                stats_text += f"   النصوص المكتشفة: {result.get('total_texts_found', 0)}\n"
                
                if result.get('easyocr_results'):
                    stats_text += "   EasyOCR:\n"
                    for j, text_result in enumerate(result['easyocr_results'][:3], 1):  # أول 3 نصوص فقط
                        stats_text += f"     {j}. {text_result['text']} ({text_result['confidence']:.2%})\n"
                
                if result.get('tesseract_results'):
                    stats_text += "   Tesseract:\n"
                    for j, text_result in enumerate(result['tesseract_results'][:3], 1):  # أول 3 نصوص فقط
                        stats_text += f"     {j}. {text_result['text']} ({text_result['confidence']:.2%})\n"
            else:
                stats_text += f"   الخطأ: {result.get('error', '')}\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
    
    def show_image_details(self, event):
        """عرض تفاصيل الصورة المحددة"""
        selection = self.results_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        filename = self.results_tree.item(item, 'text')
        
        # البحث عن النتيجة المقابلة
        result = None
        for r in self.results:
            if Path(r['image_path']).name == filename:
                result = r
                break
        
        if not result:
            return
        
        # إنشاء نافذة التفاصيل
        details_window = tk.Toplevel(self.root)
        details_window.title(f"تفاصيل: {filename}")
        details_window.geometry("600x500")
        
        # نص التفاصيل
        details_text = scrolledtext.ScrolledText(details_window, wrap=tk.WORD)
        details_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # محتوى التفاصيل
        content = f"تفاصيل الصورة: {filename}\n"
        content += "="*50 + "\n\n"
        content += f"المسار: {result['image_path']}\n"
        content += f"الحالة: {result['status']}\n"
        content += f"وقت المعالجة: {result['processing_time']:.2f} ثانية\n"
        content += f"التاريخ: {result.get('timestamp', 'غير محدد')}\n\n"
        
        if result['status'] == 'success':
            content += f"عدد النصوص المكتشفة: {result.get('total_texts_found', 0)}\n\n"
            
            if result.get('easyocr_results'):
                content += "نتائج EasyOCR:\n"
                content += "-"*30 + "\n"
                for i, text_result in enumerate(result['easyocr_results'], 1):
                    content += f"{i}. النص: {text_result['text']}\n"
                    content += f"   الثقة: {text_result['confidence']:.2%}\n\n"
            
            if result.get('tesseract_results'):
                content += "نتائج Tesseract:\n"
                content += "-"*30 + "\n"
                for i, text_result in enumerate(result['tesseract_results'], 1):
                    content += f"{i}. النص: {text_result['text']}\n"
                    content += f"   الثقة: {text_result['confidence']:.2%}\n\n"
        else:
            content += f"الخطأ: {result.get('error', '')}\n"
        
        details_text.insert(1.0, content)
        details_text.config(state=tk.DISABLED)
    
    def export_results(self):
        """تصدير النتائج"""
        if not self.results:
            messagebox.showwarning("تحذير", "لا توجد نتائج للتصدير")
            return
        
        # اختيار تنسيق التصدير
        format_choice = messagebox.askyesnocancel("تنسيق التصدير", 
                                                "اختر تنسيق التصدير:\nنعم = JSON\nلا = CSV\nإلغاء = إلغاء")
        
        if format_choice is None:  # إلغاء
            return
        
        format_type = 'json' if format_choice else 'csv'
        
        # اختيار ملف الحفظ
        file_path = filedialog.asksaveasfilename(
            title="حفظ النتائج",
            defaultextension=f".{format_type}",
            filetypes=[
                (f"{format_type.upper()} files", f"*.{format_type}"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.processor.save_results(self.results, file_path, format_type)
                messagebox.showinfo("نجح", f"تم حفظ النتائج في: {file_path}")
            except Exception as e:
                messagebox.showerror("خطأ", f"خطأ في حفظ النتائج: {str(e)}")

def main():
    """تشغيل التطبيق"""
    root = tk.Tk()
    app = BatchProcessorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
