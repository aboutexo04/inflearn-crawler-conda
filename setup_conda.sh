#!/bin/bash
# Conda 환경 설정 스크립트

echo "🎓 인프런 크롤러 Conda 환경 설정"
echo "=================================="

# 현재 디렉토리 확인
if [ ! -f "environment.yml" ]; then
    echo "❌ environment.yml 파일을 찾을 수 없습니다."
    echo "프로젝트 디렉토리에서 실행해주세요."
    exit 1
fi

echo "📦 Conda 환경을 생성합니다..."
conda env create -f environment.yml

if [ $? -eq 0 ]; then
    echo "✅ Conda 환경 생성 완료!"
    echo ""
    echo "다음 명령어로 환경을 활성화하세요:"
    echo "conda activate inflearn-crawler"
    echo ""
    echo "환경 활성화 후 실행 방법:"
    echo "python run_conda.py"
else
    echo "❌ Conda 환경 생성 실패!"
    echo "conda가 설치되어 있는지 확인해주세요."
    exit 1
fi