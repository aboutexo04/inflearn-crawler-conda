#!/usr/bin/env python3
"""
Conda 환경 전용 실행 스크립트
"""

import os
import sys
import subprocess
from pathlib import Path

def check_conda_env():
    """conda 환경이 활성화되어 있는지 확인"""
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    if conda_env != 'inflearn-crawler':
        print("❌ conda 환경이 활성화되지 않았습니다!")
        print("다음 명령어로 환경을 활성화하세요:")
        print("conda activate inflearn-crawler")
        return False
    return True

def run_simple_server():
    """간단한 HTTP 서버 실행"""
    print("🚀 간단한 HTTP 서버를 시작합니다...")
    print("브라우저에서 http://localhost:9000 으로 접속하세요")
    print("종료하려면 Ctrl+C를 눌러주세요")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "simple_server.py"])
    except KeyboardInterrupt:
        print("\n서버를 종료합니다.")

def run_fastapi_server():
    """FastAPI 서버 실행"""
    print("🚀 FastAPI 서버를 시작합니다...")
    print("브라우저에서 http://localhost:8001 으로 접속하세요")
    print("종료하려면 Ctrl+C를 눌러주세요")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "-m", "app.main"])
    except KeyboardInterrupt:
        print("\n서버를 종료합니다.")

def run_uvicorn_server():
    """uvicorn으로 서버 실행"""
    print("🚀 Uvicorn 서버를 시작합니다...")
    print("브라우저에서 http://localhost:8080 으로 접속하세요")
    print("종료하려면 Ctrl+C를 눌러주세요")
    print("-" * 50)
    
    try:
        subprocess.run(["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8080", "--reload"])
    except KeyboardInterrupt:
        print("\n서버를 종료합니다.")

def test_crawler():
    """크롤러 테스트"""
    print("🧪 크롤러를 테스트합니다...")
    print("-" * 50)
    
    try:
        from app.crawler import search_inflearn_courses
        result = search_inflearn_courses("파이썬", 3)
        
        print(f"✅ 테스트 성공!")
        print(f"키워드: {result['keyword']}")
        print(f"결과 수: {result['total_results']}")
        
        for i, course in enumerate(result['courses'], 1):
            print(f"\n{i}. {course.get('title', '제목 없음')}")
            print(f"   강사: {course.get('instructor', '정보 없음')}")
            print(f"   가격: {course.get('price', '정보 없음')}")
            
    except Exception as e:
        print(f"❌ 테스트 실패: {str(e)}")

def main():
    print("🎓 인프런 강의 검색 크롤러 (Conda 버전)")
    print("=" * 50)
    
    # conda 환경 확인
    if not check_conda_env():
        return
    
    print("✅ conda 환경 'inflearn-crawler' 활성화됨")
    print()
    
    while True:
        print("실행할 옵션을 선택하세요:")
        print("1. 간단한 HTTP 서버 실행 (권장)")
        print("2. FastAPI 서버 실행")  
        print("3. Uvicorn 서버 실행")
        print("4. 크롤러 테스트")
        print("5. 종료")
        
        choice = input("\n선택 (1-5): ").strip()
        
        if choice == "1":
            run_simple_server()
        elif choice == "2":
            run_fastapi_server()
        elif choice == "3":
            run_uvicorn_server()
        elif choice == "4":
            test_crawler()
            input("\n계속하려면 Enter를 눌러주세요...")
        elif choice == "5":
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 선택입니다. 1-5 중에서 선택해주세요.")
        
        print()

if __name__ == "__main__":
    main()