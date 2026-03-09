# aws-whats-new-pptx

AWS What's New 공지 URL을 입력하면 한국어 구조화 요약과 PPTX 프레젠테이션을 자동 생성하는 [Kiro](https://kiro.dev) agent skill입니다.

## 데모

```
사용자: https://aws.amazon.com/about-aws/whats-new/2025/01/amazon-ecr-cross-repository-layer-sharing/
       이 공지를 슬라이드로 만들어줘

Kiro:  📋 Step 1/3: URL에서 콘텐츠를 수집하고 있습니다...
       📝 Step 2/3: 구조화 요약을 생성하고 있습니다...
       ✍️ Step 3/3: PPTX를 생성하고 있습니다...
       → PPTX 렌더링 완료: AWS_WhatsNew_202501_Amazon_ECR.pptx
```

## 주요 기능

- AWS What's New URL(1개 이상)을 입력받아 자동으로 콘텐츠 수집
- 공지 유형 자동 판정 (T1a 신규 기능 ~ T6 보안/규정준수)
- 실무자 관점의 한국어 구조화 요약 생성
- AWS 공식 템플릿 기반 PPTX 렌더링 (Amazon Ember 폰트, AWS 2024 테마)
- 콘텐츠 분량에 따른 자동 폰트 크기 조절 및 슬라이드 분할
- 하이퍼링크 자동 변환

## 워크플로우

```
URL 입력 → ① 콘텐츠 수집 → ② 구조화 요약 → ③ PPTX 렌더링
```

1. URL에서 본문 텍스트 및 참조 링크 수집 (한국어 우선, 영어 폴백)
2. 유형 판정 + 개요/상세 내용/관련 링크 구조의 한국어 마크다운 요약 생성
3. 템플릿 기반 PPTX 생성 (Title 슬라이드 1장 + URL당 콘텐츠 슬라이드 1~2장)

## 설치

```bash
curl -fsSL https://raw.githubusercontent.com/amlife/aws-whats-new-pptx/main/scripts/install.sh | bash
```

또는 수동 설치:

```bash
git clone https://github.com/amlife/aws-whats-new-pptx.git
cp -R aws-whats-new-pptx/skills/aws-whats-new-pptx ~/.kiro/skills/
```

설치 후 Kiro를 재시작하면 스킬이 활성화됩니다.

## 사전 요구사항

- [Kiro CLI](https://kiro.dev)
- Python 3.10+
- 외부 Python 패키지 불필요 (표준 라이브러리만 사용)

## 프로젝트 구조

```
skills/aws-whats-new-pptx/
├── SKILL.md                          # 스킬 정의 및 워크플로우
├── assets/
│   └── whats_new_template.pptx       # AWS 공식 PPTX 템플릿
├── references/
│   ├── summary-agent.md              # 요약 에이전트 규칙 (유형 판정 + 작성 지침)
│   └── template-spec.md              # 템플릿 레이아웃 사양
├── scripts/
│   ├── render_content.py             # 마크다운 → 슬라이드 XML 렌더러
│   ├── add_slide.py                  # 슬라이드 복제/추가
│   ├── clean.py                      # 미참조 파일 정리
│   └── office/                       # PPTX unpack/pack 및 검증 유틸리티
│       ├── unpack.py
│       ├── pack.py
│       └── validators/
└── evals/
    └── evals.json                    # 스킬 평가 테스트 케이스
```

## 트리거 조건

다음 중 하나에 해당하면 자동으로 이 스킬이 활성화됩니다:

- `https://aws.amazon.com/about-aws/whats-new/` 패턴의 URL 포함
- "AWS 새 기능 발표자료 만들어줘", "What's New 슬라이드로 정리해줘" 등의 요청

## 공지 유형 분류

| 유형 | 설명 |
|------|------|
| T1a | 신규 기능 추가 |
| T1b | 기존 기능 개선 |
| T2 | 지원 범위 확장 (리전, 플랫폼 등) |
| T3 | 가격/정책 변경 |
| T4 | 신규 제품/서비스 출시 |
| T5 | 서비스 간 통합/연동 |
| T6 | 보안/규정준수 |

## 라이선스

MIT
