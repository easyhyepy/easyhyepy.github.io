---
title: "Certificate Transparency"
date: 2025-03-30
categories: [Paper]
tags: [Security, Paper]
---

# PKI 복습

![image.png](/images/certificate-transparency/image.png)

이런 중간자 공격 방어하기 위해 등장

![image.png](/images/certificate-transparency/image%201.png)

![image.png](/images/certificate-transparency/image%202.png)

근데 아래 아티클은,, 그런 CA도 MITM 등 공격 가능하다는 내용.

# 문서요약

---

## 1. 배경 및 문제점: CA 시스템의 취약성

현재 인터넷 보안 모델은 인증기관(CA, Certificate Authority)을 신뢰하는 구조 기반

but, CA가 해킹 or 내부에서 부정하게 인증서를 발급 → **중간자 공격(Man-in-the-Middle, MITM)可**

### 🔐 배경: 인증서 체계의 문제점

- **2011년 DigiNotar 사건**
    - 2011년 DigiNotar CA가 해킹되어 `*.google.com` 와일드카드 인증서가 이란에서 MITM 공격에 사용
    - DigiNotar는 **7월 19일 이전**부터 시스템 침해 사실을 인지하고 있었음에도 **한 달 이상 이를 공개하지 않음**.
    - 최소 **531개의 위조 인증서**가 발급되었으며, **전체 수량은 파악 불가** (로그 미비).
    - 2011년 9월 20일, DigiNotar는 결국 **파산 선언**.

### ⚠️ **인증기관(CA) 시스템의 구조적 문제**

> DigiNotar 사건은 유일한 사례가 아니며, 이후에도 여러 CA들이 침해되거나 내부 실수로 위조 인증서를 발급함.
> 

**주요사례**

- **Comodo**: 구글, 야후, 스카이프 등에 대한 가짜 인증서 발급.
- **TürkTrust**: google.com에 대한 비인가 인증서 발급.
- **ANSSI**: 내부 네트워크 감시 목적으로 인증서 발급.

### CA 모델의 근본적 문제

- CA의 보안이 완벽할 수 없음 → 언제든지 해킹 가능.
- 전 세계 수백 개의 CA가 존재 → 그중 하나만 뚫려도 문제 발생.
- CA가 부정 발급을 해도 즉시 탐지 어려움 → 피해 발생 후 뒤늦게 발견.

➡ **기존 보안 구조를 보완할 해결책이 필요함.**

---



## 2. 기존 대안과 한계점

### 1) Pinning (고정 인증서 사용)

웹사이트가 미리 특정 인증서를 등록하고, 브라우저가 **해당 인증서 외에는 거부**하는 방식.

- 인증서 변경이 어렵고, 실수로 키를 잃어버리면 사이트 접근 불가.
- 현재 일부 사이트에서만 적용 가능 (예: Chrome의 일부 내장 핀 목록).

### 2) Notaries (공증 서비스)

다양한 공증 서버가 인증서를 저장하고, **"이 인증서가 이전에도 존재했는가?"**를 확인하는 방식.

- 새로운 인증서 발급 시 무조건 의심받음.
- 중앙 서버(공증 서버)의 신뢰성이 문제.

### 3) DNSSEC (도메인 네임 보안 확장)

도메인 자체에 **보안 키를 등록**해 인증서를 검증하는 방식.

- DNSSEC의 배포율이 낮고, DNS의 split-view(다중 시점 위조) 가능성 존재.
- TCP 포트 53 차단, 공유기 문제 등 실질적 제약 다수.

### 4) 블록체인 기반 인증 (Bitcoin 기반)

블록체인에 인증서 정보를 저장해 위변조 방지.

- 과도한 에너지 소비, 블록체인 공격 가능성 존재.

**→ 기존 대안들은 실용성이 떨어지거나 새로운 문제를 초래함.**

---

## 3. Certificate Transparency (CT): 새로운 접근법

### 핵심 아이디어

- **공개적이고, 누구나 검증 가능한, 추가만 가능한(append-only) 로그 시스템**을 도입.
- 모든 인증서를 발급 시 **로그에 기록**하고, 사용자 브라우저는 **로그에 존재 여부를 확인**.

✅ **모든 인증서를 공개 로그에 저장** → 투명성 확보.

✅ **로그는 변경 불가 (append-only 구조)** → 인증서 위변조 불가.

✅ **브라우저가 인증서가 로그에 있는지 확인 후 연결** → 부정 발급 즉시 탐지 가능.

### 기술적 구현

**Merkle Tree 구조 사용**

- 인증서들을 잎 노드로 하여 해시 트리를 구성.
- 상위 노드는 하위 노드 해시로 계산 → **루트 해시만 비교해도 전체 무결성 확인 가능**.
- Merkle proof를 통해 특정 인증서가 로그에 존재함을 증명.

**Merkle Tree를 사용하는 이유**

- **목표**: 인증서가 실제로 로그에 존재하고, 로그가 위조되지 않았음을 검증
- 로그는 Merkle Tree 구조로 만들어짐
    - 인증서 = 리프 노드(leaf)
    - 각 상위 노드는 하위 노드들의 해시로 구성
- 이 구조를 통해:
    - 특정 인증서가 로그에 들어 있다는 **증명 가능** (inclusion proof)
    - 어제의 로그가 오늘의 로그에 그대로 포함됐는지 확인 → **append-only 속성 검증**

→ Merkle Tree는 CT 로그가 조작 없이 정직하게 유지되고 있는지 검증할 수 있는 핵심 기술

**실무적 문제: Merkle 증명 포함 방식의 한계**

- 클라이언트가 Merkle proof를 이용하려면:
    - CA가 인증서를 발급하기 전에 로그 서버에서 **증명용 데이터(경로 해시들)**를 받아야 함
    - 문제: 로그 서버는 전 세계에 분산되어 있고, **동기화에 시간 걸림**
- CA 입장에서는 로그가 완전히 동기화될 때까지 기다리는 것이 **발급 지연**으로 이어져 현실적이지 않음

**해결책: SCT (Signed Certificate Timestamp)**

- 로그 서버는 인증서를 받자마자, 해당 인증서를 **나중에 등록하겠다는 서명된 약속(SCT)**을 발급
- CA는 이 SCT를 인증서에 포함해 곧바로 발급 가능
- 각 로그는 MMD(Maximum Merge Delay)라는 시간 안에 그 인증서를 실제로 등록해야 함

**🕓 왜 SCT가 필요한가?**

- 만약 로그 등록을 기다린 후에만 인증서를 사용할 수 있다면,
→ 인증서 발급이 **수 분~수 시간 지연될 수 있음**.
- SCT를 이용하면,
→ **CA는 인증서를 바로 발급하고**,
    
    → **로그는 나중에 등록만 하면 됨**
    
    → **브라우저는 SCT를 통해 "등록 예정"임을 인식함**
    

### CT의 동작 방식

1. **인증서 발급 시** → CA는 인증서를 공개 로그에 등록.
2. **CT 로그 서버** → Merkle Tree(머클 트리) 기반으로 인증서를 저장.
3. **웹사이트 접속 시** → 브라우저가 CT 로그를 확인하고, 인증서가 기록되지 않았다면 접속 차단.
    
    

### CT의 장점

✅ **즉각적인 탐지 가능** → 잘못된 인증서 발급 시, 모두가 감지 가능.

✅ **기존 인증서 시스템과 호환 가능** → 서서히 도입 가능.

✅ **사용자에게 부담 없음** → 브라우저가 자동으로 검증.

→ **CA를 100% 신뢰하는 기존 모델을 보완하는 현실적인 해결책.**

---

## 4. CT 시스템의 주요 구성 요소

### 1) CT 로그 서버

- 인증서를 **투명한 방식으로 저장**하는 서버.
- 암호화된 서명과 **Merkle Tree**를 이용해 인증서 변경 감지.

### 2) 서명된 인증서 타임스탬프 (SCT, Signed Certificate Timestamp)

- 인증서가 **CT 로그에 저장될 것이라는 보장**을 의미.
- 브라우저는 **SCT가 없으면 사이트 접속 차단**.

### 3) 모니터링 및 감사 시스템

- CA, 보안 연구자 등이 CT 로그를 모니터링하여 **부정 발급된 인증서 감지**.
- 모든 사람이 로그를 검증할 수 있음.

### 그외)

- **CA / 서버 운영자**: 인증서 발급 시 SCT 포함 및 로그 기록 요청.
- **클라이언트(브라우저)**: SCT가 포함된 인증서만 신뢰, 후속적으로 포함 증명 확인.
- **Gossip 프로토콜**: 서로 다른 클라이언트 간 **로그 뷰 일치성 검증**을 위한 피어 간 정보 교환.

---

## 5. Certificate Transparency의 미래

### 현재 도입 현황

- **Google Chrome**은 2015년부터 **EV(Extended Validation) 인증서에 CT 필수 적용**.
- 주요 CA들도 CT 로그 사용 중.
- 다른 브라우저에서도 CT 지원 확대 예상.

### 확장 가능성 (다른 보안 시스템에 응용)

- **바이너리 투명성 (Binary Transparency)** → 소프트웨어 다운로드 시 악성 코드 삽입 방지.
- **DNSSEC 투명성** → DNS 키의 변조 감지.
- **인증서 폐기(Revocation) 투명성** → 잘못된 인증서가 제대로 폐기되었는지 감시.

➡ **투명성(Transparency) 원칙을 활용해 인터넷 보안을 전반적으로 개선 가능.**

---

## 6. 결론: CT는 실용적이고 효과적인 해결책

기존의 CA 기반 인터넷 보안 모델은 신뢰성 문제를 내포하고 있음.

➡ **Certificate Transparency는 이 문제를 해결할 수 있는 가장 현실적이고 효과적인 방법.**

✅ **발급된 모든 인증서를 공개적으로 검증 가능**

✅ **부정 발급된 인증서를 빠르게 감지 가능**

✅ **기존 인증서 시스템과 호환되며 점진적 도입 가능**

**한 줄 요약:**

➡ **CT는 "CA를 신뢰해야 하는 인터넷 보안 구조"를 "공개 검증 가능한 보안 모델"로 변화시키는 핵심 기술.**


# 아티클 분석

## 1️⃣ Pinning (인증서 고정)

### ✔️ 개념

웹사이트가 **정상적인 인증서(CA)** 목록을 직접 브라우저에 알려주고,

**그 목록에 없는 인증서는 브라우저가 거부**하는 방식입니다.

예:

- Google.com은 "이 CA만 내 인증서를 발급할 수 있다"고 브라우저에 알려줌.
- Chrome은 일부 사이트에 대해 미리 Pinning 정보 내장.

### ⚠️ 문제점

- **핵심 키를 잃었을 때 문제 발생**
    
    → 핀이 만료될 때까지 사이트 접속 불가 (서비스 마비).
    
- **짧은 핀 만료 시간**은 보안 약화
    
    ↔ **긴 핀 만료 시간**은 복구 어려움 증가.
    
- 복구하려면 Chrome에 직접 연락해서 핀을 바꿔야 함 → **확장성 부족**
- 핀을 Chrome이 내장할 경우, 결국 **Google 같은 제3자를 또 신뢰해야 함**.

---

## 2️⃣ Notaries (공증 서버)

### ✔️ 개념

**여러 위치에서 인터넷을 스캔해 인증서를 수집하고**,

사용자가 나중에 “이 인증서 본 적 있어?”라고 물어볼 수 있도록 하는 시스템입니다.

대표 예시:

- [Perspectives Project](http://perspectives-project.org/)
- [Convergence](http://convergence.io/)
- Google의 **SSL Certificate Catalog**도 과거 운영됨.

### ⚠️ 문제점

1. **새로 발급된 정상 인증서도 "못 봤다"고 할 수 있음**
    
    → 단순히 인증서 갱신한 사이트도 접속 차단될 수 있음.
    
2. **out-of-band 통신 필요**
    
    → 페이지 로딩 시 속도 느려지고 실패 확률 높아짐.
    
3. **공격자가 위조 인증서를 대규모로 배포**하면
    
    → Notary들이 그걸 "정상 인증서"로 인식할 위험.
    
4. 결국엔 **또 다른 신뢰된 제3자(Notary 서버)**를 도입하게 됨.

---

## 3️⃣ DNSSEC (Domain Name System Security Extensions)

### ✔️ 개념

DNS에 **암호학적 서명 기능**을 추가해 DNS 정보의 위조나 변조를 막는 보안 확장

이와 관련된 두 가지 주요 메커니즘:

- **DANE** (DNS-based Authentication of Named Entities):
    
    → 사용자가 서버에 접속할 때 DNS에 등록된 인증서 정보를 **직접 검증**
    
- **CAA** (Certification Authority Authorization):
    
    → CA가 인증서 발급 전, DNS에 등록된 허용 CA 목록을 **사전 확인**
    

### ⚠️ 문제점

1. **CAA는 악의적인 CA를 막지 못함**
    
    → 부정한 CA는 CAA 레코드를 무시하고 인증서를 발급할 수 있음.
    
2. **DNSSEC도 제3자를 필요로 함**
    
    → DNS 등록기관과 레지스트라를 신뢰해야 함.
    
    → 그러나 이들의 **보안 수준은 CA보다 더 낮은 경우가 많음**.
    
3. **DNS는 분산 시스템 → 관점 차이 발생 가능**
    
    → 공격자가 피해자에게는 조작된 DNS 기록을 보여주고,
    
    제3자에게는 정상 기록을 보여주는 **Split-view 공격** 가능.
    
4. **보급률이 낮음**
    
    → 수년째 보급이 더딤. 전 세계적으로 아직 잘 사용되지 않음.
    
5. **일부 환경에서 아예 동작 안 함**
    - DNSSEC을 **지원하지 않는 공유기**
    - **Captive portal** (공공 Wi-Fi 로그인 화면)
    - **TCP 53번 포트 차단** (DNSSEC 대형 응답은 UDP→TCP 필요)

📌 참고: SMTP(이메일)에서는 DNSSEC + DANE이 상대적으로 유용할 수 있음

→ 기존에 DNS에 의존하고 보안이 약한 구조이기 때문.

---

## 4️⃣ 비트코인 기반 솔루션 (예: DNSChain)

### ✔️ 개념

DNS나 키 정보를 **블록체인에 저장**해 변경 불가능한 방식으로 관리하자는 시도.

예: DNSChain 프로젝트 ([GitHub 링크](https://github.com/okTurtles/dnschain))

### ⚠️ 문제점

1. **지속적으로 막대한 에너지를 낭비함**
    
    → 저자는 "역사상 가장 환경을 해치는 발명"이라고 표현함.
    
2. **진정한 분산화는 실현되지 않음**
    
    → 강력한 공격자가 블록체인 전체 기록을 통제할 수 있음.
    
3. **검증 체계가 없음**
    
    → 블록체인에 뭐가 들어갔는지 **누가 맞고 누가 틀린지 판별할 수 없음**.
    
4. **결국 또 다른 신뢰 대상이 생김**
    
    → 블록체인에서 **합의를 형성하는 참여자들(노드 운영자)**이 새로운 신뢰된 제3자가 됨.
    

## CT?

![IMG_0842.jpeg](/images/certificate-transparency/IMG_0842.jpeg)

## Merkle Tree를 어떻게 활용하는지

> "이 인증서가 진짜 로그에 있었는지,
> 
> 
> 그리고 어제까지의 로그가 오늘 로그에도 그대로 남아 있는지를
> 
> 수학적으로 증명할 수 있다.
> 
> 그 중심엔 Merkle Tree와 루트 해시가 있다."
> 

### 우리가 로그에서 원하는 두 가지

1. **“이 인증서, 진짜 로그에 들어 있어?”**
    
    → 인증서가 정말 기록됐는지 **검증**할 수 있어야 함
    
2. **“로그는 순서대로만 추가됐고, 중간에 삭제나 수정은 없었어?”**
    
    → 즉, **append-only**인지 확인하고 싶음
    
    → “어제까지의 로그 내용이 오늘 로그에도 그대로 포함돼 있나?” 확인
    

---

### Merkle Tree로 이걸 어떻게 해?

**1. 인증서가 로그에 들어 있는지 확인**

- 로그는 인증서를 Merkle Tree 구조로 정리해요.
- Merkle Tree는 **각 인증서(잎)**들의 해시 값을 위로 위로 합쳐서 **루트 해시**를 만들어요.
- 이 루트 해시는 **전체 로그의 요약본**이죠.

**확인 방법:**

- 누군가 "이 인증서가 로그에 들어 있다"고 주장하면,
    
    그 사람은 다음을 보여줘야 해요:
    
    - 인증서의 **해시 값**
    - 그 해시가 **루트 해시로 연결되는 데 필요한 주변 해시값 목록**

→ 이걸로 **루트 해시를 재계산**해보면,

정말로 이 인증서가 로그에 포함됐는지 확인할 수 있어요.

---

**2. 로그가 순서대로만 추가됐는지 확인 (append-only)**

- Merkle Tree는 **하루가 지나고 인증서가 더 추가되면**,
    
    **루트 해시도 새로 계산**돼요.
    
- 그런데 **어제까지의 인증서들은 그대로** 들어 있으니까,
    
    어제의 루트 해시는 오늘의 루트 해시로부터 **해시 연결로 증명 가능**해요.
    

→ 즉, 어제의 로그가 **수정 없이** 오늘의 로그에 그대로 들어 있다는 걸

**수학적으로 증명할 수 있음!**

---

**마지막 조각: 로그가 "서명"함**

- Merkle Tree의 **루트 해시**는 그냥 해시가 아니라, **로그 서버가 서명한 값**
- 이걸 통해:
    - **루트가 조작되지 않았다는 보증**
    - → 결국 **로그 전체가 조작되지 않았다는 보증**

## Certificate Transparency 시스템 완성을 위한 마지막 요소

1️⃣ **문제 제기: 로그가 잘못 행동하면 어떻게 할까?**

- 로그가 인증서를 누락하거나 조작했을 때,
    
    **그 사실을 증명할 수 있어야** 신뢰할 수 있는 시스템이 됨.
    

2️⃣ **해결책: 로그가 Merkle Tree 루트에 서명**

- 로그는 Merkle Tree의 **루트 해시값에 서명**함.
- 루트 해시는 전체 로그 내용의 요약이므로,
    
    → 이 해시에 서명하면 **전체 로그 내용도 함께 보증하는 효과**를 가짐.
    

## 실제 구현에서의 고민(trade-off: 4)

### 1. **가용성 vs 일관성 (Availability vs Consistency)**

> “로그는 항상 응답할 수 있을 만큼 가용성이 높아야 하고, 동시에 로그의 상태가 일관되어야 한다.”
> 

**진짜 로그에 등록되어 있는지** 증명하고 싶음.

- P) 초기에는 Merkle proof를 인증서에 직접 포함하려 했음.
    
    하지만 로그 서버들이 전 세계에 흩어져 있는 여러 인스턴스를 **동기화(synchronization)**해야 append-only 속성을 보장할 수 있음.
    
    인증서 발급 전에 로그 동기화를 기다려야 하므로, **CA의 발급 파이프라인이 느려짐**.
    
- **S) SCT 방식**으로 전환.
    - **SCT(Signed Certificate Timestamp)**
        - 해당 인증서를 로그에 등록하겠다는 로그 서버의 서명된 약속
        - 미래의 등록을 보장하는 서명된 증거
        - SCT는 **즉시 발급 가능**하며, CA는 이를 인증서에 포함시켜 바로 사용자에게 제공할 수 있음.
        - 각 로그 서버는 **MMD(Maximum Merge Delay)**라는 상한 시간 내에, 해당 인증서를 **실제로 로그에 포함해야 함**.
    - 과정: **CA → CT 로그 서버 → SCT 생성 → CA → 사용자 → 클라이언트** 흐름
        
        1. CA → CT 로그 서버: 인증서 제출 요청
        
        - CA은 새로 발급할 인증서를 **CT 로그 서버에 제출**한다.
        - 이때 인증서는 아직 사용자에게 전달되지 않은 상태이며, 로그에 기록되기 전임.
        
        2. CT 로그 서버 → CA: SCT 발급
        
        - 로그 서버는 인증서를 받은 뒤, 해당 인증서를 **나중에 로그에 포함하겠다는 약속**으로 **SCT**를 생성하여 **CA에게 반환**한다.
        - SCT는 해당 인증서에 대한 **서명된 시점 정보와 로그 서버의 확인 서명**을 포함
        
        **3. CA → 사용자(또는 서버 운영자): 인증서 + SCT 전달**
        
        - CA는 **발급한 인증서에 SCT를 포함**시켜 최종 사용자(예: 웹사이트 운영자)에게 전달한다.
        - 이 인증서는 이후 TLS 서버에 설치되어, 클라이언트에게 제공된다.
        
        **4. 사용자 → 클라이언트(브라우저): 인증서 + SCT 제공**
        
        - 사용자가 웹사이트에 접속하면, 서버는 **SCT가 포함된 인증서**를 브라우저에게 전송한다.
        - 브라우저는 SCT가 포함되어 있는지 확인한 뒤 접속을 허용한다.
            
            SCT가 없거나 유효하지 않으면, 브라우저는 접속을 차단할 수 있다.
            
        - **CA는 SCT를 받은 즉시 인증서를 발급**할 수 있어, 발급 과정이 지연되지 않습니다.
        - **로그 서버는 추후 일정 시간(MMD, Maximum Merge Delay) 내에 인증서를 실제 로그에 등록**하면

---

### 2. **Maximum Merge Delay (MMD) 설정**

> “SCT를 발급한 뒤, 실제로 로그에 등록되기까지 허용되는 최대 지연 시간(MMD)을 어떻게 설정할 것인가?”
> 

**MMD란?**

- **SCT가 발급된 인증서를 CT 로그에 실제로 포함시켜야 하는 최대 허용 시간**
- 예: 로그 서버가 SCT를 발급한 후, **24시간 이내에** 해당 인증서를 로그에 넣어야

**● 트레이드오프의 양측 입장**

| 이해관계자 | 원하는 MMD | 이유 |
| --- | --- | --- |
| **감시자
 (log monitors)** | **짧은 MMD** | SCT 발급 후 가능한 빨리 로그에 포함돼야 부정행위를 빨리 감지할 수 있음. 
로그가 악의적으로 조작되면 등록을 **고의로 지연**시킬 수 있기 때문. |
| **로그 운영자
 (log operators)** | **긴 MMD** | 로그 시스템이 여러 서버로 구성되어 있고, 예외 상황(소프트웨어 오류, 네트워크 지연 등)에서도 **안정적 동기화**를 위해 여유 시간이 필요함. |

**● 기타 고려사항**

- SCT 발급 이후의 처리 속도는 **CA나 공격자가 통제할 수 없음**
    
    → 로그 서버가 독립적으로 등록 여부와 시점을 결정
    
- 현재까지 **적절한 MMD 기준은 확정되지 않았으며**,
    
    최소 몇 시간에서 최대 **수일(예: 48시간)**까지도 가능성이 있음
    
- **짧은 MMD**: 감시자(log monitors) 입장에서는 이상적인 설정 (악의적 지연 탐지 가능).
- **긴 MMD**: 로그 운영자 입장에서는 유리 (시스템 오류 등 발생 시 안정적 운영 가능).
- 현실적으로는 **몇 시간 ~ 며칠까지 허용해야 할 수도 있음**.
- → 보안성과 운영 효율성 사이의 균형이 필요.

---

### 3. **로그 수 (Number of Logs)**

> 하나의 인증서를 몇 개의 CT 로그에 기록할 것인가?
> 
> 
> 로그 수를 늘리면 보안성이 높아지지만, 시스템에 부담이 커진다.
> 
> 이 문제는 보안성과 효율성 사이에서 균형을 잡아야 하는 트레이드오프.
> 

**로그 수를 늘리는 이유 (보안 강화)**

1. **로그가 손상되거나 부정행위를 할 경우 대비**
    - 어떤 로그가 부정행위를 하면 브라우저(클라이언트)는 그 로그를 더 이상 신뢰하지 않음.
    - 만약 인증서에 포함된 SCT들이 **모두 그 "신뢰할 수 없는 로그"에서 온 것**이라면,
        
        → 해당 인증서는 **브라우저에서 거부됨.**
        
2. **공격자 탐지를 어렵게 만듦**
    - SCT가 여러 로그에 분산되어 있으면 → 공격자는 인증서를 숨기려면 **모든 관련 로그를 동시에 속여야 → 감지 가능성↑, 공격 난이도↑**

---

**로그 수를 줄이고 싶은 이유 (성능 문제)**

1. **TLS 핸드셰이크 데이터 크기↑**
    - 여러 개의 SCT를 포함하면, **초기 연결 시 데이터 크기↑**
2. **인증서 생성 시간↑**
    - CA가 여러 로그에 요청을 보내고 SCT를 기다리는 시간 필요
3. **로그 저장소·대역폭 부담↑**
    - 동일한 인증서가 여러 로그에 중복 저장되면 **로그 서버의 부하↑**

---

**현재 제안되는 기준**

- **최소 2개의 로그에 기록**
- **인증서 유효 기간이 길수록 더 많은 로그에 기록**
    - 예: 유효 기간이 39개월을 초과하는 경우, **5개의 로그에 기록**

---

**📌 요약**

> 로그 수가 많을수록 보안은 강화되지만, 시스템 성능과 효율성은 저하된다.
> 
> 
> 현재는 **인증서 유효 기간에 따라 최소 2개 이상, 최대 5개 로그 기록이 권장**된다.
> 

---

### 4. **무엇을 로그에 포함시킬 것인가?**

> “모든 인증서를 로그에 포함시킬 수 있을까?”
> 
- 이상적으로는 **모든 인증서(anything)**를 기록하면 가장 투명할 것처럼 보인다.
- 하지만 현실적으로는 로그의 크기가 **너무 커지면 관리가 불가능**해진다.
→ 아무도 감시할 수 없는 로그는 **존재 의미가 없다**는 것이 핵심.

S) 현실적인 기준을 적용:

- **클라가 신뢰하는 CA 체인에 연결되는 인증서만** 포함
    - 어차피 브라우저가 인식하지 않는 인증서는 **접속 자체가 되지 않음**.
    - 그러한 인증서를 기록해도 실효성이 낮다.
- **자체 서명(self-signed)** 인증서는 대부분 제외
    - 이유: 스팸 문제, 폐기 불가, 브라우저가 애초에 안 받아들임

📌 요약

> 이론적으로는 모든 인증서를 로그에 넣는 것이 이상적이지만,
> 
> 
> **현실적으로는 관리 가능한 범위 내에서, 신뢰된 CA 체인에 속한 인증서만 포함**하는 것이 바람직하다.
> 
> **Self-signed 인증서는 기술적, 실용적 이유로 포함하기 어렵다.**
> 

## The ecosystem: CT 생태계 구성 요소 및 역할

“Certificate Transparency(CT) 시스템이 제대로 작동하려면, 누가 어떤 역할을 해야 하는가?”

**1. 인증서를 로그에 기록하는 주체 (등록자): CA 또는 사이트 운영자**

- 처음에는 주로 **CA가 인증서를 로그에 등록**할 것으로 예상됨.
- 하지만 **서버 운영자(site operators)**가 직접 SCT를 포함하는 방식(TLS 확장)을 사용할 수도 있음.
    - 예: Apache HTTPD가 실험적으로 지원 중
- TLS 확장을 이용하면, SCT를 **인증서에 고정하지 않고 유연하게 갱신**할 수 있음.
    - → 더 적은 수의 SCT로도 인증서를 운영할 수 있고, **불필요한 폐기 위험 감소**

---

**2. 클라이언트(브라우저)의 역할**

- 브라우저는 인증서에 **SCT가 포함되어 있는지 확인**해야 함.
- 브라우저는 연결 시 **로그를 신뢰하되**,
    
    나중에 **로그가 정말로 그 인증서를 포함했는지 별도로 검증**해야 함 (proof of inclusion 확인).
    
- 이는 **로그 조작을 탐지**하기 위한 핵심 절차.

---

**3. 로그를 감시하는 제3자 (모니터, 감사자)**

- **사이트 운영자, CA, 연구자 등**은 로그를 **지속적으로 감시**해야 함.
    - CA가 권한 없는 도메인에 인증서를 발급했는지
    - 비표준 확장 필드나 플래그가 있는지
    - 로그가 **append-only 속성을 어겼는지** 또는 **MMD를 초과했는지** 등도 감시 대상
- 이를 통해 **부정행위나 시스템 이상을 감지**

---

**4. 모든 참여자**

→ **로그가 모든 사람에게 똑같이 보이는지 확인하는 역할**

- 로그가 사용자한테는 "A 인증서 있다" 하고
    
    실제 웹사이트 주인한테는 "없다"고 말하면 문제 생김 → **split view**
    
- 그래서 서로 받은 로그의 **루트 해시 같은 요약 정보**를 **서로 비교해서 일치 여부를 확인**해야 함.

---

## ✅ Gossip: CT 로그의 **일관성(consistency)** 검증을 위한 정보 교환

---

**왜 Gossip이 필요한가?**

- CT 로그는 **누구에게나 똑같은 내용을 보여줘야** 함.
- 그런데 악의적인 로그는 사용자 A에겐 "인증서 있음", 사용자 B에겐 "없음"이라며 **다른 뷰(split view)**를 보여줄 수 있음.
- 이런 상황을 **브라우저 하나만으로는 감지할 수 없음** → 참여자 간의 **상호 비교(gossip)**가 필요

---

**Gossip은 어떻게 이뤄지는가?**

- **클라이언트끼리**, 혹은 **클라이언트 ↔ 서버 간**에 **정보 교환**
- 방식은 여러 프로토콜 위에서 가능:
예: **XMPP, SMTP, P2P 연결**, 등등

> 현재 제안된 초기 방식은 → TLS 연결 위에 piggyback
> 
> 
> → 웹사이트에 연결할 때, **몇 가지 정보를 함께 전송**하여 gossip 수행
> 

> 📌 핵심 문장: "Whenever a client connects to a server, it sends a few items to the server [...] in return the server sends a few items back."
> 

---

**주고받는 정보: 무엇을 gossip하나?**

가장 기본이 되는 항목: **STH (Signed Tree Head)**

- **STH = 로그의 현재 상태를 요약한 해시값 + 서명**
- STH만 가지고도 “내가 본 로그 상태”를 다른 참여자와 비교할 수 있음

> 📌 핵심 문장: "Logs are summarized by STHs, so gossiping them is clearly the least a client would wish to do."
> 

---

**STH의 장점**

1. **서명되어 있음** → 위조, 스팸 불가
2. **두 STH 사이의 consistency proof 계산 가능**
→ 오래된 STH는 버릴 수 있음 → 캐시 공간 절약

---

🔹 앞으로 더 확장될 수 있는 Gossip 항목들

- **STH consistency proofs** (두 STH 사이가 이어졌는지 증명)
- **SCT inclusion proofs** (이 인증서가 실제 로그에 있는지)

---

🔹 결론

- **Gossip = 참여자 간 로그 상태를 공유하고 비교하는 방식**
- 목적: **CT 로그가 모두에게 동일한 상태를 보여주고 있는지 검증**
- 아직은 **구체적인 실행 방식은 미정**이며, 시뮬레이션을 통해 연구 중

---

**✅ 한 줄 요약**

Gossip은 클라이언트들이 서로 본 CT 로그 상태(STH 등)를 비교함으로써, 로그가 모두에게 동일한 정보를 제공하는지 검증하는 메커니즘이다.

## ✅ Other Uses of Transparency — 투명성(log 기반 증명)의 확장 응용

**Certificate Transparency(CT)**에서 시작된 "투명성(Transparency)" 개념이 **다른 보안 분야에도 응용될 수 있다**는 것을 설명하는 내용

---

### 1. **Binary Transparency**

> 💡 소프트웨어 배포의 투명성 확보
> 
- 인터넷에서 다운로드 가능한 **애플리케이션 실행 파일(binary)**도 로그에 기록
- 이 파일이 **악성인지 아닌지는 판단하지 않지만**,**누구나 감시할 수 있게 만들면** 사용자 표적 공격이 어려워짐

---

### 2. **DNSSEC Transparency**

> 💡 DNS 기반 인증 구조 감시
> 
- **DNSSEC**는 CA 없는 대안 인증 방식이지만,**레지스트리/레지스트라**(DNS 등록 기관)의 신뢰성 문제가 존재
- **DNSSEC 키를 로그에 기록하면**, 부정 행위나 오류를 **투명하게 감시**할 수 있음

---

### 3. **Revocation Transparency**

> 💡 인증서 폐기 절차의 신뢰 확보
> 
- 어떤 인증서가 악성임을 알게 되었을 때 → **폐기(revoke)** 필요
- 하지만 일부 시스템에서는 **폐기 상태를 조작하거나 선택적으로 은폐 가능**
- 로그를 이용해 폐기 내역을 기록하면, **폐기 여부가 조작되지 않았음을 검증 가능**

---

### 4. **ID-to-Key Mapping Transparency**

> 💡 이메일, 메신저 ID ↔ 공개키(PGP, OTR 등) 매핑 감시
> 
- 예: “이 이메일 주소는 이 공개키와 연결되어 있다” 같은 정보
- 이런 매핑을 **투명하게 기록하면**,
사용자가 신뢰할 수 있는 키를 확인하는 데 도움

---

### 5. **Trusted Timestamps**

> 💡 신뢰 가능한 타임스탬프 제공
> 
- 현재는 디지털 공증인(notary)을 **신뢰해야만** 타임스탬프를 믿을 수 있음
- 하지만 공증인이 모든 타임스탬프를 로그에 기록한다면,**신뢰하지 않아도 투명하게 검증 가능**

---

**✅ Other Constructions — 새로운 구조: Sparse Merkle Tree**

> ✔ 투명한 "키-값 매핑(map)"을 위해 고안된 자료구조
> 
- 기존 Merkle Tree는 모든 값이 들어가야 하므로 너무 크고 계산이 어려움
- **Sparse Merkle Tree**는 **대부분 비어 있는 매우 큰 트리(예: 2²⁵⁶)**를 가정
- 빈 값들은 동일한 해시값을 공유하므로 **트리 전체를 계산하지 않아도 됨**
- 결과적으로, **효율적이면서도 검증 가능한 포함증명** 가능

> ✔ 이 구조는 일반 로그 시스템의 보조 수단으로 사용 가능
> 

---

📌 핵심 요약

| 분야 | 목적 |
| --- | --- |
| Binary Transparency | 배포되는 소프트웨어가 공개적으로 감시되고 있음을 보장 |
| DNSSEC Transparency | DNS 키 관리의 정당성을 감시 |
| Revocation Transparency | 인증서 폐기 절차의 조작 방지 |
| ID-to-Key Mapping | 이메일/메신저 ↔ 공개키 연결을 신뢰성 있게 관리 |
| Trusted Timestamps | 공증인을 신뢰하지 않아도 되는 시간 인증 방식 |
| Sparse Merkle Tree | 효율적인 대규모 투명한 맵 구조 (포함 증명 가능) |

## ✅ Certificate Transparency의 도입 현황 (Status)

### 1. **구글 중심의 적극적 개발 및 운영**

- Google이 CT를 **직접 개발 중**이며,
    
    **운영 중인 로그 2개**, 연말까지 **3번째 로그 예정**
    
- CT 관련 모든 핵심 구성 요소는 **오픈소스로 공개됨**

---

### 2. **다른 기관들의 참여**

- *ISOC, Akamai, 여러 인증기관(CAs)**도
    
    **공개 로그(public logs)** 운영을 계획 중
    

---

### 3. **Chrome 브라우저의 지원**

- Google Chrome은 이미 **CT를 지원**
- **2015년 1월부터**, **EV 인증서(Extended Validation Certificates)**에 대해
    
    **CT 사용을 필수화(mandatory)** 할 예정
    

---

### 4. **업계의 수용도**

- 전체 인증서 발급량 기준으로,
    
    **94% 이상의 CAs**가 **EV 인증서에 SCT 포함**에 동의함
    

---

### 5. **향후 계획**

- EV 인증서에서 **CT 시스템이 안정적으로 작동하는 것을 확인**한 후
    
    → **모든 인증서**에 대해 CT 적용 예정
    
-