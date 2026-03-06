# 템플릿 사양: whats_new_template.pptx

## 기본 정보

| 항목 | 값 |
|------|-----|
| 파일 크기 | ~876KB |
| 슬라이드 크기 | 12192000 × 6858000 EMU (13.33" × 7.50") |
| 테마 | AWS Confidential Light (AWS 2024 색상) |
| 기본 폰트 | Amazon Ember (임베디드) |
| 디스플레이 폰트 | Amazon Ember Display (임베디드) |
| 모노 폰트 | Amazon Ember Mono (임베디드) |
| 슬라이드 마스터 | slideMaster1.xml (1개) |
| 레이아웃 | 4개 (slideLayout1~4) |
| 기본 슬라이드 | 2장 (slide1=Title, slide2=콘텐츠) |

### 테마 색상 (AWS 2024)

| 역할 | 색상 | 용도 |
|------|------|------|
| dk1 | #000000 | 기본 텍스트 |
| lt1 | #FFFFFF | 배경 |
| dk2 | #161D26 | 보조 텍스트 (tx2) |
| lt2 | #F3F3F7 | 보조 배경 |
| accent1 | #41B3FF | AWS 블루 |
| accent2 | #AD5CFF | 퍼플 |
| accent3 | #00E500 | 그린 |
| accent4 | #FF5C85 | 핑크 |
| accent5 | #FF693C | 오렌지 |
| accent6 | #FBD332 | 옐로 |
| hlink | #41B1E8 | 하이퍼링크 |

---

## 슬라이드 구조

### slide1.xml — Title Slide

참조 레이아웃: slideLayout2.xml ("Title Slide 2A")

Title Slide는 레이아웃에 배경 이미지, AWS 로고, 세션 ID 배지, 발표자 정보, 저작권 텍스트가 포함되어 있습니다. slide1.xml 자체에는 shape 1개만 있습니다.

| Shape | 이름 | 타입 | 위치 (EMU) | 크기 (EMU) | 용도 |
|-------|------|------|-----------|-----------|------|
| sp | "Title 5" | placeholder (type="ctrTitle") | x:672969 y:2967335 | cx:6460999 cy:923330 | 메인 타이틀 |

샘플 텍스트: `What's New` (스마트 아포스트로피 `&#x2019;` 사용)

레이아웃(slideLayout2)에 정의된 placeholder들:

| idx | 이름 | 용도 | 샘플 텍스트 |
|-----|------|------|------------|
| ctrTitle | "Title 1" | 메인 타이틀 (60pt, Amazon Ember Display) | "Enter title" |
| 1 (subTitle) | "Subtitle 2" | 서브타이틀 (32pt, Amazon Ember Display, tx2 색상) | "Enter subtitle" |
| 10 | "Text Placeholder 7" | 세션 ID (10pt, Amazon Ember Mono, 대문자) | "Enter session ID if required" |
| 11 | "Text Placeholder 9" | 발표자 이름 (20pt, Amazon Ember Display) | "Speaker name (pronouns)" |
| 12 | "Text Placeholder 11" | 발표자 직함/회사 (16pt, Amazon Ember Display) | "Speaker job title / Speaker company" |

**Title Slide 편집 방법:**
- slide1.xml의 `<a:t>What&#x2019;s New</a:t>` → 프레젠테이션 제목으로 교체
- 서브타이틀, 발표자 등은 레이아웃 placeholder이므로 slide1.xml에 `<p:sp>` 추가 필요:

```xml
<p:sp>
  <p:nvSpPr>
    <p:cNvPr id="{새ID}" name="Subtitle"/>
    <p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
    <p:nvPr><p:ph type="subTitle" idx="1"/></p:nvPr>
  </p:nvSpPr>
  <p:spPr/>
  <p:txBody>
    <a:bodyPr/>
    <a:lstStyle/>
    <a:p><a:r><a:rPr lang="ko-KR" dirty="0"/><a:t>{서브타이틀}</a:t></a:r></a:p>
  </p:txBody>
</p:sp>
```

---

### slide2.xml — 콘텐츠 슬라이드

참조 레이아웃: slideLayout3.xml ("Three Content")

콘텐츠 슬라이드는 2개의 shape로 구성됩니다.

#### Shape 1: Title ("Title 1")

| 속성 | 값 |
|------|-----|
| id | 8 |
| 타입 | placeholder (type="title") |
| 위치 | x:375560 y:153253 (x:0.41" y:0.17") |
| 크기 | cx:11479596 cy:727655 (w:12.55" h:0.80") |
| 폰트 | 20pt bold, typeface="+mn-lt" (테마 minor latin = Amazon Ember) |
| 정렬 | anchor="ctr" (수직 중앙) |
| 샘플 텍스트 | "{Title}" |

교체 방법: `<a:t>{Title}</a:t>` → `<a:t>{슬라이드 제목}</a:t>`

#### Shape 2: Table ("Table 3")

| 속성 | 값 |
|------|-----|
| id | 7 |
| 타입 | graphicFrame (테이블) |
| 위치 | x:375560 y:880908 (x:0.41" y:0.96") |
| 크기 | cx:11553088 cy:5201839 (w:12.63" h:5.69") |
| 컬럼 | 1개 (w:11553088 = 12.63") |
| 행 수 | **2** |
| 테이블 스타일 | {3B4B98B0-60AC-42C2-AFA5-B58CD77FA1E5} |
| 셀 마진 | L:121920 R:121920 T:60960 B:60960 (L/R:0.13" T/B:0.07") |

#### Row 구조

| Row | 높이 EMU | 높이 인치 | 역할 | 배경 | 폰트 | 샘플 텍스트 |
|-----|---------|----------|------|------|------|------------|
| 0 | 382957 | 0.42" | 섹션 헤더 | bg1 (흰색) | Amazon Ember 14pt | "Summary" |
| 1 | 4818882 | 5.27" | 메인 본문 | 없음 | +mn-lt 14pt / Malgun Gothic (ea) | (빈 행) |

#### Row 0 (섹션 헤더) 서식
```xml
<a:rPr lang="en-US" sz="1400" dirty="0">
  <a:latin typeface="Amazon Ember" panose="020B0603020204020204" pitchFamily="34" charset="0"/>
  <a:ea typeface="Amazon Ember" panose="020B0603020204020204" pitchFamily="34" charset="0"/>
  <a:cs typeface="Amazon Ember" panose="020B0603020204020204" pitchFamily="34" charset="0"/>
</a:rPr>
```
- `<a:tcPr>` 에 `<a:solidFill><a:schemeClr val="bg1"/></a:solidFill>`

#### Row 1 (메인 본문) 서식
```xml
<a:endParaRPr lang="en-US" sz="1400" dirty="0">
  <a:latin typeface="+mn-lt"/>
  <a:ea typeface="Malgun Gothic" panose="020B0503020000020004" pitchFamily="34" charset="-127"/>
  <a:cs typeface="Amazon Ember" panose="020B0603020204020204" pitchFamily="34" charset="0"/>
</a:endParaRPr>
```
- `<a:tcPr>` 에 배경 없음 (마진만 설정)
- 빈 상태: `<a:endParaRPr>` 만 존재

⚠️ **이 템플릿에는 URL 바(Rectangle 5)가 없습니다.** 이전 `powers/whats_new_template.pptx`와 다릅니다.

---

## 렌더링 워크플로우

1. `python scripts/office/unpack.py assets/whats_new_template.pptx unpacked/`
2. Title Slide 편집 (slide1.xml): `ctrTitle`의 `<a:t>` 교체 + 필요 시 서브타이틀 placeholder 추가
3. 콘텐츠 슬라이드 복제: URL 수 - 1만큼 `python scripts/add_slide.py unpacked/ slide2.xml` 반복 (slide2가 원본, 복제본이 slide3, slide4, ...)
4. `presentation.xml`의 `<p:sldIdLst>` 순서 설정
5. 각 콘텐츠 슬라이드 편집:
   a. Title shape의 `<a:t>{Title}</a:t>` → 슬라이드 제목
   b. 테이블 Row 0 `<a:t>Summary</a:t>` → "개요" (또는 유형별 헤더)
   c. 테이블 Row 1 `<a:txBody>` 전체 교체 (요약 콘텐츠)
6. `python scripts/clean.py unpacked/`
7. `python scripts/office/pack.py unpacked/ output.pptx --original assets/whats_new_template.pptx`

### Row 1 콘텐츠 교체 XML 템플릿

Row 1의 `<a:txBody>` 전체를 아래 패턴으로 교체합니다:

```xml
<a:txBody>
  <a:bodyPr/>
  <a:lstStyle/>
  <a:p>
    <a:r>
      <a:rPr lang="ko-KR" sz="1400" dirty="0">
        <a:latin typeface="Amazon Ember" panose="020B0603020204020204" pitchFamily="34" charset="0"/>
        <a:ea typeface="Amazon Ember" panose="020B0603020204020204" pitchFamily="34" charset="0"/>
        <a:cs typeface="Amazon Ember" panose="020B0603020204020204" pitchFamily="34" charset="0"/>
      </a:rPr>
      <a:t>{텍스트 라인}</a:t>
    </a:r>
    <a:br>
      <a:rPr lang="ko-KR" sz="1400" dirty="0">
        <a:latin typeface="Amazon Ember" panose="020B0603020204020204" pitchFamily="34" charset="0"/>
        <a:ea typeface="Amazon Ember" panose="020B0603020204020204" pitchFamily="34" charset="0"/>
        <a:cs typeface="Amazon Ember" panose="020B0603020204020204" pitchFamily="34" charset="0"/>
      </a:rPr>
    </a:br>
    <!-- 다음 라인 반복 -->
  </a:p>
</a:txBody>
```

bold 텍스트: `<a:rPr>` 에 `b="1"` 추가
빈 줄: `<a:br>` 2개 연속

---

## 테이블 매핑 규칙

이 템플릿은 2행 테이블이므로, summary-agent 출력 전체를 Row 1 하나에 넣습니다.

| 테이블 Row | summary-agent 출력 매핑 |
|-----------|----------------------|
| Row 0 헤더 | "개요" (모든 유형 동일) |
| Row 1 본문 | 게시일 + 개요 + 상세 내용 + 관련 링크 |

### Row 1 콘텐츠 구성 순서

```
유형: {T1a — 신규 기능 추가}
게시일: {YYYY년 M월 D일}
(빈줄)
{개요 3~5문장 — 헤더 없이 바로 시작}
(빈줄)
**{섹션 헤더}**
{본문 — 완결된 문장의 불릿 포인트}
(빈줄)
**{다음 섹션 헤더}**
{본문}
...
(빈줄)
**관련 링크:**
[{링크1}]({URL}) | [{링크2}]({URL})
```

### 분량 판단 규칙

`render_content.py --font-size auto`가 시각적 줄 수를 추정하여 자동 판단:
1. **14pt, 1장** (기본): 시각적 ≤23줄 → `sz="1400"`
2. **12pt, 1장** (약간 넘침): 시각적 ≤27줄 → `sz="1200"`
3. **SPLIT_NEEDED** (많이 넘침): 시각적 >27줄 → 렌더링하지 않고 `SPLIT_NEEDED` 출력 (exit code 2). LLM이 콘텐츠를 2장으로 분할 후 각각 `--font-size 1400`으로 재렌더링

시각적 줄 수 = 슬라이드에서 실제로 보이는 줄 수. 긴 텍스트의 줄바꿈을 반영 (한글=2폭, 영문=1폭, 14pt 한 줄 max 135).

### 마크다운 → XML 변환 규칙

- `### 헤더` → `<a:r>` with `b="1"` (bold) + `<a:br>`
- `[표시텍스트](URL)` → `<a:r>` with `<a:hlinkClick>` + `<a:t>표시텍스트</a:t>` (URL은 `_rels`에 등록)
- `- 불릿 항목` → `<a:r>` with `<a:t>• {텍스트}</a:t>` + `<a:br>`
- `| 테이블 |` → 각 행을 `<a:r>` + `<a:br>`로 변환
- 빈 줄 → `<a:br>` 2개 연속
- 기본: `<a:rPr>` 에 `lang="ko-KR" sz="1400" dirty="0"` + Amazon Ember 3종
- 12pt 모드: `sz="1400"` → `sz="1200"`으로 전체 변경

---

## 레이아웃 파일 참조표

| 파일명 | 이름 | 용도 |
|--------|------|------|
| slideLayout1.xml | Agenda Slide 1 | 사용 안 함 |
| slideLayout2.xml | Title Slide 2A | slide1.xml이 참조 (Title Slide) |
| slideLayout3.xml | Three Content | slide2.xml이 참조 (콘텐츠 슬라이드) |
| slideLayout4.xml | Title and Bulleted Content | 사용 안 함 |
