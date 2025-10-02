# برنامج تحسين الصور للتعرف على النصوص
## Image Enhancement for OCR/Text Recognition

برنامج متقدم لتحسين الصور تلقائياً لتحسين دقة التعرف على النصوص باستخدام تقنيات الذكاء الاصطناعي والتعلم الآلي.

## المميزات

- 🖼️ **تحسين الصور تلقائياً**: تحويل الصور إلى تنسيق مثالي للتعرف على النصوص
- 🔍 **استخراج النصوص**: دعم العربية والإنجليزية باستخدام EasyOCR و Tesseract
- 🎨 **واجهة مستخدم رسومية**: واجهة سهلة الاستخدام مع عرض النتائج بصرياً
- 📊 **تحليل الثقة**: عرض نسبة الثقة لكل نص مستخرج
- 💾 **حفظ النتائج**: إمكانية حفظ الصور المحسنة والنتائج
- 🚀 **المعالجة المجمعة**: معالجة عدد كبير من الصور في وقت واحد
- ⚡ **المعالجة المتوازية**: استخدام threading و multiprocessing لتحسين السرعة
- 📈 **تتبع التقدم**: عرض تقدم المعالجة في الوقت الفعلي
- 📋 **تصدير النتائج**: حفظ النتائج بصيغ JSON, CSV, TXT

## التقنيات المستخدمة

### معالجة الصور
- **OpenCV**: معالجة الصور الأساسية
- **scikit-image**: تحسين جودة الصور وإزالة الضوضاء
- **PIL/Pillow**: التعامل مع الصور

### التعرف على النصوص (OCR)
- **EasyOCR**: دعم متعدد اللغات مع دقة عالية
- **Tesseract**: محرك OCR مفتوح المصدر

### واجهة المستخدم
- **Tkinter**: واجهة مستخدم رسومية
- **Matplotlib**: عرض النتائج بصرياً

## التثبيت

### 1. تثبيت المتطلبات

```bash
pip install -r requirements.txt
```

### 2. تثبيت Tesseract OCR

#### Windows:
1. تحميل Tesseract من: https://github.com/UB-Mannheim/tesseract/wiki
2. تثبيت البرنامج
3. إضافة مسار التثبيت إلى متغير البيئة PATH

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-ara  # للعربية
```

#### macOS:
```bash
brew install tesseract
brew install tesseract-lang  # للعربية
```

## الاستخدام

### 1. استخدام سطر الأوامر

```bash
# معالجة صورة واحدة
python image_enhancer.py path/to/image.jpg

# معالجة بدون حفظ الصورة المحسنة
python image_enhancer.py path/to/image.jpg --no-save

# معالجة بدون عرض النتائج بصرياً
python image_enhancer.py path/to/image.jpg --no-show
```

### 2. المعالجة المجمعة

```bash
# معالجة مجلد كامل
python batch_processor.py /path/to/images -o /path/to/output

# معالجة مع خيارات متقدمة
python batch_processor.py /path/to/images -o /path/to/output -w 8 --multiprocessing

# معالجة صورة واحدة
python batch_processor.py /path/to/image.jpg -o /path/to/output
```

### 3. استخدام الواجهة الرسومية

```bash
# الواجهة العادية
python gui_app.py

# الواجهة للمعالجة المجمعة
python batch_gui.py
```

## خوارزميات التحسين

### 1. المعالجة الأولية
- تحويل الصورة إلى grayscale
- تطبيع الأبعاد

### 2. إزالة الضوضاء
- Gaussian Blur
- Median Filter

### 3. تحسين التباين
- CLAHE (Contrast Limited Adaptive Histogram Equalization)

### 4. Thresholding
- Adaptive Thresholding
- Otsu's Method

### 5. التوضيح
- Kernel-based Sharpening

## أمثلة على الاستخدام

### معالجة صورة نصية

```python
from image_enhancer import ImageEnhancer

# إنشاء معزز الصور
enhancer = ImageEnhancer()

# معالجة صورة
results = enhancer.process_image("document.jpg")

# عرض النتائج
print("النصوص المكتشفة:")
for result in results['easyocr_results']:
    print(f"- {result['text']} (الثقة: {result['confidence']:.2%})")
```

### استخدام مخصص

```python
import cv2
from image_enhancer import ImageEnhancer

# تحميل صورة
image = cv2.imread("image.jpg")

# إنشاء معزز
enhancer = ImageEnhancer()

# تحسين الصورة فقط
enhanced = enhancer.enhance_image_pipeline(image)

# استخراج النصوص
texts = enhancer.extract_text_easyocr(enhanced)
```

## دعم اللغات

- **العربية**: دعم كامل للنصوص العربية
- **الإنجليزية**: دعم كامل للنصوص الإنجليزية
- **أرقام**: دعم الأرقام العربية والإنجليزية

## استكشاف الأخطاء

### مشاكل شائعة

1. **خطأ في Tesseract**:
   - تأكد من تثبيت Tesseract
   - تحقق من مسار التثبيت في PATH

2. **خطأ في EasyOCR**:
   - تأكد من اتصال الإنترنت (لتحميل النماذج)
   - تحقق من تثبيت PyTorch

3. **مشاكل في الذاكرة**:
   - استخدم صور بحجم أصغر
   - أغلق التطبيقات الأخرى

## المساهمة

نرحب بالمساهمات! يرجى:

1. Fork المشروع
2. إنشاء branch جديد
3. إجراء التغييرات
4. إرسال Pull Request

## الترخيص

هذا المشروع مرخص تحت رخصة MIT.

## الدعم

للدعم والاستفسارات، يرجى فتح issue في GitHub.

---

**ملاحظة**: هذا البرنامج مصمم لتحسين دقة التعرف على النصوص في الصور، خاصة للوثائق والصور النصية.
