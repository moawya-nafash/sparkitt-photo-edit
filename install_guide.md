# دليل التثبيت والإعداد
## Installation and Setup Guide

## 1. تثبيت Python والمكتبات

### Windows

```bash
# تثبيت المتطلبات
pip install -r requirements.txt

# تثبيت Tesseract OCR
# 1. تحميل من: https://github.com/UB-Mannheim/tesseract/wiki
# 2. تثبيت البرنامج
# 3. إضافة إلى PATH أو تعيين المسار في الكود
```

### Linux (Ubuntu/Debian)

```bash
# تحديث النظام
sudo apt update

# تثبيت Tesseract
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-ara  # للعربية
sudo apt-get install tesseract-ocr-eng  # للإنجليزية

# تثبيت المتطلبات
pip install -r requirements.txt
```

### macOS

```bash
# تثبيت Tesseract
brew install tesseract
brew install tesseract-lang  # للعربية

# تثبيت المتطلبات
pip install -r requirements.txt
```

## 2. إعداد Tesseract

### Windows
```python
# إضافة هذا السطر في بداية الكود إذا لم يكن Tesseract في PATH
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Linux/macOS
```bash
# التحقق من تثبيت Tesseract
tesseract --version

# التحقق من اللغات المتاحة
tesseract --list-langs
```

## 3. اختبار التثبيت

```bash
# تشغيل المثال التوضيحي
python demo.py

# تشغيل الواجهة الرسومية
python gui_app.py

# تشغيل من سطر الأوامر
python image_enhancer.py sample_image.jpg
```

## 4. استكشاف الأخطاء

### مشاكل شائعة

#### خطأ في Tesseract
```
TesseractNotFoundError: tesseract is not installed or it's not in your PATH
```

**الحل:**
- تأكد من تثبيت Tesseract
- أضف المسار إلى متغير البيئة PATH
- أو عين المسار يدوياً في الكود

#### خطأ في EasyOCR
```
ModuleNotFoundError: No module named 'easyocr'
```

**الحل:**
```bash
pip install easyocr
```

#### مشاكل في الذاكرة
```
CUDA out of memory
```

**الحل:**
- استخدم صور بحجم أصغر
- أغلق التطبيقات الأخرى
- استخدم CPU بدلاً من GPU

#### مشاكل في الخطوط العربية
```
خطأ في عرض النصوص العربية
```

**الحل:**
- تأكد من تثبيت خطوط عربية في النظام
- استخدم matplotlib مع دعم Unicode

## 5. تحسين الأداء

### استخدام GPU مع EasyOCR
```python
# في image_enhancer.py، غير السطر:
self.reader = easyocr.Reader(['ar', 'en'], gpu=True)  # إذا كان لديك GPU
```

### تحسين سرعة المعالجة
```python
# تقليل حجم الصورة قبل المعالجة
def resize_image(image, max_size=1000):
    height, width = image.shape[:2]
    if max(height, width) > max_size:
        ratio = max_size / max(height, width)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        return cv2.resize(image, (new_width, new_height))
    return image
```

## 6. إعدادات متقدمة

### تخصيص معاملات CLAHE
```python
# في enhance_contrast method
clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))  # قيم أعلى = تباين أقوى
```

### تخصيص معاملات Thresholding
```python
# في apply_threshold method
thresh = cv2.adaptiveThreshold(
    image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
    cv2.THRESH_BINARY, 15, 3  # قيم مختلفة للنتائج المختلفة
)
```

### تخصيص معاملات إزالة الضوضاء
```python
# في remove_noise method
denoised = cv2.GaussianBlur(image, (5, 5), 0)  # kernel أكبر = إزالة ضوضاء أقوى
denoised = cv2.medianBlur(denoised, 5)  # kernel أكبر
```

## 7. نصائح للاستخدام الأمثل

### أنواع الصور المناسبة
- ✅ صور النصوص والوثائق
- ✅ صور الشاشات واللقطات
- ✅ صور الكتب والمجلات
- ❌ صور طبيعية بدون نصوص
- ❌ صور بجودة منخفضة جداً

### تحسين النتائج
1. **استخدم صور عالية الدقة** (300 DPI أو أعلى)
2. **تأكد من وضوح النص** في الصورة الأصلية
3. **تجنب الصور المائلة** أو المشوهة
4. **استخدم إضاءة جيدة** عند التقاط الصور

### مقارنة النتائج
- **EasyOCR**: أفضل للنصوص العربية والإنجليزية المختلطة
- **Tesseract**: أفضل للنصوص المنظمة والجداول
- **استخدم كليهما** للحصول على أفضل النتائج

## 8. الدعم والمساعدة

### مصادر مفيدة
- [EasyOCR Documentation](https://github.com/JaidedAI/EasyOCR)
- [Tesseract Documentation](https://tesseract-ocr.github.io/)
- [OpenCV Documentation](https://docs.opencv.org/)

### الحصول على المساعدة
1. تحقق من رسائل الخطأ
2. راجع هذا الدليل
3. ابحث في GitHub Issues
4. اطلب المساعدة في المنتديات

---

**ملاحظة**: هذا البرنامج مصمم للعمل على أنظمة Windows و Linux و macOS. تأكد من تثبيت جميع المتطلبات قبل الاستخدام.
