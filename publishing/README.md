# Publishing / النشر

## المسار الآمن الحالي

1. شغّل `production-artifact` من فرع `main` وانتظر نتيجة **Success**.
2. راجع الـ artifact بصريًا وسمعيًا، خصوصًا نطق المصري، تزامن الترجمة، ومحتوى كل درس.
3. لو هتجرب YouTube، شغّل `test-youtube-upload` يدويًا، واكتب رقم تشغيل الإنتاج الناجح من `main`، وفعّل تأكيد رفع فيديو اختبار واحد. السكربت يرفض الرفع ما لم يوجد تأكيد صريح، ويتحقق من القناة، ويقصر الرفع على **Private**.
4. لو هتنشر على Facebook Page، استخدم `facebook-page-upload.yml` يدويًا، وحدد `content_id` واحدًا فقط، وفعّل تأكيد النشر العام. لازم تكون أسرار `FACEBOOK_PAGE_ID` و`FACEBOOK_PAGE_ACCESS_TOKEN` مضبوطة في إعدادات المستودع.
5. النشر التلقائي الجماعي يظل **معطّلًا**. لا تضع أي token أو كلمة مرور في الملفات أو في سجلات التشغيل.

## بوابات الحماية

- لازم يكون `automatic_publish: false` في كل package.
- لازم يكون المحتوى `owner_controlled: true` ويعلن الوجهة المطلوبة صراحةً.
- تشغيل Facebook يدويًا يمكن أن يجعل الفيديو ظاهرًا للجمهور على الصفحة؛ لا تؤكد النشر إلا بعد مراجعة الفيديو والوصف.
- لا تعِد محاولة رفع فشل غير واضح على YouTube قبل التحقق من YouTube Studio؛ قد يكون الفيديو اتسجل بالفعل رغم انقطاع الرد.

## متطلبات الاتصال

- YouTube: `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN`، مع ضبط `YOUTUBE_EXPECTED_CHANNEL_HANDLE` في workflow على القناة المقصودة.
- Facebook: `FACEBOOK_PAGE_ID`, `FACEBOOK_PAGE_ACCESS_TOKEN`.
- لا يتم تنفيذ أي رفع بمجرد إنشاء artifact؛ الرفع يحتاج تشغيل workflow يدويًا وتأكيدًا مستقلًا.
