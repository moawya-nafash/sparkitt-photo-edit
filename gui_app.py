#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
واجهة مستخدم رسومية لبرنامج تحسين الصور
GUI Application for Image Enhancement
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import cv2
import numpy as np
from PIL import Image, ImageTk
import threading
import os
from pathlib import Path
from image_enhancer import ImageEnhancer

class ImageEnhancerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("برنامج تحسين الصور للتعرف على النصوص")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # تهيئة معزز الصور
        self.enhancer = ImageEnhancer()
        
        # متغيرات
        self.current_image = None
        self.enhanced_image = None
        self.easyocr_results = []
        self.tesseract_results = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        # العنوان الرئيسي
        title_label = tk.Label(
            self.root, 
            text="برنامج تحسين الصور للتعرف على النصوص",
            font=("Arial", 16, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title_label.pack(pady=10)
        
        # إطار الأزرار
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=10)
        
        # زر تحميل الصورة
        self.load_btn = tk.Button(
            button_frame,
            text="تحميل صورة",
            command=self.load_image,
            bg='#3498db',
            fg='white',
            font=("Arial", 12),
            padx=20,
            pady=5
        )
        self.load_btn.pack(side=tk.LEFT, padx=5)
        
        # زر معالجة الصورة
        self.process_btn = tk.Button(
            button_frame,
            text="معالجة الصورة",
            command=self.process_image,
            bg='#27ae60',
            fg='white',
            font=("Arial", 12),
            padx=20,
            pady=5,
            state=tk.DISABLED
        )
        self.process_btn.pack(side=tk.LEFT, padx=5)
        
        # زر حفظ الصورة المحسنة
        self.save_btn = tk.Button(
            button_frame,
            text="حفظ الصورة المحسنة",
            command=self.save_enhanced_image,
            bg='#e74c3c',
            fg='white',
            font=("Arial", 12),
            padx=20,
            pady=5,
            state=tk.DISABLED
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # شريط التقدم
        self.progress = ttk.Progressbar(
            self.root, 
            mode='indeterminate',
            length=400
        )
        self.progress.pack(pady=10)
        
        # إطار المحتوى الرئيسي
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # إطار الصور
        image_frame = tk.Frame(main_frame, bg='#f0f0f0')
        image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # الصورة الأصلية
        original_frame = tk.LabelFrame(image_frame, text="الصورة الأصلية", font=("Arial", 12, "bold"))
        original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.original_label = tk.Label(original_frame, bg='white', relief=tk.SUNKEN)
        self.original_label.pack(padx=10, pady=10)
        
        # الصورة المحسنة
        enhanced_frame = tk.LabelFrame(image_frame, text="الصورة المحسنة", font=("Arial", 12, "bold"))
        enhanced_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        self.enhanced_label = tk.Label(enhanced_frame, bg='white', relief=tk.SUNKEN)
        self.enhanced_label.pack(padx=10, pady=10)
        
        # إطار النتائج
        results_frame = tk.LabelFrame(main_frame, text="نتائج استخراج النصوص", font=("Arial", 12, "bold"))
        results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # تبويبات للنتائج
        notebook = ttk.Notebook(results_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # تبويب EasyOCR
        easyocr_frame = ttk.Frame(notebook)
        notebook.add(easyocr_frame, text="EasyOCR")
        
        self.easyocr_text = scrolledtext.ScrolledText(
            easyocr_frame, 
            wrap=tk.WORD, 
            height=15,
            font=("Arial", 10)
        )
        self.easyocr_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # تبويب Tesseract
        tesseract_frame = ttk.Frame(notebook)
        notebook.add(tesseract_frame, text="Tesseract")
        
        self.tesseract_text = scrolledtext.ScrolledText(
            tesseract_frame, 
            wrap=tk.WORD, 
            height=15,
            font=("Arial", 10)
        )
        self.tesseract_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # شريط الحالة
        self.status_label = tk.Label(
            self.root, 
            text="جاهز لتحميل صورة",
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg='#ecf0f1'
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    def load_image(self):
        """تحميل صورة من الملف"""
        file_path = filedialog.askopenfilename(
            title="اختر صورة",
            filetypes=[
                ("ملفات الصور", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
                ("جميع الملفات", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.current_image = cv2.imread(file_path)
                if self.current_image is not None:
                    self.display_image(self.current_image, self.original_label)
                    self.process_btn.config(state=tk.NORMAL)
                    self.status_label.config(text=f"تم تحميل الصورة: {Path(file_path).name}")
                else:
                    messagebox.showerror("خطأ", "لا يمكن تحميل الصورة")
            except Exception as e:
                messagebox.showerror("خطأ", f"خطأ في تحميل الصورة: {str(e)}")
    
    def display_image(self, image, label, max_size=(400, 300)):
        """عرض صورة في label مع تغيير الحجم"""
        try:
            # تغيير حجم الصورة
            height, width = image.shape[:2]
            ratio = min(max_size[0]/width, max_size[1]/height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            
            resized = cv2.resize(image, (new_width, new_height))
            
            # تحويل من BGR إلى RGB
            if len(resized.shape) == 3:
                rgb_image = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = resized
            
            # تحويل إلى PIL Image ثم إلى PhotoImage
            pil_image = Image.fromarray(rgb_image)
            photo = ImageTk.PhotoImage(pil_image)
            
            # عرض الصورة
            label.config(image=photo)
            label.image = photo  # الاحتفاظ بمرجع للصورة
            
        except Exception as e:
            print(f"خطأ في عرض الصورة: {e}")
    
    def process_image(self):
        """معالجة الصورة في thread منفصل"""
        if self.current_image is None:
            messagebox.showwarning("تحذير", "يرجى تحميل صورة أولاً")
            return
        
        # تعطيل الأزرار أثناء المعالجة
        self.process_btn.config(state=tk.DISABLED)
        self.progress.start()
        self.status_label.config(text="جاري معالجة الصورة...")
        
        # تشغيل المعالجة في thread منفصل
        thread = threading.Thread(target=self._process_image_thread)
        thread.daemon = True
        thread.start()
    
    def _process_image_thread(self):
        """معالجة الصورة في thread منفصل"""
        try:
            # تحسين الصورة
            self.enhanced_image = self.enhancer.enhance_image_pipeline(self.current_image)
            
            # استخراج النصوص
            self.easyocr_results = self.enhancer.extract_text_easyocr(self.enhanced_image)
            self.tesseract_results = self.enhancer.extract_text_tesseract(self.enhanced_image)
            
            # تحديث الواجهة في main thread
            self.root.after(0, self._update_ui_after_processing)
            
        except Exception as e:
            self.root.after(0, lambda: self._show_error(f"خطأ في معالجة الصورة: {str(e)}"))
    
    def _update_ui_after_processing(self):
        """تحديث الواجهة بعد انتهاء المعالجة"""
        try:
            # عرض الصورة المحسنة
            self.display_image(self.enhanced_image, self.enhanced_label)
            
            # عرض نتائج EasyOCR
            self.easyocr_text.delete(1.0, tk.END)
            if self.easyocr_results:
                for i, result in enumerate(self.easyocr_results, 1):
                    self.easyocr_text.insert(tk.END, f"{i}. النص: {result['text']}\n")
                    self.easyocr_text.insert(tk.END, f"   الثقة: {result['confidence']:.2%}\n\n")
            else:
                self.easyocr_text.insert(tk.END, "لم يتم العثور على نصوص")
            
            # عرض نتائج Tesseract
            self.tesseract_text.delete(1.0, tk.END)
            if self.tesseract_results:
                for i, result in enumerate(self.tesseract_results, 1):
                    self.tesseract_text.insert(tk.END, f"{i}. النص: {result['text']}\n")
                    self.tesseract_text.insert(tk.END, f"   الثقة: {result['confidence']:.2%}\n\n")
            else:
                self.tesseract_text.insert(tk.END, "لم يتم العثور على نصوص")
            
            # تفعيل الأزرار
            self.process_btn.config(state=tk.NORMAL)
            self.save_btn.config(state=tk.NORMAL)
            self.progress.stop()
            self.status_label.config(text="تمت معالجة الصورة بنجاح")
            
        except Exception as e:
            self._show_error(f"خطأ في تحديث الواجهة: {str(e)}")
    
    def _show_error(self, message):
        """عرض رسالة خطأ"""
        self.process_btn.config(state=tk.NORMAL)
        self.progress.stop()
        self.status_label.config(text="خطأ في المعالجة")
        messagebox.showerror("خطأ", message)
    
    def save_enhanced_image(self):
        """حفظ الصورة المحسنة"""
        if self.enhanced_image is None:
            messagebox.showwarning("تحذير", "لا توجد صورة محسنة للحفظ")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="حفظ الصورة المحسنة",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                cv2.imwrite(file_path, self.enhanced_image)
                messagebox.showinfo("نجح", f"تم حفظ الصورة في: {file_path}")
                self.status_label.config(text=f"تم حفظ الصورة: {Path(file_path).name}")
            except Exception as e:
                messagebox.showerror("خطأ", f"خطأ في حفظ الصورة: {str(e)}")

def main():
    """تشغيل التطبيق"""
    root = tk.Tk()
    app = ImageEnhancerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
