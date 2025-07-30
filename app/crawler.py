import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import json


class InfLearnCrawler:
    def __init__(self):
        self.setup_driver()
    
    def setup_driver(self):
        """Chrome 드라이버 설정"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 백그라운드 실행
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
    
    def search_courses(self, keyword, max_results=20):
        """인프런에서 강의 검색"""
        try:
            # 검색 URL 생성
            search_url = f"https://www.inflearn.com/courses?s={keyword}"
            print(f"검색 URL: {search_url}")
            self.driver.get(search_url)
            
            # 페이지 로딩 대기
            time.sleep(5)
            
            # 페이지 소스 일부 출력 (디버깅용)
            print("페이지 제목:", self.driver.title)
            
            # 더 구체적인 강의 카드 셀렉터들
            selectors_to_try = [
                "article[class*='course']",  # 더 구체적으로
                "div[class*='course_card']",
                "div[class*='courseCard']",
                "[data-testid*='course']",
                "div[class*='Course'][class*='Card']",
                ".course-card",
                "article",  # 백업용
            ]
            
            course_cards = []
            for selector in selectors_to_try:
                try:
                    found_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if found_cards:
                        print(f"'{selector}' 셀렉터로 {len(found_cards)}개 요소 발견")
                        # 실제 강의 카드인지 확인하기 위해 텍스트가 있는지 체크
                        valid_cards = []
                        for card in found_cards:
                            text = card.text.strip()
                            if text and len(text) > 10:  # 최소한의 텍스트가 있는 카드만
                                valid_cards.append(card)
                        
                        if valid_cards:
                            print(f"실제 강의 카드: {len(valid_cards)}개")
                            course_cards = valid_cards
                            break
                except Exception as e:
                    continue
            
            if not course_cards:
                # 모든 div 요소 확인 (최후의 수단)
                all_divs = self.driver.find_elements(By.TAG_NAME, "div")
                print(f"전체 div 요소 수: {len(all_divs)}")
                
                # 페이지 HTML 일부 저장 (디버깅용)
                with open("debug_page.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source[:5000])  # 처음 5000자만
                
                return {
                    "error": "강의 카드를 찾을 수 없습니다. 사이트 구조가 변경되었을 수 있습니다.",
                    "keyword": keyword,
                    "courses": []
                }
            
            results = []
            
            for idx, card in enumerate(course_cards[:max_results]):
                try:
                    course_data = self.extract_course_info(card)
                    if course_data and any(course_data.values()):  # 빈 데이터가 아닌 경우만
                        results.append(course_data)
                        print(f"강의 {idx+1}: {course_data}")
                except Exception as e:
                    print(f"Error extracting course {idx}: {str(e)}")
                    continue
            
            return {
                "keyword": keyword,
                "total_results": len(results),
                "courses": results
            }
            
        except Exception as e:
            return {
                "error": f"크롤링 중 오류 발생: {str(e)}",
                "keyword": keyword,
                "courses": []
            }
    
    def extract_course_info(self, card_element):
        """강의 카드에서 정보 추출"""
        course_info = {}
        
        try:
            # 요소의 텍스트와 HTML을 먼저 확인 (디버깅)
            element_text = card_element.text.strip()
            print(f"카드 요소 텍스트: {element_text[:100]}...")
            
            # 더 광범위한 제목 추출 시도
            title_selectors = [
                "h1", "h2", "h3", "h4", "h5", "h6",
                "[class*='title']", "[class*='Title']",
                "[class*='name']", "[class*='Name']",
                "[class*='course']", "[class*='Course']",
                "div[class*='title']", "span[class*='title']",
                "p[class*='title']", "a[class*='title']",
                ".title", ".course-title", ".course-name"
            ]
            
            title = self.find_text_by_selectors(card_element, title_selectors)
            if not title and element_text:
                # 요소 텍스트에서 첫 번째 줄을 제목으로 사용
                lines = element_text.split('\n')
                if lines:
                    title = lines[0].strip()
            
            if title:
                course_info['title'] = title.strip()
                print(f"추출된 제목: {title}")
            
            # 강사명 추출
            instructor_selectors = [
                "[class*='instructor']", "[class*='Instructor']",
                "[class*='teacher']", "[class*='Teacher']",
                "[class*='author']", "[class*='Author']",
                "[class*='name']", "[class*='Name']",
                "p[class*='instructor']", "span[class*='instructor']",
                "div[class*='instructor']", ".instructor"
            ]
            
            instructor = self.find_text_by_selectors(card_element, instructor_selectors)
            if not instructor and element_text:
                # 텍스트에서 강사명 패턴 찾기
                lines = element_text.split('\n')
                for line in lines[1:]:  # 첫 번째 줄(제목) 제외
                    if line.strip() and len(line.strip()) < 50:  # 너무 긴 텍스트 제외
                        instructor = line.strip()
                        break
            
            if instructor:
                course_info['instructor'] = instructor.strip()
                print(f"추출된 강사: {instructor}")
            
            # 가격 추출
            price_selectors = [
                "[class*='price']", "[class*='Price']",
                "[class*='cost']", "[class*='Cost']",
                "[class*='won']", "[class*='Won']",
                "span[class*='price']", "div[class*='price']"
            ]
            
            price = self.find_text_by_selectors(card_element, price_selectors)
            if not price and element_text:
                # 텍스트에서 가격 패턴 찾기 (원, $, ₩ 포함)
                import re
                price_pattern = r'[₩$]\s*[\d,]+|[\d,]+\s*원'
                matches = re.findall(price_pattern, element_text)
                if matches:
                    price = matches[0]
            
            if price:
                course_info['price'] = price.strip()
                print(f"추출된 가격: {price}")
            
            # 평점 추출
            rating_selectors = [
                "[class*='rating']", "[class*='Rating']",
                "[class*='star']", "[class*='Star']",
                "[class*='score']", "[class*='Score']"
            ]
            
            rating = self.find_text_by_selectors(card_element, rating_selectors)
            if rating:
                course_info['rating'] = rating.strip()
                print(f"추출된 평점: {rating}")
            
            # 링크 추출
            try:
                link_element = card_element.find_element(By.TAG_NAME, "a")
                href = link_element.get_attribute("href")
                if href:
                    if href.startswith("/"):
                        href = "https://www.inflearn.com" + href
                    course_info['url'] = href
                    print(f"추출된 링크: {href}")
            except:
                pass
            
            # 이미지 URL 추출
            try:
                img_element = card_element.find_element(By.TAG_NAME, "img")
                img_src = img_element.get_attribute("src")
                if img_src:
                    course_info['image_url'] = img_src
                    print(f"추출된 이미지: {img_src}")
            except:
                pass
            
            # 강의 카드인지 더 엄격하게 검증
            if course_info.get('title') and len(course_info.get('title', '')) > 5:
                return course_info
            elif element_text and len(element_text) > 20:
                # 텍스트에서 강의 제목처럼 보이는 부분 찾기
                lines = element_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if len(line) > 10 and '강의' in line or '입문' in line or '기초' in line or '실습' in line:
                        course_info['title'] = line
                        return course_info
                # 첫 번째 긴 줄을 제목으로 사용
                for line in lines:
                    line = line.strip()
                    if len(line) > 15:
                        course_info['title'] = line
                        return course_info
            
            return None
            
        except Exception as e:
            print(f"Error in extract_course_info: {str(e)}")
            return None
    
    def find_text_by_selectors(self, parent_element, selectors):
        """여러 셀렉터로 텍스트 찾기"""
        for selector in selectors:
            try:
                element = parent_element.find_element(By.CSS_SELECTOR, selector)
                text = element.text.strip()
                if text:
                    return text
            except:
                continue
        return None
    
    def close(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()


def search_inflearn_courses(keyword, max_results=20):
    """인프런 강의 검색 함수"""
    crawler = InfLearnCrawler()
    
    try:
        results = crawler.search_courses(keyword, max_results)
        return results
    finally:
        crawler.close()


if __name__ == "__main__":
    # 테스트
    keyword = "파이썬"
    results = search_inflearn_courses(keyword, 10)
    print(json.dumps(results, ensure_ascii=False, indent=2))
