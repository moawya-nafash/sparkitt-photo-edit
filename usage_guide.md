# دليل الاستخدام - المعالجة المجمعة
## Batch Processing Usage Guide

## نظرة عامة

تم تطوير البرنامج ليدعم معالجة عدد كبير من الصور في وقت واحد باستخدام تقنيات المعالجة المتوازية. يمكنك الآن معالجة مئات أو آلاف الصور بكفاءة عالية.

## الملفات الجديدة

### 1. `batch_processor.py`
- **الوظيفة**: معالج الصور المجمعة الأساسي
- **المميزات**: 
  - معالجة متوازية باستخدام threading أو multiprocessing
  - تتبع التقدم في الوقت الفعلي
  - تصدير النتائج بصيغ مختلفة (JSON, CSV, TXT)
  - إحصائيات مفصلة

### 2. `batch_gui.py`
- **الوظيفة**: واجهة مستخدم رسومية للمعالجة المجمعة
- **المميزات**:
  - واجهة سهلة الاستخدام
  - عرض التقدم بصرياً
  - إحصائيات مفصلة
  - تصدير النتائج

### 3. `batch_demo.py`
- **الوظيفة**: أمثلة توضيحية شاملة
- **المميزات**:
  - مقارنة المعالجة المتوازية مع المتسلسلة
  - مقارنة threading مع multiprocessing
  - أمثلة على تصدير النتائج

## طرق الاستخدام

### 1. سطر الأوامر

#### معالجة مجلد كامل:
```bash
python batch_processor.py /path/to/images -o /path/to/output
```

#### معالجة مع خيارات متقدمة:
```bash
python batch_processor.py /path/to/images -o /path/to/output -w 8 --multiprocessing
```

#### معالجة صورة واحدة:
```bash
python batch_processor.py /path/to/image.jpg -o /path/to/output
```

#### خيارات إضافية:
```bash
# البحث في المجلدات الفرعية
python batch_processor.py /path/to/images -r

# عدم حفظ الصور المحسنة
python batch_processor.py /path/to/images --no-save

# تصدير النتائج بصيغة CSV
python batch_processor.py /path/to/images --format csv
```

### 2. الواجهة الرسومية

```bash
python batch_gui.py
```

**خطوات الاستخدام:**
1. اختر مجلد أو ملف الإدخال
2. اختر مجلد الإخراج (اختياري)
3. اضبط عدد العمال (1-16)
4. اختر الخيارات المطلوبة
5. اضغط "بدء المعالجة"
6. راقب التقدم
7. تصدير النتائج عند الانتهاء

### 3. استخدام برمجي

```python
from batch_processor import BatchProcessor

# إنشاء معالج
processor = BatchProcessor(max_workers=4, use_multiprocessing=False)

# معالجة مجلد
results = processor.process_directory(
    input_dir="path/to/images",
    output_dir="path/to/output",
    recursive=True,
    save_enhanced=True
)

# طباعة الإحصائيات
processor.print_statistics(results)

# حفظ النتائج
processor.save_results(results, "results.json", "json")
```

## خيارات المعالجة

### عدد العمال (Workers)
- **Threading**: مناسب للمهام I/O intensive
- **Multiprocessing**: مناسب للمهام CPU intensive
- **العدد الأمثل**: عادة 4-8 عمال حسب المعالج

### أنواع المعالجة
1. **Threading**: أسرع للصور الصغيرة، أقل استهلاكاً للذاكرة
2. **Multiprocessing**: أسرع للصور الكبيرة، استهلاك أعلى للذاكرة

### خيارات الحفظ
- **حفظ الصور المحسنة**: حفظ نسخ محسنة من الصور
- **تصدير النتائج**: حفظ النتائج بصيغ مختلفة

## تنسيقات التصدير

### JSON
```json
[
  {
    "image_path": "image1.jpg",
    "status": "success",
    "processing_time": 1.23,
    "easyocr_results": [...],
    "tesseract_results": [...]
  }
]
```

### CSV
```csv
image_path,status,processing_time,total_texts_found
image1.jpg,success,1.23,5
image2.jpg,failed,0.00,0
```

### TXT
```
نتائج معالجة الصور المجمعة
==================================================

الصورة 1: image1.jpg
الحالة: success
وقت المعالجة: 1.23 ثانية
عدد النصوص المكتشفة: 5
```

## الإحصائيات المتاحة

- **إجمالي الصور**: عدد الصور المعالجة
- **معدل النجاح**: نسبة الصور المعالجة بنجاح
- **وقت المعالجة**: إجمالي ومتوسط وقت المعالجة
- **النصوص المكتشفة**: إجمالي ومتوسط النصوص لكل صورة

## نصائح للأداء الأمثل

### 1. اختيار عدد العمال
- **معالج 4 أنوية**: 4-6 عمال
- **معالج 8 أنوية**: 6-8 عمال
- **معالج 16 أنوية**: 8-12 عمال

### 2. اختيار نوع المعالجة
- **صور صغيرة (< 1MB)**: Threading
- **صور كبيرة (> 5MB)**: Multiprocessing
- **مزيج**: جرب كلا النوعين

### 3. إدارة الذاكرة
- **صور كثيرة**: قلل عدد العمال
- **صور كبيرة**: استخدم multiprocessing
- **ذاكرة محدودة**: استخدم threading

### 4. تحسين السرعة
- **استخدم SSD**: للوصول السريع للصور
- **أغلق التطبيقات الأخرى**: لتحرير الذاكرة
- **استخدم GPU**: إذا كان متاحاً

## استكشاف الأخطاء

### مشاكل شائعة

#### 1. خطأ في الذاكرة
```
MemoryError: Unable to allocate array
```
**الحل**: قلل عدد العمال أو استخدم threading

#### 2. بطء في المعالجة
**الحل**: 
- زد عدد العمال
- استخدم multiprocessing
- تأكد من استخدام SSD

#### 3. فشل في معالجة بعض الصور
**الحل**:
- تحقق من صيغة الصور
- تأكد من عدم تلف الصور
- راجع ملف السجل

### ملفات السجل
- **batch_processing.log**: سجل مفصل للمعالجة
- **results.json**: النتائج الكاملة

## أمثلة عملية

### مثال 1: معالجة 100 صورة
```bash
python batch_processor.py photos/ -o output/ -w 6 --multiprocessing
```

### مثال 2: معالجة مع تصدير CSV
```bash
python batch_processor.py documents/ -o results/ --format csv
```

### مثال 3: معالجة بدون حفظ الصور المحسنة
```bash
python batch_processor.py images/ --no-save -w 4
```

## الدعم والمساعدة

### مصادر مفيدة
- راجع ملف `batch_demo.py` للأمثلة
- استخدم `test_batch.py` للاختبار
- راجع ملفات السجل للتشخيص

### الحصول على المساعدة
1. تحقق من رسائل الخطأ
2. راجع ملف السجل
3. جرب مع عدد أقل من العمال
4. تأكد من صحة مسارات الملفات

---

**ملاحظة**: المعالجة المجمعة مصممة للتعامل مع آلاف الصور بكفاءة. ابدأ بعدد صغير من الصور للاختبار قبل المعالجة على نطاق واسع.
