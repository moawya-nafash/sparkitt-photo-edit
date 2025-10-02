#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
واجهة مستخدم محسنة للذاكرة
Memory Optimized GUI Application
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import cv2
import numpy as np
from PIL import Image, ImageTk
import threading
import os
from pathlib import Path
import gc
import psutil

class MemoryOptimizedGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("برنامج تحسين الصور - محسن للذاكرة")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # متغيرات
        self.current_image = None
        self.enhanced_image = None
        self.easyocr_results = []
        self.tesseract_results = []
        self.is_processing = False
        
        # إعدادات الذاكرة
        self.max_image_size = 1024  # الحد الأقصى لحجم الصورة
        self.use_easyocr = False  # تعطيل EasyOCR افتراضياً لتوفير الذاكرة
        
        self.setup_ui()
        self.monitor_memory()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        # العنوان الرئيسي
        title_label = tk.Label(
            self.root, 
            text="برنامج تحسين الصور - محسن للذاكرة",
            font=("Arial", 14, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title_label.pack(pady=10)
        
        # إطار إعدادات الذاكرة
        memory_frame = tk.LabelFrame(self.root, text="إعدادات الذاكرة", font=("Arial", 10, "bold"))
        memory_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # معلومات الذاكرة
        self.memory_label = tk.Label(memory_frame, text="الذاكرة: جاري التحميل...", font=("Arial", 9))
        self.memory_label.pack(pady=5)
        
        # خيارات الذاكرة
        options_frame = tk.Frame(memory_frame)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # حجم الصورة
        tk.Label(options_frame, text="الحد الأقصى لحجم الصورة:", font=("Arial", 9)).pack(side=tk.LEFT)
        self.size_var = tk.StringVar(value="1024")
        size_combo = ttk.Combobox(options_frame, textvariable=self.size_var, 
                                 values=["512", "1024", "1536", "2048"], width=8)
        size_combo.pack(side=tk.LEFT, padx=5)
        
        # استخدام EasyOCR
        self.easyocr_var = tk.BooleanVar(value=False)
        easyocr_check = tk.Checkbutton(
            options_frame, 
            text="استخدام EasyOCR (يستهلك ذاكرة أكثر)", 
            variable=self.easyocr_var,
            font=("Arial", 9)
        )
        easyocr_check.pack(side=tk.LEFT, padx=10)
        
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
            font=("Arial", 11),
            padx=15,
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
            font=("Arial", 11),
            padx=15,
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
            font=("Arial", 11),
            padx=15,
            pady=5,
            state=tk.DISABLED
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # زر تنظيف الذاكرة
        self.cleanup_btn = tk.Button(
            button_frame,
            text="تنظيف الذاكرة",
            command=self.cleanup_memory,
            bg='#f39c12',
            fg='white',
            font=("Arial", 11),
            padx=15,
            pady=5
        )
        self.cleanup_btn.pack(side=tk.LEFT, padx=5)
        
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
        original_frame = tk.LabelFrame(image_frame, text="الصورة الأصلية", font=("Arial", 10, "bold"))
        original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.original_label = tk.Label(original_frame, bg='white', relief=tk.SUNKEN)
        self.original_label.pack(padx=10, pady=10)
        
        # الصورة المحسنة
        enhanced_frame = tk.LabelFrame(image_frame, text="الصورة المحسنة", font=("Arial", 10, "bold"))
        enhanced_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        self.enhanced_label = tk.Label(enhanced_frame, bg='white', relief=tk.SUNKEN)
        self.enhanced_label.pack(padx=10, pady=10)
        
        # إطار النتائج
        results_frame = tk.LabelFrame(main_frame, text="نتائج استخراج النصوص", font=("Arial", 10, "bold"))
        results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # نص النتائج
        self.results_text = scrolledtext.ScrolledText(
            results_frame, 
            wrap=tk.WORD, 
            height=15,
            font=("Arial", 9)
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # شريط الحالة
        self.status_label = tk.Label(
            self.root, 
            text="جاهز لتحميل صورة",
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg='#ecf0f1'
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    def monitor_memory(self):
        """مراقبة الذاكرة"""
        try:
            memory = psutil.virtual_memory()
            memory_text = f"الذاكرة: {memory.percent:.1f}% مستخدمة ({memory.used / (1024**3):.1f} GB / {memory.total / (1024**3):.1f} GB)"
            self.memory_label.config(text=memory_text)
            
            # تحذير إذا كانت الذاكرة عالية
            if memory.percent > 85:
                self.memory_label.config(fg='red')
                messagebox.showwarning("تحذير", "استخدام الذاكرة عالي! يرجى تنظيف الذاكرة أو إغلاق البرامج الأخرى.")
            elif memory.percent > 70:
                self.memory_label.config(fg='orange')
            else:
                self.memory_label.config(fg='black')
            
        except Exception as e:
            self.memory_label.config(text=f"خطأ في مراقبة الذاكرة: {e}")
        
        # تحديث كل 5 ثوان
        self.root.after(5000, self.monitor_memory)
    
    def cleanup_memory(self):
        """تنظيف الذاكرة"""
        try:
            # جمع القمامة
            collected = gc.collect()
            
            # إجبار جمع القمامة لجميع الأجيال
            for generation in range(3):
                collected += gc.collect()
            
            messagebox.showinfo("نجح", f"تم تنظيف الذاكرة! تم تحرير {collected} كائن.")
            self.status_label.config(text="تم تنظيف الذاكرة")
            
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في تنظيف الذاكرة: {e}")
    
    def resize_image_if_needed(self, image):
        """تغيير حجم الصورة إذا كانت كبيرة جداً"""
        height, width = image.shape[:2]
        max_size = int(self.size_var.get())
        
        if max(height, width) > max_size:
            # حساب النسبة
            ratio = max_size / max(height, width)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            
            # تغيير الحجم
            resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            self.status_label.config(text=f"تم تغيير حجم الصورة من {width}x{height} إلى {new_width}x{new_height}")
            return resized
        
        return image
    
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
                # تحميل الصورة
                image = cv2.imread(file_path)
                if image is None:
                    messagebox.showerror("خطأ", "لا يمكن تحميل الصورة")
                    return
                
                # تغيير الحجم إذا لزم الأمر
                image = self.resize_image_if_needed(image)
                
                self.current_image = image
                self.display_image(image, self.original_label)
                self.process_btn.config(state=tk.NORMAL)
                self.status_label.config(text=f"تم تحميل الصورة: {Path(file_path).name}")
                
            except Exception as e:
                messagebox.showerror("خطأ", f"خطأ في تحميل الصورة: {str(e)}")
    
    def display_image(self, image, label, max_size=(400, 300)):
        """عرض صورة في label مع تغيير الحجم"""
        try:
            # تغيير حجم الصورة للعرض
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
            self.enhanced_image = self.enhance_image_pipeline(self.current_image)
            
            # استخراج النصوص
            if self.easyocr_var.get():
                self.easyocr_results = self.extract_text_easyocr(self.enhanced_image)
            else:
                self.easyocr_results = []
            
            self.tesseract_results = self.extract_text_tesseract(self.enhanced_image)
            
            # تحديث الواجهة في main thread
            self.root.after(0, self._update_ui_after_processing)
            
        except Exception as e:
            self.root.after(0, lambda: self._show_error(f"خطأ في معالجة الصورة: {str(e)}"))
    
    def enhance_image_pipeline(self, image):
        """خط أنابيب تحسين الصورة الكامل"""
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
            raise Exception(f"خطأ في تحسين الصورة: {e}")
    
    def extract_text_easyocr(self, image):
        """استخراج النص باستخدام EasyOCR"""
        try:
            import easyocr
            reader = easyocr.Reader(['ar', 'en'], gpu=False)  # تعطيل GPU لتوفير الذاكرة
            results = reader.readtext(image)
            
            extracted_text = []
            for (bbox, text, confidence) in results:
                if confidence > 0.5:
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
            import pytesseract
            custom_config = r'--oem 3 --psm 6 -l ara+eng'
            text = pytesseract.image_to_string(image, config=custom_config)
            
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
    
    def _update_ui_after_processing(self):
        """تحديث الواجهة بعد انتهاء المعالجة"""
        try:
            # عرض الصورة المحسنة
            self.display_image(self.enhanced_image, self.enhanced_label)
            
            # عرض النتائج
            self.results_text.delete(1.0, tk.END)
            
            if self.easyocr_results:
                self.results_text.insert(tk.END, "نتائج EasyOCR:\n")
                self.results_text.insert(tk.END, "-" * 30 + "\n")
                for i, result in enumerate(self.easyocr_results, 1):
                    self.results_text.insert(tk.END, f"{i}. النص: {result['text']}\n")
                    self.results_text.insert(tk.END, f"   الثقة: {result['confidence']:.2%}\n\n")
            
            if self.tesseract_results:
                self.results_text.insert(tk.END, "نتائج Tesseract:\n")
                self.results_text.insert(tk.END, "-" * 30 + "\n")
                for i, result in enumerate(self.tesseract_results, 1):
                    self.results_text.insert(tk.END, f"{i}. النص: {result['text']}\n")
                    self.results_text.insert(tk.END, f"   الثقة: {result['confidence']:.2%}\n\n")
            
            if not self.easyocr_results and not self.tesseract_results:
                self.results_text.insert(tk.END, "لم يتم العثور على نصوص")
            
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
    app = MemoryOptimizedGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
