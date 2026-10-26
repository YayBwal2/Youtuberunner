# 📐 Youtuberunner — Visual Specification v1.0
### Design Baseline, Proposed Tokens & Technical Acceptance Framework

---

## Design System Status

| Item | Specification |
|---|---|
| **Visual Direction** | Minimal & Premium |
| **Primary Objective** | Viewer Retention |
| **Canvas Proposal** | 1080 × 1920 · 9:16 Vertical Video |
| **Implementation Status** | **Code Unchanged (Design Reference Only)** |
| **Specification Classification** | **Baseline** (အတည်ပြုထားသော စည်းမျဉ်း), **Proposed Token** (စမ်းသပ်မည့် အကြံပြုတန်ဖိုး), **Needs Validation** (စစ်ဆေးပြီးမှ အတည်ပြုမည့်အချက်) |

---

## 1. Global Visual Tokens (Proposed & Baseline)

ဗီဒီယိုတစ်ခုလုံးတွင် တသမတ်တည်း သုံးစွဲမည့် အခြေခံ စံနှုန်းများ ဖြစ်သည်။

### 1.1 Color Palette

| Token | Hex / Value | အမျိုးအစား | သုံးစွဲမှုနှင့် စည်းမျဉ်း |
|---|---|---|---|
| `BG_PRIMARY` | `#0F172A` | Baseline | အဓိက Canvas နောက်ခံအရောင် (Slate Black) |
| `BG_DEEP` | `#090D16` | Baseline | အမှောင်ပိုင်း Scene သို့မဟုတ် Contrast မြှင့်ရန် Scene နောက်ခံ |
| `TEXT_PRIMARY` | `#FFFFFF` | Baseline | အဓိက ဖတ်ရှုရမည့် စာသား (High-contrast pure white) |
| `TEXT_SECONDARY` | `#CBD5E1` | Baseline | အထောက်အကူပြုစာသား၊ Metadata၊ Subtext |
| `ACCENT_HERO` | `#22C55E` | Proposed Token | အဓိက Keyword / Focus Pill Highlight (Neon Emerald) |
| `ACCENT_CODE` | `#38BDF8` | Proposed Token | Code၊ Variable၊ Technical Node အစိတ်အပိုင်းများ (Sky Blue) |
| `ACCENT_WARNING` | `#F59E0B` | Proposed Token | အရေးကြီးသော Warning သို့မဟုတ် Critical Metric (Amber) |

> **Restrained Color Discipline (အရောင်ကန့်သတ်သုံးစွဲမှု စည်းမျဉ်း):**  
> Scene တစ်ခုအတွင်း အထက်ပါ Accent အရောင်အားလုံးကို တစ်ပြိုင်တည်း အားပြင်းပြင်း မသုံးရ။ အဓိက Visual Anchor ကို ခွဲခြားသိသာစေရန် (One Visual Focus) အတွက်သာ အရောင်ကို ရွေးချယ် အသုံးပြုရမည်။

---

## 2. Typography Specification

1080 × 1920 Canvas အတွက် စမ်းသပ်မည့် Initial Tokens များ ဖြစ်ပြီး Final Font Size မဟုတ်သေးပါ။ စမ်းသပ်မှုရလဒ်ပေါ် မူတည်၍ ချိန်ညှိသွားမည်။

| Token | Proposed Size | Weight | သုံးစွဲမှု |
|---|---|---|---|
| `TYPE_HOOK` | 84–104 px | Black / ExtraBold | Hook Scene စာသားကြီး (3–5 Words Only) |
| `TYPE_HERO` | 80–96 px | Bold / Black | အဓိက Keyword / Dominant Subject |
| `TYPE_SECTION` | 48–56 px | Bold | Section Heading |
| `TYPE_NODE` | 30–36 px | Medium / Semibold | Architecture Diagram Node Label |
| `TYPE_CODE` | 28–30 px | Regular / Medium | Terminal Code Line |
| `TYPE_SUBTITLE` | 52–60 px | Medium | Narration Caption / Spoken Word |

### Font Rules
- **English Display:** Inter သို့မဟုတ် SF Pro ကဲ့သို့ ရှင်းလင်းပြတ်သားသော Sans-Serif font ကို အသုံးပြုမည်။
- **Code & Specs:** JetBrains Mono သို့မဟုတ် SF Mono ကို အသုံးပြုမည်။

---

## 3. Canvas, Layout & Safe Area Rules

```
+------------------------------------------+ (0, 0)
|          Top UI Risk Area                | YouTube Shorts Header, Sound Title, Notch
+ - - - - - - - - - - - - - - - - - - - - -+ (y ≈ 240px)
|                                          |
|            PRIMARY VISUAL                |
|                                          |
|            [ HERO WORD ]                 | Focus Area Proposal
|                                          | (Provisional: 840 × 1300px)
|                                          |
+ - - - - - - - - - - - - - - - - - - - - -+ (y ≈ 1540px)
|          Bottom UI Risk Area             | Profile Handle, Title, Subscribe Button
+------------------------------------------+ (0, 1920)
       Right UI Risk Area (≈ 160px for Like, Comment, Share, Remix)
```

### Layout Rules
1. **ဗဟိုဦးစားပေး:** အဓိကစာသား၊ Diagram နှင့် Hero Visual ကို မျက်နှာပြင်အလယ် (Safe Active Zone) တွင် ဦးစားပေးထားမည်။
2. **UI Overlay ထည့်တွက်ခြင်း:** Shorts ၏ ညာဘက် Action Icons (Like, Comment, Share) နှင့် အောက်ခြေ Channel Information (Profile, Title, Audio, CTA) တို့ကို တိကျစွာ ထည့်တွက်ရမည်။
3. **No Hidden Content:** အဓိက အချက်အလက်များကို Native UI Overlay များ၏ အောက်တွင် လုံးဝ မထားရ။
4. **Dynamic Layout Routing:** Layout ကို Fixed 5-slot တစ်မျိုးတည်းအဖြစ် မယူဆဘဲ Scene Archetype အလိုက် စမ်းသပ်မည် (ဥပမာ Hook အတွက် Fullscreen Typo၊ Explanation အတွက် Centered Stage)။
5. **Safe Area သတ်မှတ်ချက် (Needs Validation):** 840 × 1300px Safe Area ကို ယာယီ Design Hypothesis အဖြစ်သာ သတ်မှတ်ထားပြီး၊ Device မျိုးစုံ၊ UI Overlay နှင့် Aspect Ratio အလိုက် အမှန်တကယ် စစ်ဆေးပြီးမှသာ အပြီးသတ် (Finalize) ပြုလုပ်မည်။

---

## 4. Scene Archetypes Specification

### 4.1 Hook Scene (0–2s)
- **ရည်ရွယ်ချက်:** Scroll လုပ်နေသူကို ၂ စက္ကန့်အတွင်း ရပ်တန့်စေရန် အာရုံဖမ်းစားနိုင်သော ပထမဆုံး Visual ဖန်တီးခြင်း (Pattern Interrupt)။
- **Composition (ဖွဲ့စည်းပုံ):**
  - Terminal Card နှင့် ရှုပ်ထွေးသော Diagram များ လုံးဝ မပါဝင်စေရ။
  - အဓိက စကားလုံး ၃–၅ လုံးကိုသာ ကြီးမားစွာ ဦးစားပေးမည် (`TYPE_HOOK` 84–104px)။
  - အဖြူရောင်စာသားနှင့် အစိမ်းရောင် Accent (`#22C55E`) Pill Box တစ်ခုတည်းကိုသာ အဓိကထားမည်။
  - Logo Intro ကို အရှည်ကြီး မပြရ။
- **Motion:**
  - အောက်မှ အပေါ်သို့ Mask Reveal တက်လာမည်။
  - Initial reveal duration: `0.35–0.50 s` (`ease_out_expo`)။
  - Reveal ပြီးနောက် တုန်ခါမှုမရှိဘဲ တည်ငြိမ်စွာ ရပ်တည်မည်။
- **Needs Validation:** Hook တွင် Subtitle ကို ဖယ်ထားပါက အသံပိတ်ကြည့်သူ (Muted Viewers) အတွက် အဓိကအကြောင်းအရာ မပျောက်သွားနိုင်စေရန် Screen စာသားကိုယ်တိုင်က အပြည့်အဝ နားလည်နိုင်မှု ရှိ/မရှိ စမ်းသပ်စစ်ဆေးရမည်။

---

### 4.2 Explanation Scene (2s–25s)
- **ရည်ရွယ်ချက်:** ရှုပ်ထွေးသော နည်းပညာ အယူအဆကို တစ်ဆင့်ချင်း နားလည်စေရန် (Progressive Disclosure)။
- **Composition (ဖွဲ့စည်းပုံ):**
  - Main Stage တစ်ခုတည်းကိုသာ အဓိကထားမည် (Cognitive load မများစေရန်)။
  - Content အလိုက် Expanded Terminal၊ Clean Code၊ Diagram သို့မဟုတ် Metric Comparison ကို ရွေးချယ်မည်။
  - Node ၃ ခု ရှိပါက အားလုံးကို တစ်ပြိုင်တည်း မီးမလင်းဘဲ Narration စကားပြောသံနှင့်အညီ တစ်ဆင့်ချင်း မီးလင်းဖော်ပြမည်။
  - Subtitle ကို Main Visual နှင့် မပြိုင်ဆိုင်စေဘဲ Stage အောက် သီးခြားနေရာချထားမည်။
- **Motion:**
  - Node Reveal နှင့် Connector Draw ဖြင့် ချိတ်ဆက်မည်။
  - Spring motion ကို လိုအပ်သော အဓိက transition တွင်သာ သုံးမည်။
  - အချက်အလက်အသစ် မပါလာသည့်အခါ Animation အသစ်တစ်ခုကို အကြောင်းမဲ့ မထည့်သွင်းရ။
- **Needs Validation:** 840px Stage အကျယ်သည် ဖုန်းမျက်နှာပြင်တွင် စာသားများ မကျပ်တည်းစေဘဲ အမှန်တကယ် သုံးလို့ ရ/မရကို Renderer နှင့် Safe Area စမ်းသပ်မှုအပြီး ဆုံးဖြတ်မည်။

---

### 4.3 Payoff Scene (Ending 3–5s)
- **ရည်ရွယ်ချက်:** အစတွင် ပေးထားသော မေးခွန်း သို့မဟုတ် ပြဿနာကို အဖြေပေးပြီး ကြည့်ရှုသူအား စိတ်ကျေနပ်မှု ပေးနိုင်ရန်။
- **Composition (ဖွဲ့စည်းပုံ):**
  - အဓိကရလဒ် သို့မဟုတ် အဖြေကို စာသားကြီးဖြင့် ရှင်းလင်းစွာ ဖော်ပြမည်။
  - Status Badge ကို အမှန်တကယ် စစ်ဆေးထားသော အထောက်အထားရှိမှသာ သုံးမည်။
  - `[OK] VERIFIED` သို့မဟုတ် `100% RECOVERED` ကဲ့သို့သော မဟုတ်မမှန်သည့် Claim များကို လုံးဝ မသုံးရ။
- **Motion:**
  - Verdict Card ကို Settle In လုပ်ပြီး တည်ငြိမ်စွာ အဆုံးသတ်မည်။
  - Seamless Loop ကို ရည်ရွယ်ထားပါက နောက်ဆုံး Frame နှင့် ပထမ Hook Frame တို့၏ Visual ဆက်စပ်မှုကို စမ်းသပ်ထားရမည်။
- **Needs Validation:** Seamless Loop အောင်မြင်စေရန် Content အဓိပ္ပာယ်၊ Audio အဆက်အစပ်နှင့် Frame Transition တို့ကို သီးခြားစမ်းသပ် အတည်ပြုရမည်။

---

## 5. Motion Token Specification

| Token | Proposed Value | စည်းမျဉ်းနှင့် အသုံးပြုမှု |
|---|---|---|
| `MOTION_HOOK_IN` | 0.35–0.50 s | Mask Reveal (Fast & Punchy Entrance) |
| `MOTION_ELEMENT_IN` | 0.35–0.55 s | Component / Element ဝင်လာခြင်း (Spring Pop-in) |
| `MOTION_HOLD` | Content-dependent | ပရိသတ် အဓိကအချက်ကို ဖတ်ရှုနိုင်ရန် ငြိမ်သက်စွာ ရပ်တည်ချိန် |
| `MOTION_EXIT` | 0.20–0.25 s | လိုအပ်မှသာ အသုံးပြုမည့် လျင်မြန်သော Exit Transition |
| `MOTION_STAGGER` | Content-dependent | Architecture Nodes များ အစဉ်လိုက် ပေါ်လာခြင်း Delay |

### Timing Rules
1. **စကားလုံးအလယ်တွင် မဖြတ်ရ:** Scene Transition ကို Spoken Word တစ်လုံး၏ အလယ်တည့်တည့်မှ ဖြတ်တောက်ခြင်း မပြုရ။
2. **Breath Pause သတ်မှတ်ချက် (Needs Validation):** Breath Pause ကို ရှာဖွေရာတွင် `≥ 0.06 s` (60 ms) ဟူသော စံတစ်ခုတည်းကို အမှန်တကယ် အသက်ရှူအနားယူချိန်ဟု မယူဆရ။ 60 ms သည် တိုတောင်းလွန်းနိုင်သဖြင့် စကားပြောသံ၊ Punctuation နှင့် Semantic Boundary တို့ကိုပါ တွက်ချက်ရမည်။
3. **Rest Stabilization:** Animation ပြီးဆုံးချိန်တိုင်းတွင် Element ၏ Position၊ Scale နှင့် Velocity တို့သည် တည်ငြိမ်စွာ ရပ်တန့်ရမည် ($v = 0$)။
4. **Duration ပုံသေမသတ်မှတ်ရ:** Motion Duration များကို အကြောင်းအရာ အားလုံးအတွက် ပုံစံတူ အတင်းအကျပ် မသတ်မှတ်ရ။

---

## 6. Subtitle System Specification

Subtitle သည် Voice နှင့် Visual တို့ကို ချိတ်ဆက်ပေးသော အစိတ်အပိုင်း ဖြစ်သော်လည်း၊ စာလုံးတစ်လုံးချင်း မီးလင်းပြနေရုံဖြင့် Viewer Retention ရရှိမည်ဟု မယူဆသင့်ပါ။

| Token | Proposed Value | သတ်မှတ်ချက် |
|---|---|---|
| `SUBTITLE_INACTIVE` | 52–58 px | မပြောသေးသော / ပြောပြီးသော စာသားအရွယ်အစား |
| `SUBTITLE_ACTIVE` | 58–64 px | လက်ရှိ အသံထွက်နေသော စကားလုံး အရွယ်အစား |
| `SUBTITLE_ACTIVE_COLOR`| `#22C55E` | အသံထွက်နေသော စကားလုံး မီးလင်းရမည့် အစိမ်းရောင် |
| `SUBTITLE_BASE_COLOR` | `#FFFFFF` | ပုံမှန် စာသားအရောင် |
| `SUBTITLE_MAX_LINES` | 1–2 လိုင်း | စမ်းသပ်မည့် အမြင့်ဆုံး လိုင်းအရေအတွက် |

### အဓိက စည်းမျဉ်းများ
- **Chunking:** စာကြောင်းရှည်များကို အဓိပ္ပာယ်ပြည့်ဝသော အပိုင်းတိုများအဖြစ် ခွဲခြမ်းပြသမည်။
- **Strict Sync:** Narration အသံထွက်နှင့် Subtitle စာသား လုံးဝ မလွဲချော်စေရ။
- **Language / Font Integrity:** စာသား font render လုပ်ရာတွင် Glyph မပျက်စီးစေရန် တိကျစွာ စစ်ဆေးရမည်။
- **WordBoundary & Text Normalization (Needs Validation):** `edge-tts` ၏ `WordBoundary` timestamp များကို အသုံးပြုနိုင်မနိုင် လက်ရှိ pipeline တွင် စစ်ဆေးရမည်။ အထူးသဖြင့် နံပါတ်များ (ဥပမာ `1200` $\to$ `twelve hundred`) နှင့် သင်္ကေတများပါသော စာသားများတွင် Text Normalization မပြီးမချင်း 100% Word Alignment ရရှိပြီဟု မသတ်မှတ်ရ။

---

## 7. Viewer Retention Design Rules

Visual System သည် အောက်ပါ စည်းမျဉ်း ၇ ချက်ကို တင်းကြပ်စွာ လိုက်နာရမည်-

1. **Immediate Relevance:** ပထမဆုံး Visual က ဗီဒီယို၏ အဓိကအကြောင်းအရာကို ချက်ချင်း နားလည်စေရမည်။
2. **Curiosity:** နောက်တစ်ဆင့်တွင် အဖြေ၊ ရှင်းလင်းချက် သို့မဟုတ် အရေးကြီးသော အချက်တစ်ခု ရှိကြောင်း ပရိသတ်ကို ဆွဲဆောင်ထားရမည်။
3. **Progressive Disclosure:** အချက်အလက်များစွာကို တစ်ပြိုင်တည်း မပြဘဲ အစဉ်လိုက် စနစ်တကျ ဖော်ပြမည်။
4. **Meaningful Change:** Scene ပြောင်းတိုင်း ပရိသတ်အတွက် အဓိပ္ပာယ်အသစ် သို့မဟုတ် အချက်အလက်အသစ် တစ်ခု ရှိရမည်။
5. **Payoff:** အစတွင် မေးထားသော မေးခွန်း သို့မဟုတ် ပြဿနာကို နောက်ဆုံးတွင် သေချာပေါက် ဖြေရှင်းပေးရမည်။
6. **No False Promises:** ဗီဒီယိုထဲက Claim များကို Visual က အမှန်တရားထက် ပိုမိုကြီးကျယ်အောင် ချဲ့ကား မဖော်ပြရ။
7. **Test Before Generalizing:** ကြည့်ရှုချိန်နှင့် Retention တိုးတက်မှုကို အမှန်တကယ် Audience Data ရရှိမှသာ တရားဝင် သတ်မှတ်မည်။

---

## 8. Acceptance Criteria — Prototype စမ်းသပ်မည့် စံနှုန်းများ

Code သို့ မကူးပြောင်းမီ စစ်ဆေးရမည့် **Prototype Review Checklist (0/7 Reviewed):**

- [ ] **1. Hook Scene:** အဓိက Visual တစ်ခုတည်း ထင်ရှားပြီး စာသားကို ဖုန်းမျက်နှာပြင်ပေါ်တွင် အလွယ်တကူ ဖတ်နိုင်ရမည်။
- [ ] **2. Explanation Scene:** Diagram သို့မဟုတ် Code ကို တစ်ဆင့်ချင်း နားလည်နိုင်ပြီး Element များ တစ်ခုနှင့်တစ်ခု မပြိုင်ဆိုင်ရ။
- [ ] **3. Payoff Scene:** အဓိက အဖြေကို ရှင်းလင်းစွာ ပေးနိုင်ရမည်ဖြစ်ပြီး မမှန်ကန်သော Badge/Claim မသုံးရ။
- [ ] **4. Subtitles:** အသံနှင့် စာသား Timing တိကျမှုရှိမရှိ စမ်းသပ်ပြီး Font Glyph မပျက်စီးရ။
- [ ] **5. Safe Area:** Shorts UI Overlay နှင့် ဖုန်းအရွယ်အစား အမျိုးမျိုးတွင် အရေးကြီးသော Content များ မဖုံးကွယ်ရ။
- [ ] **6. Performance Verification:** 60-second stress benchmark၊ Peak Memory (tracemalloc) နှင့် Startup Pre-purge disk cleanup အောင်မြင်ရမည်။
- [ ] **7. Retention:** တကယ့် YouTube Audience Data မရရှိသေးသရွေ့ Retention တိုးတက်သွားပြီဟု မကြေညာရ။

---

## 9. နောက်ဆုံး သတ်မှတ်ချက်များနှင့် ရှေ့ဆက်မည့် အစီအစဉ်

Visual Specification v1.0 ၏ ရည်ရွယ်ချက်မှာ Design ကို စနစ်တကျ သတ်မှတ်ပြီး Implementation ဆုံးဖြတ်ချက်များကို မှန်ကန်စွာ အထောက်အကူပြုရန် ဖြစ်သည်။

### Final Technical Fact အဖြစ် မသတ်မှတ်ရသေးသော အချက်များ:
1. Font Size အားလုံးသည် ဖုန်းတိုင်းတွင် အကောင်းဆုံးဖြစ်သည်ဟူသော အချက်။
2. 840 × 1300px သည် YouTube Shorts အတွက် အတိအကျ Safe Area ဖြစ်သည်ဟူသော အချက်။
3. Voice `WordBoundary` သည် Script နှင့် အမြဲတမ်း စကားလုံးတစ်လုံးချင်း တိကျစွာ ကိုက်ညီသည်ဟူသော အချက် (Text normalization လိုအပ်နေသေးသည်)။
4. လက်ရှိ Renderer သည် Scene Archetype အားလုံးကို အပြည့်အဝ ပံ့ပိုးနိုင်သည်ဟူသော အချက် (Dynamic Archetype Routing လိုအပ်နေသေးသည်)။
5. Benchmark ရလဒ်များသည် ရှည်လျားသော ၆၀ စက္ကန့် ဗီဒီယိုအားလုံးအတွက် အတူတူဖြစ်မည်ဟူသော အချက် (Stress test လိုအပ်နေသေးသည်)။

### အကြံပြုထားသော ရှေ့ဆက်လုပ်ငန်းစဉ် (Recommended Next Steps):
> **ဒီ Specification ကို Design Reference အဖြစ် သတ်မှတ်ပြီး Architecture နှင့် Code ကို မပြင်ဆင်မီ —  
> Hook၊ Explanation နှင့် Payoff Scene တစ်ခုစီအတွက် တကယ့် Rendered Prototype Frame / Short Clip များကို သီးခြား စမ်းသပ်ပါမည်။  
> ထိုစမ်းသပ်မှု ရလဒ်များ အတည်ပြုပြီးမှသာ Layout၊ Component နှင့် Rendering Architecture အတွက် ပြင်ဆင်မှုများကို အဆင့်လိုက် ဆက်လက် ဆုံးဖြတ်သွားပါမည်။**
