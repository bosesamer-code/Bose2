"""Deterministic content engine for the handmade production factory."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_SCENES = ("hook", "lesson", "application", "cta")

REQUIRED_RULES = (
    "one_clear_learning_goal",
    "include_hook",
    "include_practical_steps",
    "include_cta",
    "avoid_unverified_claims",
    "keep_content_beginner_friendly",
)


# Each entry is a small, actionable lesson, not generic filler. Keep advice
# beginner-safe and avoid unsupported promises about sales or results.
LESSON_LIBRARY: dict[str, list[dict[str, str]]] = {
    "crochet_basics": [
        {
            "goal": "عمل عينة كروشيه صغيرة مع الحفاظ على حجم الغرز متقاربًا",
            "hook": "أول عينة كروشيه ليكي؟ خلينا نبدأ من غير استعجال.",
            "lesson": "جهزي خيطًا متوسط السمك وسنارة مناسبة له، واعملي عقدة البداية ثم سلسلة من عشر غرز. عدي الغرز قبل ما تكملي.",
            "application": "اعملي غرزة حشو في كل سلسلة، وخلي شد الخيط ثابتًا من غير ما تشديه بقوة. في نهاية السطر عدي الغرز وقارني عرض البداية بالنهاية.",
            "cta": "احفظي الخطوات وجربي عينة صغيرة، واكتبي لنا إيه أكتر خطوة محتاجة شرح.",
        },
        {
            "goal": "اختيار خيط مناسب لأول تجربة كروشيه",
            "hook": "محتارة تختاري أنهي خيط لأول مشروع كروشيه؟",
            "lesson": "ابدئي بخيط فاتح اللون وناعم نسبيًا، لأن شكل الغرز بيكون أوضح عليه. راجعي ملصق الخيط لمعرفة مقاس السنارة المقترح.",
            "application": "اعملي عدة سلاسل تجريبية بالسنارة المقترحة. لو الحركة صعبة جدًا جربي مقاسًا قريبًا، وسجلي المقاس الذي أعطاك غرزًا مريحة وواضحة.",
            "cta": "احتفظي بعينة التجربة مع ملصق الخيط عشان ترجعي للمقاس لاحقًا.",
        },
        {
            "goal": "اكتشاف أخطاء البداية وتصحيحها",
            "hook": "لو عينة الكروشيه بتوسع أو بتضيق، راجعي الحاجات دي.",
            "lesson": "أكتر حاجة بتلخبط المبتدئ هي نسيان غرزة عند طرف السطر أو تغيير شد الخيط. حطي علامة عند أول وآخر غرزة لو محتاجة.",
            "application": "بعد كل سطر عدي الغرز وقارني العدد بالسطر الأول. لو العدد اتغير، راجعي الطرفين بدل ما تفكي الشغل كله مرة واحدة.",
            "cta": "جربي العد بعد كل سطر، وشاركي النتيجة أو السؤال اللي وقف معاكي.",
        },
    ],
    "handmade_home": [
        {
            "goal": "تخطيط مفرش كروشيه صغير قبل بدء التنفيذ",
            "hook": "عايزة تعملي مفرش صغير؟ ابدئي بعينة وخطة واضحة.",
            "lesson": "حددي مكان استخدام المفرش وقيسي المساحة بشريط قياس. اختاري غرزة تعرفي تنفذيها وخيطًا مناسبًا للاستخدام المقصود.",
            "application": "اعملي عينة من عدة أسطر، وقيسي عرضها. استخدمي القياس لتقدير عدد الغرز، ثم ابدئي جزءًا صغيرًا وراجعي المقاس قبل الاستمرار.",
            "cta": "اكتبي مقاس المفرش والغرض منه قبل ما تشتري الخامات.",
        },
        {
            "goal": "فرز بقايا الخامات لمشروع ديكور بسيط",
            "hook": "بقايا الخامات ممكن تبدأ منها فكرة ديكور جديدة.",
            "lesson": "افرزي البقايا حسب النوع واللون والحجم، واستبعدي القطع التالفة. اختاري خامات متوافقة في طريقة التنظيف والاستخدام.",
            "application": "رتبي القطع على سطح مستوٍ وجربي شكلين أو ثلاثة قبل التثبيت. صوري الترتيب الذي أعجبك وسجلي الخامات المطلوبة لإكماله.",
            "cta": "ابدئي بتصميم صغير من الموجود عندك، وصوري مراحل التجربة.",
        },
        {
            "goal": "اختيار قطعة ديكور عملية تناسب وقتك وخاماتك",
            "hook": "قبل أي مشروع للبيت، اختاري فكرة على قد الخامات والوقت.",
            "lesson": "اكتبي استخدام القطعة ومكانها، ثم حددي الخامات المتاحة والوقت الذي تقدري تخصصيه. تجنبي مشروعًا يحتاج أدوات غير متوفرة عندك.",
            "application": "ارسمي شكلًا بسيطًا على ورقة، وحددي الأبعاد، ثم نفذي نموذجًا صغيرًا للتأكد من المقاس قبل إكمال القطعة.",
            "cta": "احتفظي بالرسم والمقاسات عشان تقدري تكرري التصميم أو تعدليه.",
        },
    ],
    "handmade_business": [
        {
            "goal": "تصوير منتج هاند ميد بالموبايل بصورة واضحة",
            "hook": "مش محتاجة كاميرا احترافية عشان تصوري شغلك بوضوح.",
            "lesson": "نظفي عدسة الموبايل، واختاري ضوء نهار قريب من شباك من غير شمس مباشرة. خلي الخلفية هادية وابعدي الأشياء المشتتة.",
            "application": "صوري لقطة كاملة للمنتج، ولقطة قريبة للخامة والتفاصيل، ولقطة توضح الحجم بجسم مرجعي مناسب. راجعي وضوح الصور قبل النشر.",
            "cta": "جربي نفس المنتج في مكانين للإضاءة وقارني الصور قبل اختيار الأفضل.",
        },
        {
            "goal": "كتابة وصف واضح لمنتج هاند ميد",
            "hook": "الوصف الواضح بيساعد العميل يفهم هو بيشتري إيه.",
            "lesson": "ابدئي باسم القطعة، ثم اذكري الخامة والمقاس واللون وطريقة العناية إذا كانت معلومة عندك. ما تكتبيش ميزة مش متأكدة منها.",
            "application": "اكتبي ثلاث جمل: ما المنتج؟ ما مقاسه وخامته؟ وكيف يمكن طلبه أو السؤال عنه؟ راجعي أن كل معلومة دقيقة قبل النشر.",
            "cta": "اكتبي وصف منتج واحد وراجعيه بالقائمة دي قبل ما تنشريه.",
        },
        {
            "goal": "تحويل فكرة هاند ميد إلى نموذج قابل للتقييم",
            "hook": "قبل ما تعملي كمية من أي فكرة، اختبري نموذجًا واحدًا.",
            "lesson": "حددي مين ممكن يستخدم القطعة، وإيه المشكلة أو الاحتياج اللي بتخدمه. اكتبي الخامات والتكلفة الفعلية والوقت المطلوب من غير تخمين.",
            "application": "نفذي نموذجًا واحدًا، وصوريه، واطلبي رأيًا محددًا عن الاستخدام والمقاس والتشطيب. عدلي التصميم بناءً على الملاحظات قبل تكراره.",
            "cta": "ابدئي بنموذج واحد وسجلي التكلفة والوقت والملاحظات في ورقة.",
        },
    ],
    "winter_handmade": [
        {
            "goal": "تخطيط إكسسوار شتوي بسيط للمبتدئين",
            "hook": "عايزة تبدأي قطعة شتوية هاند ميد؟ اختاري تصميمًا صغيرًا.",
            "lesson": "اختاري إكسسوارًا بسيطًا مثل رباط رأس، وحددي المقاس والخامة المناسبة للملامسة والدفء. راجعي تعليمات الخيط ومقاس السنارة أو الإبر.",
            "application": "اعملي عينة صغيرة، وقيسي عرضها بعد فردها برفق. عدلي عدد الغرز حسب المقاس المطلوب وسجلي العدد قبل بدء القطعة.",
            "cta": "سجلي نوع الخيط والمقاس وعدد الغرز عشان يسهل تكرار التجربة.",
        },
        {
            "goal": "اختيار خامة مناسبة لمشغول شتوي",
            "hook": "مش كل خيط مناسب لكل قطعة شتوية؛ راجعي الملصق وجربي عينة.",
            "lesson": "قارني ملمس الخيط وتعليمات غسله وسمكه، وفكري في طريقة استخدام القطعة. لو القطعة هتلامس الجلد، اختاري خامة مريحة لك.",
            "application": "اعملي عينة صغيرة بالخيط المختار واغسليها حسب تعليمات الملصق إن أمكن. بعد الجفاف افحصي الملمس والمقاس قبل تنفيذ القطعة كاملة.",
            "cta": "احتفظي ببيانات الخيط والعينة لتسهيل اختيار الخامات في المرة القادمة.",
        },
        {
            "goal": "تطوير تصميم شتوي بسيط من خلال عينة",
            "hook": "عايزة تعدلي تصميم شتوي؟ غيري عنصرًا واحدًا كل مرة.",
            "lesson": "ابدئي بتصميم أساسي ومقاس واضح. اختاري تغييرًا واحدًا مثل اللون أو عرض القطعة، حتى تعرفي تأثيره على النتيجة.",
            "application": "اعملي عينتين صغيرتين مع تغيير واحد فقط، وقارني المقاس واستهلاك الخيط والوقت. اكتبي ملاحظاتك قبل اختيار النسخة النهائية.",
            "cta": "جربي تعديلًا واحدًا وسجلي الفرق بدل تغيير كل التفاصيل معًا.",
        },
    ],
}


def load_catalog(path: Path) -> dict[str, Any]:
    catalog = json.loads(path.read_text(encoding="utf-8"))
    if catalog.get("human_approval_required") is not True:
        raise ValueError("human_approval_required must be true")
    if catalog.get("automatic_publish") is not False:
        raise ValueError("automatic_publish must be false")
    rules = catalog.get("generation_rules", {})
    missing = [rule for rule in REQUIRED_RULES if rules.get(rule) is not True]
    if missing:
        raise ValueError(f"missing_generation_rules:{','.join(missing)}")
    return catalog


def validate_lesson(lesson: dict[str, Any]) -> dict[str, Any]:
    scenes = lesson.get("scenes", [])
    if [scene.get("purpose") for scene in scenes] != list(REQUIRED_SCENES):
        raise ValueError("invalid_scene_sequence")
    if any(not str(scene.get("text", "")).strip() for scene in scenes):
        raise ValueError("scene_text_required")
    if any(int(scene.get("duration_seconds", 0)) <= 0 for scene in scenes):
        raise ValueError("scene_duration_required")
    if sum(int(scene["duration_seconds"]) for scene in scenes) < 20:
        raise ValueError("lesson_too_short")
    if lesson.get("human_approval_required") is not True:
        raise ValueError("human_approval_required")
    if lesson.get("publishing", {}).get("automatic_publish") is not False:
        raise ValueError("automatic_publish_must_be_false")
    return lesson


def generate_lesson(catalog: dict[str, Any], topic_id: str, idea_index: int = 0) -> dict[str, Any]:
    topics = {item["topic_id"]: item for item in catalog.get("topics", [])}
    if topic_id not in topics:
        raise ValueError(f"unknown_topic:{topic_id}")

    topic = topics[topic_id]
    ideas = topic.get("ideas", [])
    if not ideas:
        raise ValueError(f"topic_has_no_ideas:{topic_id}")
    if idea_index < 0 or idea_index >= len(ideas):
        raise ValueError(f"invalid_idea_index:{idea_index}")

    idea = ideas[idea_index]
    lesson_data = LESSON_LIBRARY.get(topic_id, [])
    if idea_index >= len(lesson_data):
        raise ValueError(f"lesson_script_missing:{topic_id}:{idea_index}")
    script = lesson_data[idea_index]
    scenes = [
        {"scene": 1, "duration_seconds": 4, "purpose": "hook", "text": script["hook"]},
        {"scene": 2, "duration_seconds": 10, "purpose": "lesson", "text": script["lesson"]},
        {"scene": 3, "duration_seconds": 10, "purpose": "application", "text": script["application"]},
        {"scene": 4, "duration_seconds": 4, "purpose": "cta", "text": script["cta"]},
    ]

    return validate_lesson({
        "content_id": f"{topic_id}-{idea_index + 1:03d}",
        "language": catalog["language"],
        "title": idea,
        "learning_goal": script["goal"],
        "topic": topic["category"],
        "audience": "beginners",
        "format": catalog["default_format"],
        "script": " ".join(scene["text"] for scene in scenes),
        "scenes": scenes,
        "visual_style": "clean_handmade_tutorial",
        "video_format": "mp4_16_9",
        "publishing": {
            "facebook": True,
            "youtube": True,
            "automatic_publish": False,
        },
        "human_approval_required": True,
    })


def generate_queue(
    catalog: dict[str, Any],
    selections: list[tuple[str, int]],
) -> list[dict[str, Any]]:
    queue = [generate_lesson(catalog, topic_id, index) for topic_id, index in selections]
    ids = [item["content_id"] for item in queue]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate_content_id")
    return queue
