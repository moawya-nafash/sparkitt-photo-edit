# دليل الاستخدام النهائي - المعالجة الانتقائية
## Final Usage Guide - Selective Processing

## نظرة عامة

تم تطوير البرنامج ليدعم معالجة عدد كبير من الصور (حتى 5000 صورة) مع إمكانية اختيار الصور المحددة وحفظها في مجلدات مخصصة. البرنامج الآن يدعم:

- ✅ **اختيار الصور الانتقائي**: اختيار صور محددة بناءً على معايير مختلفة
- ✅ **المعالجة المجمعة**: معالجة آلاف الصور في وقت واحد
- ✅ **إدارة المجلدات**: تنظيم النتائج في مجلدات مخصصة
- ✅ **تحسين الأداء**: تحسين تلقائي للأداء حسب موارد النظام
- ✅ **واجهات متعددة**: سطر الأوامر والواجهة الرسومية

## الملفات الجديدة

### 1. `selective_processor.py`
**الوظيفة**: معالج الصور الانتقائي الأساسي
**المميزات**:
- اختيار الصور بناءً على النمط، الحجم، التاريخ
- معالجة متوازية مع تحسين الأداء
- إنشاء هيكل مجلدات مخصص
- تتبع التقدم في الوقت الفعلي

### 2. `selective_gui.py`
**الوظيفة**: واجهة مستخدم رسومية للمعالجة الانتقائية
**المميزات**:
- واجهة سهلة لاختيار آلاف الصور
- عرض الصور المتاحة والمختارة
- إحصائيات مفصلة
- تصدير النتائج

### 3. `folder_manager.py`
**الوظيفة**: إدارة المجلدات والتنظيم
**المميزات**:
- إنشاء هيكل مجلدات مخصص
- تنظيم الصور حسب النوع، الحجم، التاريخ
- إنشاء تقارير المجلدات
- تنظيف المجلدات الفارغة

### 4. `performance_optimizer.py`
**الوظيفة**: تحسين الأداء للمعالجة الكبيرة
**المميزات**:
- تحليل موارد النظام
- حساب العدد الأمثل للعمال
- مراقبة الأداء
- توصيات التحسين

## طرق الاستخدام

### 1. الواجهة الرسومية (الأسهل)

```bash
python selective_gui.py
```

**خطوات الاستخدام:**
1. **اختيار مجلد الصور**: اضغط "تصفح" واختر مجلد يحتوي على الصور
2. **فحص الصور**: اضغط "فحص الصور" لرؤية جميع الصور المتاحة
3. **اختيار الصور**: 
   - حدد عدد الصور المطلوب (حتى 5000)
   - اختر نمط الاختيار (عشوائي، أول، آخر، نمط)
   - أدخل نمط البحث إذا أردت
4. **اختيار مجلد الإخراج**: اضغط "تصفح" واختر مجلد الحفظ
5. **تخصيص الإعدادات**:
   - عدد العمال (1-16)
   - نوع هيكل الإخراج
   - حفظ الصور المحسنة
6. **بدء المعالجة**: اضغط "بدء المعالجة"
7. **مراقبة التقدم**: راقب شريط التقدم والإحصائيات
8. **تصدير النتائج**: اضغط "تصدير النتائج" عند الانتهاء

### 2. سطر الأوامر

#### معالجة 5000 صورة:
```bash
python selective_processor.py /path/to/images -o /path/to/output -m 5000
```

#### اختيار الصور بناءً على النمط:
```bash
python selective_processor.py /path/to/images -o /path/to/output -p "document" -m 1000
```

#### معالجة مع خيارات متقدمة:
```bash
python selective_processor.py /path/to/images -o /path/to/output -m 5000 -w 8 --multiprocessing --structure by_date
```

#### اختيار الصور بناءً على الحجم:
```bash
python selective_processor.py /path/to/images -o /path/to/output -s "1000000-5000000" -m 2000
```

### 3. استخدام برمجي

```python
from selective_processor import SelectiveProcessor

# إنشاء معالج
processor = SelectiveProcessor(max_workers=4, use_multiprocessing=False)

# اختيار الصور بناءً على النمط
selected_images = processor.select_images_by_pattern(
    Path("/path/to/images"), 
    "document", 
    recursive=True
)

# معالجة الصور المختارة
results = processor.process_selected_images(
    selected_images,
    Path("/path/to/output"),
    save_enhanced=True,
    structure_type="by_date"
)

# طباعة الإحصائيات
processor.print_statistics(results)
```

## خيارات الاختيار

### 1. اختيار بناءً على النمط
```bash
# اختيار الصور التي تحتوي على "document" في الاسم
python selective_processor.py /path/to/images -p "document" -m 1000
```

### 2. اختيار بناءً على الحجم
```bash
# اختيار الصور بين 1MB و 5MB
python selective_processor.py /path/to/images -s "1000000-5000000" -m 2000
```

### 3. اختيار بناءً على التاريخ
```bash
# اختيار الصور من آخر 30 يوم
python selective_processor.py /path/to/images -d "2024-01-01-2024-12-31" -m 1500
```

### 4. اختيار عشوائي
```bash
# اختيار 5000 صورة عشوائياً
python selective_processor.py /path/to/images -m 5000
```

## أنواع هيكل الإخراج

### 1. Flat (مسطح)
```
output/
├── enhanced_image1.png
├── enhanced_image2.png
└── enhanced_image3.png
```

### 2. By Date (حسب التاريخ)
```
output/
└── 2024-10-02/
    ├── enhanced_image1.png
    ├── enhanced_image2.png
    └── enhanced_image3.png
```

### 3. By Size (حسب الحجم)
```
output/
└── batch_5000/
    ├── enhanced_image1.png
    ├── enhanced_image2.png
    └── enhanced_image3.png
```

### 4. By Source (حسب المصدر)
```
output/
└── from_photos/
    ├── enhanced_image1.png
    ├── enhanced_image2.png
    └── enhanced_image3.png
```

## تحسين الأداء

### 1. حساب العدد الأمثل للعمال
```python
from performance_optimizer import PerformanceOptimizer

optimizer = PerformanceOptimizer()
optimal_workers = optimizer.calculate_optimal_workers("cpu_intensive", 200)
print(f"العدد الأمثل للعمال: {optimal_workers}")
```

### 2. تحسين للمعالجة على نطاق واسع
```python
recommendations = optimizer.optimize_for_large_scale(5000, 2.0)
print(f"التوصيات: {recommendations}")
```

### 3. مراقبة الأداء
```python
# مراقبة موارد النظام
metrics = optimizer.monitor_system_resources(duration=60)
print(f"استخدام المعالج: {metrics['cpu_usage']}")
```

## أمثلة عملية

### مثال 1: معالجة 5000 صورة وثائق
```bash
# إنشاء مجلد للوثائق
mkdir documents_output

# معالجة الصور
python selective_processor.py /path/to/documents -o documents_output -p "doc" -m 5000 -w 6 --structure by_date
```

### مثال 2: معالجة صور كبيرة فقط
```bash
# معالجة الصور الأكبر من 5MB
python selective_processor.py /path/to/images -o large_images_output -s "5000000-999999999" -m 1000
```

### مثال 3: معالجة صور من تاريخ محدد
```bash
# معالجة صور من آخر شهر
python selective_processor.py /path/to/images -o recent_output -d "2024-09-01-2024-10-01" -m 2000
```

### مثال 4: استخدام الواجهة الرسومية
```bash
# تشغيل الواجهة الرسومية
python selective_gui.py
```

## إدارة المجلدات

### 1. إنشاء تقرير المجلد
```bash
python folder_manager.py /path/to/folder --action report --output report.json
```

### 2. تحسين هيكل المجلد
```bash
python folder_manager.py /path/to/folder --action optimize --optimization-type size
```

### 3. تنظيف المجلدات الفارغة
```bash
python folder_manager.py /path/to/folder --action cleanup
```

### 4. إنشاء نسخة احتياطية
```bash
python folder_manager.py /path/to/folder --action backup --output /path/to/backup
```

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
- **selective_processing.log**: سجل مفصل للمعالجة
- **results.json**: النتائج الكاملة

## الدعم والمساعدة

### مصادر مفيدة
- راجع ملف `test_selective.py` للأمثلة
- استخدم `selective_gui.py` للواجهة الرسومية
- راجع ملفات السجل للتشخيص

### الحصول على المساعدة
1. تحقق من رسائل الخطأ
2. راجع ملف السجل
3. جرب مع عدد أقل من العمال
4. تأكد من صحة مسارات الملفات

---

**ملاحظة**: البرنامج مصمم للتعامل مع آلاف الصور بكفاءة. ابدأ بعدد صغير من الصور للاختبار قبل المعالجة على نطاق واسع.
