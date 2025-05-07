import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class ParkingDataFetcher:
    def __init__(self,api_key:str):
        self.api_key =api_key

    def geocode(self,address:str):
        headers={"Authorization":f"{self.api_key}"}

        #addresss search
        r=requests.get(
            "https://dapi.kakao.com/v2/local/search/address.json",
            headers=headers,
            params={"query":address},
            timeout=10,
        )
        print("주소 응답:",r.status_code)
        if r.status_code == 200 and r.json()['documents']:
            doc =r.json()['documents'][0]
            return doc['x'],doc['y']

        #keyword fallback
        r=requests.get(
            "https://dapi.kakao.com/v2/local/search/keyword.json",
            headers=headers,
            params={'query':address},
            timeout=10,
        )
        if r.status_code == 200 and r.json()['documents']:
            doc =r.json()['documents'][0]
            return doc['x'],doc['y']
        raise ValueError('해당 주소/ 키워드를 좌표로 변환할수 없습니다.')

    def fetch_parking(self,x:float,y:float,radius:int):
        url="https://dapi.kakao.com/v2/local/search/keyword.json"
        headers={'Authorization':f"{self.api_key}"}
        params ={
            "query":"주차장",
            "x":x,
            "y":y,
            "radius":radius,
            "sort":"distance",
        }
        r=requests.get(url,headers=headers,params=params)
        r.raise_for_status()
        return r.json().get("documents",[])
    def get_parking_lots(self,x:float,y:float,radius:int):
        url="https://dapi.kakao.com/v2/local/search/category.json"
        headers={'Authorization':self.api_key}
        params ={
            "category_group_code":"PK6",
            "X":x,
            "Y":y,
            "radius":radius,
            "sort":"distance",
        }
        r=requests.get(url,headers=headers,params=params,timeout=10)
        r.raise_for_status()
        return r.json().get("documents",[])
    def scape_parking_fee(self,detail_url: str) -> str:

        options=webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        prefs ={"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)

        try:
            driver=webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), options=options
            )
        except Exception as e:
            return f"크롬 드라이버 초기화 실패 : {e} "

        try:
            driver.get(detail_url)
            time.sleep(2)

            result_parts =[]

            try:
                parking_info=driver.find_element(
                    By.CSS_SELECTOR, "div.cont_parking"
                ).text
                result_parts.append("주차정보:")
                result_parts.append(parking_info)
            except Exception:
                result_parts.append("주차정보를 찾을 수 없습니다.")

            try:
                fee_block =driver.find_element(
                    By.CSS_SELECTOR, "div.cont_ table.tbl_comm"
                ).text
                #deduplicate indentical lines
                uniq=[]
                for ln in fee_block.splitlines():
                    if ln not in quiq:
                        quiq.append(ln)
                result_parts.append("\n현장요금:")
                result_parks.extend(uniq)
            except Exception:
                result_parts.append("\n 요금 정보를 찾을 수 없습니다.")
            return "\n".join(result_parts).strip()
        except Exception as e:
            return f"크롤링 에러: {e}"