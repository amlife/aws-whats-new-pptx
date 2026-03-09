---
name: aws-whats-new-pptx
description: "AWS What's New 공지 URL을 입력받아 한국어 요약 또는 번역 + PPTX 프레젠테이션을 생성합니다. 사용자가 AWS What's New URL(https://aws.amazon.com/about-aws/whats-new/... 또는 https://aws.amazon.com/ko/about-aws/whats-new/... 등 로케일 프리픽스 포함)을 1개 이상 제공하면 자동으로 트리거됩니다. 'AWS 새 기능 발표자료 만들어줘', 'What's New 슬라이드로 정리해줘', 'AWS 공지 프레젠테이션', 'whats-new pptx' 등의 요청에도 반응합니다. '번역해줘', '원문 번역', '전문 번역' 요청 시 원문 전체를 한국어로 번역하여 슬라이드를 생성합니다. AWS What's New URL이 포함된 모든 프레젠테이션 요청에 반드시 이 스킬을 사용하세요. URL에 aws.amazon.com/about-aws/whats-new/ 또는 aws.amazon.com/{locale}/about-aws/whats-new/ 패턴이 포함되면 항상 트리거하세요. 사용자가 AWS 발표, 공지 요약, 새 기능 정리, 공지 번역을 요청할 때도 이 스킬이 적합합니다."
---

# AWS What's New → PPTX 생성 스킬

AWS What's New 공지 URL을 입력받아 구조화된 한국어 요약을 생성하고, 이를 기반으로 PPTX 프레젠테이션을 만듭니다.

## 워크플로우 (3단계)

```
URL 입력 → ① 콘텐츠 수집 → ② 구조화 요약 → ③ PPTX 렌더링
```

### Step 1: URL 콘텐츠 수집

사용자로부터 1개 이상의 AWS What's New URL을 받습니다.

**URL 형식:**
```
https://aws.amazon.com/ko/about-aws/whats-new/YYYY/MM/slug/
https://aws.amazon.com/about-aws/whats-new/YYYY/MM/slug/
```

각 URL에 대해:
1. 한국어(`/ko/`) URL 우선 → 실패 시 영어 URL 폴백
2. `web_fetch`로 본문 텍스트 추출
3. 본문 내 참조 링크(공식 문서, 가격 페이지 등)도 `web_fetch`로 보강 정보 수집
4. 페이지의 `<h1>` 타이틀을 추출하여 슬라이드 제목으로 사용한다. 한국어(`/ko/`) 페이지의 타이틀은 그대로 사용하고, 영어 페이지의 타이틀은 한국어로 번역한다. 임의로 축약하거나 재작성하지 않는다.

**MCP 도구 활용 (사용 가능한 경우):**
- `aws___search_documentation`: 서비스/기능 관련 문서 검색
- `aws___get_regional_availability`: 리전 가용성 확인
- 위 도구가 없으면 `web_search`/`web_fetch`로 대체

**진행 보고:**
```
📋 Step 1/3: URL에서 콘텐츠를 수집하고 있습니다... (N개 URL)
  → [URL 1] Amazon ECR 교차 리포지토리 레이어 공유 ✅
  → [URL 2] Trusted Advisor 미사용 NAT 게이트웨이 검사 ✅
```

### Step 2: 콘텐츠 생성 (요약 또는 번역)

**모드 판단:** 사용자 요청에서 모드를 판단합니다.
- **요약 모드 (기본)**: URL만 제공하거나 "요약", "정리", "슬라이드", "발표자료" 등의 키워드
- **번역 모드**: "번역", "translate", "원문 번역", "전문 번역", "원문 그대로" 등의 키워드 포함 시

#### 요약 모드

**[references/summary-agent.md](references/summary-agent.md)를 읽고 그 지침을 정확히 따릅니다.**

각 URL의 수집된 콘텐츠를 summary-agent의 규칙에 따라:
1. 유형 판정 (T1a~T6, 우선순위 기반) → 라벨로 표기
2. 개요 + 상세 내용 + 관련 링크 구조의 한국어 마크다운 요약 생성
3. 자체 점검 체크리스트 수행

#### 번역 모드

**[references/translation-agent.md](references/translation-agent.md)를 읽고 그 지침을 정확히 따릅니다.**

각 URL의 수집된 콘텐츠를 translation-agent의 규칙에 따라:
1. 원문 전체를 한국어로 번역 (원문 구조 유지, 기술 용어 병기)
2. 자체 점검 체크리스트 수행

#### 발표자 스크립트 생성 (필수)

요약/번역 콘텐츠 생성 후, 각 슬라이드에 대한 발표자 스크립트를 반드시 생성합니다:
- 톤: AWS TAM이 고객에게 설명하듯 이해하기 쉬운 구어체
- 슬라이드 내용을 기반으로 "왜 중요한지", "실무에서 어떻게 활용하는지" 맥락을 추가한다
- 분량: 1~2분 분량 (약 200~400자)
- 스크립트 파일은 `/tmp/script_slide{N}.txt`에 저장

**임시 파일 정리 (Step 2 시작 전):**
`rm -f /tmp/script_slide*.txt` — 이전 실행의 잔여 파일을 제거하여 게이트 검증 오류를 방지한다.

**각 URL 처리 워크플로우:**
1. 요약/번역 생성 → `/tmp/content_slide{N}.dat` 저장
2. 발표자 스크립트 생성 → `/tmp/script_slide{N}.txt` 저장

**스크립트 검증 (Step 3 진행 전 필수):**
각 URL에 대응하는 `/tmp/script_slide{N}.txt`가 존재하는지 개별 확인한다 (N = 슬라이드 번호, slide2부터 시작). 누락된 파일이 있으면 해당 URL의 스크립트를 재생성한 후 Step 3으로 진행한다.

**진행 보고:**
```
📝 Step 2/3: 구조화 요약을 생성하고 있습니다... (요약 모드)
  → [URL 1] T1a 신규 기능 추가 — 요약 완료, 스크립트 완료

📝 Step 2/3: 원문을 한국어로 번역하고 있습니다... (번역 모드)
  → [URL 1] 번역 완료, 스크립트 완료
```

### Step 3: PPTX 렌더링

**[references/template-spec.md](references/template-spec.md)를 읽고 템플릿 구조를 파악합니다.**

기본 템플릿: `assets/whats_new_template.pptx`

**슬라이드 구조:**
- Title Slide 1장: slide1.xml 편집 (ctrTitle placeholder 텍스트 교체)
- 콘텐츠 슬라이드 N장: slide2.xml 복제 (Title + 2행 테이블)

각 URL당 1장의 콘텐츠 슬라이드를 생성합니다. 콘텐츠가 많으면 2장까지 확장 가능합니다.

**렌더링 워크플로우:**
1. `python scripts/office/unpack.py assets/whats_new_template.pptx working/`
2. 콘텐츠 슬라이드 복제: URL 수 - 1만큼 `python scripts/add_slide.py working/ slide2.xml` 반복 (presentation.xml에 자동 등록됨)
3. Title Slide 편집 (slide1.xml): Edit 도구로 `ctrTitle`의 `<a:t>` 교체
   - 서브타이틀 추가 권장: "2026년 2월" 또는 "N건의 AWS 업데이트" 등 맥락 (template-spec.md의 서브타이틀 XML 참조)
4. 각 콘텐츠 슬라이드를 `render_content.py`로 원스톱 렌더링:
   ```bash
   # 요약 마크다운을 stdin으로 전달 (working/ 내부에 temp 파일 생성 금지)
   cat /tmp/content_slide2.dat | python scripts/render_content.py \
       working/ppt/slides/slide2.xml - \
       --title "Step 1에서 추출한 원문 타이틀" --header "개요" --font-size auto \
       --script /tmp/script_slide2.txt
   ```
   - `--font-size auto`: 시각적 줄 수 기반 자동 판단 (≤23줄 14pt, ≤27줄 12pt)
   - `--title`: Step 1에서 추출한 원문 페이지 `<h1>` 타이틀을 그대로 사용한다. 임의 축약 금지.
   - `--script`: 발표자 노트에 삽입할 스크립트 파일. 모든 콘텐츠 슬라이드에 반드시 `--script` 옵션을 포함한다 (`add_slide.py`가 notesSlide를 복제하므로 `--script` 없이 렌더링하면 `{script}` 텍스트가 발표자 노트에 그대로 남는다)
   - 하이퍼링크: URL이 자동으로 클릭 가능한 링크로 변환됨 (`_rels` 자동 등록)
   - `유형:` 줄: 자동 스킵됨
   - **SPLIT_NEEDED 처리 (exit code 2)**: 시각적 줄 수가 27줄을 초과하면 렌더링하지 않고 `SPLIT_NEEDED`를 출력합니다. 이 경우:
     1. 요약 콘텐츠를 섹션 헤더(`**...**`) 경계에서 자연스럽게 2개 파트로 분할 (앞: 개요+상세 전반, 뒤: 상세 후반+관련 링크)
     2. `python scripts/add_slide.py working/ slide{N}.xml`으로 추가 슬라이드 생성
     3. 각 파트를 별도 슬라이드에 `--font-size 1400`으로 렌더링 (두 번째 슬라이드 `--title`에 "(계속)" 추가 가능)
     4. 두 번째 슬라이드("(계속)")용 스크립트를 별도 생성한다. 후반부 콘텐츠 기반으로 1~2분 분량(200~400자)을 작성하고, 도입부에 "(이어서)" 연결 멘트를 포함한다. `{script}` placeholder 잔존 방지를 위해 split된 슬라이드에도 반드시 `--script`를 적용한다.
5. `python scripts/clean.py working/`
6. `python scripts/office/pack.py working/ output.pptx --original assets/whats_new_template.pptx`
7. `rm -rf working/` — PPTX 생성 완료 후 working 디렉토리 정리

**주의사항:**
- 콘텐츠 파일은 `working/` 외부(예: `/tmp/`)에 생성 (pack.py 검증 시 "Unreferenced file" 에러 방지)
- 슬라이드가 여러 장이면 서브에이전트로 병렬 렌더링 가능 (각 slide{N}.xml은 독립 파일)

**진행 보고:**
```
✍️ Step 3/3: PPTX를 생성하고 있습니다...
  → [슬라이드 1] Title Slide — 완료
  → [슬라이드 2] 콘텐츠 (URL 1) — 완료
  → [슬라이드 3] 콘텐츠 (URL 2) — 완료
  → PPTX 렌더링 완료: output.pptx
```

---

## 참조 파일

| 파일 | 용도 | 읽는 시점 |
|------|------|----------|
| [references/summary-agent.md](references/summary-agent.md) | 요약 에이전트 규칙 (유형 판정 + 템플릿) | Step 2 시작 시 (요약 모드) |
| [references/translation-agent.md](references/translation-agent.md) | 번역 에이전트 규칙 (원문 번역) | Step 2 시작 시 (번역 모드) |
| [references/template-spec.md](references/template-spec.md) | 템플릿 레이아웃 구조 + shape 맵 | Step 3 시작 시 |
