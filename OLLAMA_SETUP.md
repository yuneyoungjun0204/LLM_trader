# Ollama 설정 가이드

LLM_Trader를 Ollama 로컬 모델로 전환하는 완벽한 가이드입니다.

---

## 📋 목차

1. [Ollama란?](#ollama란)
2. [하드웨어 요구사항](#하드웨어-요구사항)
3. [설치 방법](#설치-방법)
4. [모델 다운로드](#모델-다운로드)
5. [설정 변경](#설정-변경)
6. [연결 테스트](#연결-테스트)
7. [사용 방법](#사용-방법)
8. [문제 해결](#문제-해결)

---

## 🤖 Ollama란?

**Ollama**는 로컬 컴퓨터에서 대형 언어 모델(LLM)을 실행할 수 있게 해주는 오픈소스 도구입니다.

### 장점
- ✅ **완전 무료** - API 비용 없음
- ✅ **무제한 요청** - Rate limit 없음
- ✅ **프라이버시** - 데이터가 외부로 전송되지 않음
- ✅ **빠른 응답** - 로컬 실행으로 낮은 지연시간
- ✅ **오프라인 사용 가능**

### 단점
- ❌ GPU 필요 (권장)
- ❌ 디스크 공간 필요 (모델당 4-10GB)
- ❌ 초기 설정 필요

---

## 💻 하드웨어 요구사항

### 최소 사양
| 구성 요소 | 최소 사양 | 권장 사양 |
|-----------|----------|----------|
| **GPU** | RTX 3060 (12GB VRAM) | RTX 4070+ (12GB+ VRAM) |
| **RAM** | 16GB | 32GB |
| **저장 공간** | 40GB 여유 공간 | 100GB SSD |
| **OS** | Windows 10/11, macOS, Linux | Windows 11, macOS |

### 모델별 VRAM 요구사항

| 모델 | 크기 | VRAM (FP16) | VRAM (Q4) | 용도 |
|------|------|-------------|-----------|------|
| **Qwen2.5 14B** | 9GB | 12GB | 6GB | 메인 거래 분석 |
| **Qwen2-Math 7B** | 5GB | 7GB | 4GB | 기술 지표 계산 |
| **DeepSeek-R1 7B** | 5GB | 7GB | 4GB | 패턴 추론 |
| **Llama 3.1 8B** | 6GB | 8GB | 4GB | 뉴스 요약 |

> **참고**: Q4 = 4비트 양자화 모델 (VRAM 절반, 성능 약간 감소)

### GPU 없이 사용 (CPU만)
- ✅ 가능하지만 **매우 느림** (10-100배)
- RAM 32GB+ 권장
- 소형 모델(7B) 권장

---

## 📥 설치 방법

### Windows

1. **Ollama 다운로드**
   ```
   https://ollama.com/download/windows
   ```

2. **설치 파일 실행**
   - `OllamaSetup.exe` 더블클릭
   - 기본 설정으로 설치

3. **설치 확인**
   ```cmd
   ollama --version
   ```

### macOS

```bash
# Homebrew로 설치
brew install ollama

# 또는 공식 설치 프로그램 사용
# https://ollama.com/download/mac
```

### Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

---

## 📦 모델 다운로드

Ollama가 설치되면 터미널/명령 프롬프트에서 모델을 다운로드합니다.

### 1. Ollama 서버 시작

```bash
ollama serve
```

> **참고**: Windows에서는 자동으로 백그라운드에서 실행됩니다.

### 2. 모델 다운로드 (새 터미널)

```bash
# 메인 분석 모델 (14B - 가장 중요)
ollama pull qwen2.5:14b

# 수학 계산 모델 (7B)
ollama pull qwen2-math:7b

# 추론 모델 (7B)
ollama pull deepseek-r1:7b

# 요약 모델 (8B)
ollama pull llama3.1:8b
```

### 양자화 모델 (VRAM 절약)

VRAM이 부족하면 4비트 양자화 버전 사용:

```bash
ollama pull qwen2.5:14b-q4_K_M
ollama pull qwen2-math:7b-q4_K_M
ollama pull deepseek-r1:7b-q4_K_M
ollama pull llama3.1:8b-q4_K_M
```

### 다운로드 확인

```bash
ollama list
```

---

## ⚙️ 설정 변경

### 1. `config/config.ini` 수정

```ini
[ai_providers]
# Ollama로 변경
provider = ollama

# Ollama 서버 URL (기본값)
ollama_base_url = http://localhost:11434/v1

# 작업별 모델 설정
ollama_main_model = qwen2.5:14b           # 메인 거래 분석
ollama_math_model = qwen2-math:7b         # 기술 지표 계산
ollama_reasoning_model = deepseek-r1:7b   # 패턴 추론
ollama_summary_model = llama3.1:8b        # 뉴스 요약
```

### 2. 양자화 모델 사용 시

```ini
ollama_main_model = qwen2.5:14b-q4_K_M
ollama_math_model = qwen2-math:7b-q4_K_M
ollama_reasoning_model = deepseek-r1:7b-q4_K_M
ollama_summary_model = llama3.1:8b-q4_K_M
```

---

## 🧪 연결 테스트

### 테스트 스크립트 실행

```bash
python test_ollama.py
```

### 테스트 항목

1. ✓ Ollama 서버 연결 확인
2. ✓ 모든 모델 설치 확인
3. ✓ 각 모델 응답 테스트
4. ✓ 스트리밍 모드 테스트

### 성공 메시지

```
============================================================
✓ ALL TESTS PASSED!
============================================================

Ollama is ready for trading bot usage.

Task-based model mapping:
  • main_analysis     → qwen2.5:14b
  • technical_calc    → qwen2-math:7b
  • pattern_reasoning → deepseek-r1:7b
  • news_summary      → llama3.1:8b
============================================================
```

---

## 🚀 사용 방법

### 1. Ollama 서버 시작

```bash
ollama serve
```

### 2. 트레이딩 봇 실행

```bash
python start.py
```

### 작업별 모델 자동 선택

봇이 자동으로 작업에 맞는 모델을 선택합니다:

| 작업 | 모델 | Temperature |
|------|------|-------------|
| **메인 거래 분석** | Qwen2.5 14B | 0.3 (보수적) |
| **기술 지표 계산** | Qwen2-Math 7B | 0.1 (정밀) |
| **패턴 추론** | DeepSeek-R1 7B | 0.4 (균형) |
| **뉴스 요약** | Llama 3.1 8B | 0.7 (창의적) |

### 수동 모델 선택 (고급)

```python
# Python 코드에서
response = await model_manager.send_prompt(
    prompt="BTC 분석 요청",
    task_type="pattern_reasoning"  # 패턴 추론 모델 사용
)
```

---

## 🔧 문제 해결

### 1. "Ollama connection failed" 오류

**원인**: Ollama 서버가 실행되지 않음

**해결**:
```bash
# 서버 시작
ollama serve

# 다른 터미널에서 테스트
curl http://localhost:11434/api/tags
```

### 2. "Model not found" 오류

**원인**: 모델이 다운로드되지 않음

**해결**:
```bash
# 모델 목록 확인
ollama list

# 모델 다운로드
ollama pull qwen2.5:14b
```

### 3. CUDA/GPU 오류

**원인**: GPU 드라이버 문제

**해결**:
```bash
# NVIDIA GPU 확인
nvidia-smi

# CUDA 버전 확인
nvcc --version

# 드라이버 업데이트
# https://www.nvidia.com/download/index.aspx
```

### 4. 메모리 부족 (VRAM)

**원인**: 모델이 GPU 메모리보다 큼

**해결**:

**옵션 A**: 양자화 모델 사용
```bash
ollama pull qwen2.5:14b-q4_K_M
```

**옵션 B**: 더 작은 모델 사용
```ini
ollama_main_model = llama3.1:8b  # 14B 대신 8B
```

**옵션 C**: CPU 사용 (느림)
```bash
# 환경 변수 설정 (CPU 강제)
set CUDA_VISIBLE_DEVICES=-1  # Windows
export CUDA_VISIBLE_DEVICES=-1  # Linux/macOS
```

### 5. 응답이 너무 느림

**원인**: CPU 모드 또는 모델이 너무 큼

**해결**:

1. GPU 사용 확인
   ```bash
   ollama list  # 실행 중인 모델 확인
   nvidia-smi   # GPU 사용률 확인
   ```

2. 더 작은 모델 사용
   ```ini
   ollama_main_model = llama3.1:8b
   ```

3. 양자화 모델 사용
   ```bash
   ollama pull qwen2.5:14b-q4_K_M
   ```

### 6. "Rate limit" 여전히 발생

**원인**: `config.ini`에서 provider가 여전히 `googleai`로 설정됨

**해결**:
```ini
# config/config.ini
[ai_providers]
provider = ollama  # ← 확인!
```

---

## 📊 성능 비교

### Google AI vs Ollama

| 항목 | Google AI (현재) | Ollama (제안) |
|------|-----------------|---------------|
| **비용** | $0 (제한적) | $0 (무제한) |
| **속도** | 중간 (네트워크 의존) | 빠름 (로컬) |
| **제한** | 20개/일, 4개/분 | 무제한 |
| **프라이버시** | 클라우드 전송 | 완전 로컬 |
| **품질** | 우수 | 우수 (모델 의존) |
| **하드웨어** | 불필요 | GPU 권장 |

### 추천 시나리오

**Ollama 추천**:
- ✅ 하루 20개 이상 분석 필요
- ✅ 프라이버시 중요
- ✅ RTX 3060+ GPU 보유
- ✅ 안정적인 전력 공급

**Google AI 유지**:
- ✅ 하루 10개 미만 분석
- ✅ GPU 없음
- ✅ 간단한 테스트

---

## 🎯 다음 단계

### 1. 최적화

모델 성능을 최적화하려면 `config.ini`에서 조정:

```ini
[model_config]
temperature = 0.3    # 낮을수록 보수적 (0.1-1.0)
top_p = 0.9         # Nucleus sampling (0.5-1.0)
max_tokens = 8192   # 최대 응답 길이
```

### 2. 폴백 시스템

Ollama 실패 시 Google AI로 자동 전환:

```ini
[ai_providers]
provider = all  # 모든 제공자 폴백 활성화
```

폴백 순서: Ollama → Google AI → OpenRouter

### 3. 커스텀 모델

자체 fine-tuned 모델 사용:

```bash
# Modelfile 생성
FROM qwen2.5:14b
PARAMETER temperature 0.3

# 커스텀 모델 빌드
ollama create my-trading-model -f Modelfile

# config.ini에서 사용
ollama_main_model = my-trading-model
```

---

## 📚 추가 자료

- **Ollama 공식 문서**: https://ollama.com/docs
- **모델 라이브러리**: https://ollama.com/library
- **Discord 커뮤니티**: https://discord.gg/ollama
- **GitHub**: https://github.com/ollama/ollama

---

## ❓ FAQ

### Q: 모든 모델을 동시에 실행할 수 있나요?

A: 아니요. Ollama는 한 번에 하나의 모델만 메모리에 로드합니다. 작업별로 자동 전환되며, 전환 시 약 2-5초 소요됩니다.

### Q: 모델을 삭제하려면?

```bash
ollama rm qwen2.5:14b
```

### Q: Ollama 서버를 백그라운드에서 실행하려면?

Windows: 자동으로 백그라운드 실행
Linux/macOS:
```bash
nohup ollama serve > /dev/null 2>&1 &
```

### Q: 다른 포트 사용?

```bash
# 환경 변수 설정
set OLLAMA_HOST=0.0.0.0:8080  # Windows
export OLLAMA_HOST=0.0.0.0:8080  # Linux/macOS

# config.ini 수정
ollama_base_url = http://localhost:8080/v1
```

---

## 🎉 완료!

이제 LLM_Trader가 Ollama로 완전히 전환되었습니다!

**다음 명령어로 시작**:
```bash
python test_ollama.py   # 테스트
python start.py          # 봇 실행
```

**문제가 있나요?** GitHub Issues에 보고해주세요!
