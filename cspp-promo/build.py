#!/usr/bin/env python3
"""Builds the timeline (timeline.json) and the animated HTML page (build/index.html)
for the CSPP promo video. Every animation is seeked by time, so render.js can capture
frame-exact output."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
os.makedirs(BUILD, exist_ok=True)

# ---------------------------------------------------------------- timeline
dur = {}
with open(os.path.join(BUILD, "vo", "durations.txt")) as fh:
    for line in fh:
        k, v = line.split()
        dur[k] = float(v)

ORDER = ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9"]
LEAD, GAP, PRE, TAIL = 1.25, 0.6, 0.4, 4.2
vo = {}
t = LEAD
EXTRA = {"s1": 1.0, "s3": 0.3, "s8": 0.4}  # extra breathing room after these scenes
for k in ORDER:
    vo[k] = t
    t += dur[k] + GAP + EXTRA.get(k, 0)
TOTAL = round(vo["s9"] + dur["s9"] + TAIL, 2)

scene = {}
for i, k in enumerate(ORDER):
    start = 0.95 if k == "s1" else vo[k] - PRE
    end = (vo[ORDER[i + 1]] - PRE + 0.35) if i + 1 < len(ORDER) else TOTAL + 1
    scene[k] = (round(start, 3), round(end, 3))

timeline = {"fps": 30, "total": TOTAL, "vo": vo, "dur": dur, "scene": scene}
with open(os.path.join(BUILD, "timeline.json"), "w") as fh:
    json.dump(timeline, fh, indent=1)

def at(k, off):
    """absolute time = voiceover start of scene k + offset"""
    return round(vo[k] + off, 3)

def d(k, off):
    return f"--d:{at(k, off)}s"

# ---------------------------------------------------------------- icons
def icon(name, size=64, stroke=None):
    s = stroke or "currentColor"
    P = {
        "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
        "wallet": '<rect x="3" y="6" width="18" height="13" rx="2.5"/><path d="M3 10h18M16 14.5h2"/><path d="M6 6l9-3 2 3"/>',
        "leaf": '<path d="M5 19c0-8 5-14 15-14 0 10-6 15-14 15"/><path d="M5 19c3-4 6-6.5 10-8.5"/>',
        "globe": '<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="3.8" ry="9"/><path d="M3.6 8.5h16.8M3.6 15.5h16.8"/>',
        "people": '<circle cx="9" cy="8" r="3.2"/><path d="M3 20c0-3.6 2.7-6 6-6s6 2.4 6 6"/><circle cx="17" cy="9" r="2.6"/><path d="M16 14.2c2.9.3 5 2.4 5 5.8"/>',
        "shield": '<path d="M12 3l8 3v6c0 4.6-3.4 8-8 9-4.6-1-8-4.4-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
        "calendar": '<rect x="3" y="5" width="18" height="16" rx="2.5"/><path d="M3 10h18M8 3v4M16 3v4"/>',
        "video": '<rect x="2.5" y="6" width="13" height="12" rx="2.5"/><path d="M15.5 10.5l6-3.5v10l-6-3.5"/>',
        "live": '<circle cx="12" cy="12" r="2.5"/><path d="M7.8 7.8a6 6 0 000 8.4M16.2 7.8a6 6 0 010 8.4M5 5a10 10 0 000 14M19 5a10 10 0 010 14"/>',
        "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
        "quiz": '<rect x="4" y="3" width="16" height="18" rx="2.5"/><path d="M8 8h8M8 12h8M8 16h5"/>',
        "rec": '<circle cx="12" cy="12" r="9"/><path d="M10 8.5l5.5 3.5-5.5 3.5z"/>',
        "book": '<path d="M4 5.5C6.5 4 9.5 4 12 5.5 14.5 4 17.5 4 20 5.5V19c-2.5-1.5-5.5-1.5-8 0-2.5-1.5-5.5-1.5-8 0z"/><path d="M12 5.5V19"/>',
        "cert": '<rect x="3" y="4" width="18" height="12" rx="2"/><circle cx="12" cy="15" r="3"/><path d="M10 17.5L9 22l3-1.5 3 1.5-1-4.5M7 8h10"/>',
        "chat": '<path d="M4 18.5l1.2-3.6A7.8 7.8 0 1112 20a7.8 7.8 0 01-4.3-1.3z"/><path d="M9 10.5c.5 2 2 3.6 4.5 4.5"/>',
        "phone": '<rect x="6.5" y="2.5" width="11" height="19" rx="2.5"/><path d="M10.5 18.5h3"/>',
        "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
        "cycle": '<path d="M20 12a8 8 0 01-14 5.3M4 12A8 8 0 0118 6.7"/><path d="M18 3v4h-4M6 21v-4h4"/>',
        "plan": '<rect x="4" y="3" width="16" height="18" rx="2.5"/><path d="M8 9l1.6 1.6L12.5 7.8M8 15l1.6 1.6 2.9-2.8M14.5 9.5H17M14.5 15.5H17"/>',
        "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.3"/>',
        "gift": '<rect x="3" y="9" width="18" height="12" rx="2"/><path d="M3 13h18M12 9v12"/><path d="M12 9c-1.5-3.5-6-4-6-1.5S10 9 12 9zm0 0c1.5-3.5 6-4 6-1.5S14 9 12 9z"/>',
        "star": '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>',
        "group": '<circle cx="12" cy="7.5" r="3"/><circle cx="5" cy="10" r="2.3"/><circle cx="19" cy="10" r="2.3"/><path d="M6.5 20c0-3.3 2.5-6 5.5-6s5.5 2.7 5.5 6M1.5 19c0-2.3 1.4-4.2 3.5-4.2M22.5 19c0-2.3-1.4-4.2-3.5-4.2"/>',
    }[name]
    return (f'<svg class="ic" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{s}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{P}</svg>')

def logo(cls=""):
    return (f'<div class="logo {cls}"><span class="logo-mark">{icon("leaf", 40)}</span>'
            f'<span class="logo-txt"><b>Easy</b><i>PM</i></span></div>')

def scene_attr(k):
    s, e = scene[k]
    return f'class="scene" id="{k}" data-s="{s}" data-e="{e}" style="--s:{s}s;--e:{e - 0.45}s"'

# ---------------------------------------------------------------- scenes
S = []

# 0. Intro sting --------------------------------------------------------
S.append(f'''
<section class="scene" id="s0" data-s="0" data-e="1.6" style="--s:0s;--e:1.15s">
  <div class="sting">
    <div class="sting-ring fx-ring" style="--d:0.05s"></div>
    <div class="fx-pop" style="--d:0.15s">{logo("xl")}</div>
    <div class="sting-line fx-wipe" style="--d:0.45s"></div>
  </div>
</section>''')

# 1. Hook ----------------------------------------------------------------
S.append(f'''
<section {scene_attr("s1")}>
  <div class="hook">
    <div class="orb fx-pop" style="{d("s1", -0.25)}">
      <div class="orb-glow"></div>
      <div class="orb-core">{icon("globe", 210)}</div>
      <div class="orb-leaf">{icon("leaf", 92)}</div>
      <div class="orbit o1"><span></span></div>
      <div class="orbit o2"><span></span></div>
    </div>
    <div class="kicker fx-up" style="{d("s1", -0.05)}">THE FUTURE OF PROJECT MANAGEMENT</div>
    <h1 class="h-hero"><span class="ln">
      <span class="w fx-word" style="{d("s1", 0.0)}">مستقبل</span>
      <span class="w fx-word" style="{d("s1", 0.25)}">إدارة</span>
      <span class="w fx-word" style="{d("s1", 0.5)}">المشاريع</span></span><span class="ln">
      <span class="w fx-word" style="{d("s1", 1.15)}">يبدأ من</span>
      <span class="w grad fx-word" style="{d("s1", 1.5)}">الاستدامة</span></span>
    </h1>
    <p class="sub fx-up" style="{d("s1", 2.0)}">هل أنت مستعد للانتقال بإدارة المشاريع إلى مستوى جديد؟</p>
  </div>
</section>''')

# 2. The shift -----------------------------------------------------------
S.append(f'''
<section {scene_attr("s2")}>
  <div class="shift">
    <h2 class="h2 fx-up" style="{d("s2", 0.0)}">النجاح لم يعد مجرد...</h2>
    <div class="old-row">
      <div class="old-card fx-up dimmer" style="{d("s2", 1.2)};--x:{at("s2", 4.2)}s">
        {icon("clock", 70)}<span>التسليم في الوقت المحدد</span><em class="tick fx-pop" style="{d("s2", 1.6)}">{icon("check", 34)}</em>
      </div>
      <div class="old-card fx-up dimmer" style="{d("s2", 2.4)};--x:{at("s2", 4.2)}s">
        {icon("wallet", 70)}<span>الالتزام بالميزانية</span><em class="tick fx-pop" style="{d("s2", 2.8)}">{icon("check", 34)}</em>
      </div>
    </div>
    <div class="but fx-up" style="{d("s2", 4.2)}">بل أصبح يشمل</div>
    <div class="pillars">
      <div class="pillar fx-rise" style="{d("s2", 4.6)}"><div class="p-ic">{icon("target", 78)}</div><b>قيمة مستدامة</b><small>Sustainable Value</small></div>
      <div class="pillar fx-rise" style="{d("s2", 6.9)}"><div class="p-ic">{icon("leaf", 78)}</div><b>أثر بيئي واجتماعي أقل</b><small>People &amp; Planet</small></div>
      <div class="pillar fx-rise" style="{d("s2", 9.1)}"><div class="p-ic">{icon("shield", 78)}</div><b>حوكمة ومسؤولية مؤسسية</b><small>Governance</small></div>
    </div>
  </div>
</section>''')

# 3. Course reveal -------------------------------------------------------
S.append(f'''
<section {scene_attr("s3")}>
  <div class="reveal">
    <div class="pre fx-up" style="{d("s3", 0.0)}">{logo("sm")}<span>تقدّم لك</span></div>
    <div class="flash" style="{d("s3", 1.55)}"></div>
    <div class="cspp fx-slam" style="{d("s3", 1.6)}">CSPP</div>
    <div class="cspp-en fx-track" style="{d("s3", 3.6)}">Certified Sustainable<br>Project Professional</div>
    <div class="cspp-ar fx-up" style="{d("s3", 5.9)}">إدارة المشاريع المستدامة</div>
    <div class="chips">
      <span class="chip fx-pop" style="{d("s3", 6.6)}">{icon("globe", 34)} شهادة عالمية</span>
      <span class="chip fx-pop" style="{d("s3", 7.1)}">{icon("live", 34)} كورس تفاعلي أونلاين</span>
    </div>
    <div class="first-time fx-up" style="{d("s3", 8.6)}">{icon("target", 46)}<span>برنامج مصمم لتنجح <b>من أول مرة</b> بإذن الله</span></div>
  </div>
</section>''')

# 4. Modules -------------------------------------------------------------
mods = [
    ("01", "Foundations of Sustainable Project Work", "أساسيات العمل في المشاريع المستدامة ودورها في تحقيق القيمة طويلة المدى", "leaf", 1.45),
    ("02", "Sustainability Management Plan (SMP)", "إعداد خطة احترافية لإدارة الاستدامة بأهداف ومؤشرات أداء واضحة", "plan", 3.7),
    ("03", "PRiSM Life Cycle Approach", "دمج الاستدامة في كل مراحل دورة حياة المشروع", "cycle", 5.95),
    ("04", "ESG, Governance & Reporting", "المعايير البيئية والاجتماعية والحوكمة وتقارير الاستدامة", "chart", 9.25),
    ("05", "P5 Standard & Impact Analysis", "تحليل التأثير على الأفراد والكوكب والازدهار والعمليات والمنتجات", "people", 12.45),
]
mod_html = []
for i, (n, en, ar, ic, off) in enumerate(mods):
    nxt = mods[i + 1][4] if i + 1 < len(mods) else dur["s4"] + 0.4
    mod_html.append(f'''
      <div class="mod fx-side" style="{d("s4", off - 0.15)};--a:{at("s4", off)}s;--ad:{round(nxt - off, 3)}s">
        <div class="mod-n">{n}</div>
        <div class="mod-body"><div class="mod-en">{en}</div><div class="mod-ar">{ar}</div></div>
        <div class="mod-ic">{icon(ic, 54)}</div>
      </div>''')
S.append(f'''
<section {scene_attr("s4")}>
  <div class="modules">
    <div class="sec-tag fx-up" style="{d("s4", -0.2)}">ماذا ستتعلم؟</div>
    <h2 class="h2 fx-up" style="{d("s4", 0.05)}"><span class="grad">5 موديولات</span> متكاملة</h2>
    <div class="mod-list">{"".join(mod_html)}</div>
  </div>
</section>''')

# 5. Schedule ------------------------------------------------------------
S.append(f'''
<section {scene_attr("s5")}>
  <div class="sched">
    <div class="sec-tag fx-up" style="{d("s5", -0.2)}">تفاصيل ومواعيد الكورس</div>
    <div class="date-card fx-pop" style="{d("s5", 0.3)}">
      <div class="date-top">موعد البدء</div>
      <div class="date-main"><span class="day">9</span><span class="mon"><b>يناير</b><i>2027</i></span></div>
      <div class="date-dow">السبت</div>
    </div>
    <div class="grid">
      <div class="cell fx-up" style="{d("s5", 3.4)}">{icon("live", 56)}<b><span class="num">6</span> محاضرات</b><small>تفاعلية مباشرة</small></div>
      <div class="cell fx-up" style="{d("s5", 4.2)}">{icon("calendar", 56)}<b>~ 3 أسابيع</b><small>محاضرتان أسبوعيًا</small></div>
      <div class="cell fx-up" style="{d("s5", 5.2)}">{icon("video", 56)}<b>أونلاين بالكامل</b><small>عبر Zoom Meeting</small></div>
      <div class="cell fx-up" style="{d("s5", 6.6)}">{icon("star", 56)}<b>السبت والثلاثاء</b><small>من كل أسبوع</small></div>
    </div>
    <div class="time-bar fx-up" style="{d("s5", 7.9)}">{icon("clock", 54)}<span><b dir="ltr">7:00 – 10:00</b> مساءً</span><small>بتوقيت القاهرة</small></div>
  </div>
</section>''')

# 6. Why Easy PM ---------------------------------------------------------
why = [
    ("quiz", "باقة أسئلة محاكية للامتحان الحقيقي", "على منصة Easy PM + استراتيجيات الحل السريع", 4.0),
    ("rec", "تسجيل جميع المحاضرات", "متاحة للمشاهدة حتى النجاح (Above Target)", 6.2),
    ("book", "المادة العلمية كاملة", "لكل المشتركين", 8.6),
    ("cert", "شهادة حضور معتمدة", "20 ساعة تدريبية = 20 PDUs لتجديد شهادات PMI", 10.8),
    ("chat", "متابعة مستمرة حتى الاجتياز", "جروب واتساب + جروب مذاكرة مع المدرب", 12.7),
]
why_html = "".join(
    f'''<div class="why-row fx-side" style="{d("s6", off)}"><div class="why-ic">{icon(ic, 48)}</div>
        <div><b>{t1}</b><small>{t2}</small></div><em>{icon("check", 30)}</em></div>'''
    for ic, t1, t2, off in why)
S.append(f'''
<section {scene_attr("s6")}>
  <div class="why">
    <div class="sec-tag fx-up" style="{d("s6", -0.2)}">لماذا Easy PM؟</div>
    <div class="atp fx-pop" style="{d("s6", 0.9)}">
      <div class="atp-badge"><span>PMI</span><b>ATP</b></div>
      <div class="atp-txt"><b>شريك تدريب معتمد</b><small>Authorized Training Partner</small></div>
    </div>
    <div class="why-list">{why_html}</div>
    <div class="app fx-up" style="{d("s6", 14.2)}">{icon("phone", 44)}<span>تطبيق Easy PM — شاهد المحاضرات حتى <b>بدون إنترنت</b></span><i>Android · iOS</i></div>
  </div>
</section>''')

# 7. Trainer -------------------------------------------------------------
certs = ["PMP", "PMOCP", "CPMAI", "RMP", "ACP", "SP", "CP", "P3O", "CSPP"]
cert_html = "".join(
    f'<span class="cert fx-pop{" hot" if c == "CSPP" else ""}" style="{d("s7", 3.4 + i * 0.2)}">{c}</span>'
    for i, c in enumerate(certs))
S.append(f'''
<section {scene_attr("s7")}>
  <div class="trainer">
    <div class="sec-tag fx-up" style="{d("s7", -0.2)}">المدرب</div>
    <div class="avatar fx-pop" style="{d("s7", 0.0)}">
      <div class="av-ring"></div><div class="av-in">{icon("people", 1)}<span>م.غ</span></div>
    </div>
    <h2 class="t-name fx-up" style="{d("s7", 0.5)}">م/ محمد غانم</h2>
    <div class="t-role fx-up" style="{d("s7", 2.4)}">{icon("shield", 40)} محاضر معتمد (ATP) من معهد إدارة المشروعات PMI</div>
    <div class="certs">{cert_html}</div>
  </div>
</section>''')

# 8. Offer ---------------------------------------------------------------
S.append(f'''
<section {scene_attr("s8")}>
  <div class="offer">
    <div class="ribbon fx-pop" style="{d("s8", 0.0)}">عرض خاص لفترة محدودة</div>
    <div class="old-price fx-up" style="{d("s8", 3.4)}"><span dir="ltr">$250</span><i class="strike" style="{d("s8", 4.0)}"></i></div>
    <div class="flash" style="{d("s8", 1.5)}"></div>
    <div class="new-price fx-slam" style="{d("s8", 1.55)}"><span class="cur">$</span><span class="count" data-from="250" data-to="125" data-t0="{at("s8", 1.55)}" data-dur="1.1">125</span></div>
    <div class="save fx-pop" style="{d("s8", 2.6)}">وفّر <span dir="ltr">50%</span></div>
    <div class="incl fx-up" style="{d("s8", 3.0)}">شامل باقة الأسئلة المحاكية للامتحان على منصة Easy PM</div>
    <div class="first5 fx-pop pulse" style="{d("s8", 5.6)}">{icon("gift", 54)}<span>اسأل عن <b>الخصم الخاص</b> لأول 5 مشتركين</span></div>
  </div>
</section>''')

# 9. CTA -----------------------------------------------------------------
S.append(f'''
<section {scene_attr("s9")}>
  <div class="cta">
    {logo("lg fx-pop") .replace('class="logo lg fx-pop"', f'class="logo lg fx-pop" style="{d("s9", -0.3)}"')}
    <div class="btn fx-pop" style="{d("s9", 0.0)}">احجز مكانك الآن</div>
    <div class="url fx-up" style="{d("s9", 0.8)}" dir="ltr">easypmp.org</div>
    <div class="url-sub fx-up" style="{d("s9", 1.2)}">أو ابعتلنا رسالة لتفاصيل الاشتراك</div>
    <div class="recap fx-up" style="{d("s9", 1.9)}">
      <span>{icon("calendar", 36)} يبدأ 9 يناير 2027</span><span class="sep"></span><span>{icon("star", 36)} <b dir="ltr">$125</b> بدلًا من <s dir="ltr">$250</s></span>
    </div>
    <div class="tag-en">
      <div class="fx-up" style="{d("s9", 3.1)}">Successful Projects <b>Deliver Results…</b></div>
      <div class="fx-up" style="{d("s9", 5.5)}">Sustainable Projects <b class="grad">Create Lasting Value.</b></div>
    </div>
    <div class="hash fx-up" style="{d("s9", 6.6)}" dir="ltr">#SustainableProjectManagement #PRiSM #P5Standard #ESG #EasyPM</div>
  </div>
</section>''')

# ---------------------------------------------------------------- page
CSS = open(os.path.join(HERE, "style.css"), encoding="utf-8").read()
JS = open(os.path.join(HERE, "runtime.js"), encoding="utf-8").read()

html = f'''<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8">
<style>{CSS}</style></head>
<body>
<div id="stage">
  <div class="bg"><div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div><div class="grid-lines"></div></div>
  <canvas id="fx" width="1080" height="1920"></canvas>
  <header class="topbar fx-down" style="--d:1.0s">{logo("sm")}<span class="tb-pill">PMI ATP · CSPP 2027</span></header>
  {"".join(S)}
  <div class="vignette"></div>
  <div class="progress"><i></i></div>
</div>
<script>window.TIMELINE = {json.dumps(timeline)};</script>
<script>{JS}</script>
</body></html>'''
with open(os.path.join(BUILD, "index.html"), "w", encoding="utf-8") as fh:
    fh.write(html)
print("total", TOTAL, "s")
for k in ORDER:
    print(k, "vo@", round(vo[k], 2), "scene", scene[k])
