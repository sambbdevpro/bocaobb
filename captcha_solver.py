# captcha_solver.py
import requests
import time
from config import CONFIG

class FastCaptchaSolver:
    def __init__(self, service='capsolver'):
        self.service = service
        if service == 'capsolver':
            self.api_key = CONFIG['captcha']['capsolver_key']
            self.submit_url = 'https://api.capsolver.com/createTask'
            self.result_url = 'https://api.capsolver.com/getTaskResult'
        else:
            self.api_key = CONFIG['captcha']['2captcha_key']
            self.submit_url = 'http://2captcha.com/in.php'
            self.result_url = 'http://2captcha.com/res.php'
    
    def solve_recaptcha(self, site_key: str, page_url: str) -> str:
        if self.service == 'capsolver':
            return self._solve_capsolver(site_key, page_url)
        else:
            return self._solve_2captcha(site_key, page_url)
    
    def _solve_capsolver(self, site_key: str, page_url: str) -> str:
        try:
            submit_data = {
                "clientKey": self.api_key,
                "task": {
                    "type": "ReCaptchaV2TaskProxyless",
                    "websiteURL": page_url,
                    "websiteKey": site_key
                }
            }
            
            session = requests.Session()
            session.verify = False
            
            response = session.post(self.submit_url, json=submit_data)
            result = response.json()
            
            if result.get('errorId') == 0:
                task_id = result['taskId']
            else:
                raise Exception(f"CapSolver error: {result}")
            
            for attempt in range(15):
                time.sleep(2)
                
                result_data = {
                    "clientKey": self.api_key,
                    "taskId": task_id
                }
                
                response = session.post(self.result_url, json=result_data)
                result = response.json()
                
                if result.get('status') == 'ready':
                    return result['solution']['gRecaptchaResponse']
                elif result.get('status') == 'processing':
                    continue
                else:
                    raise Exception(f"CapSolver failed: {result}")
            
            raise Exception("CapSolver timeout")
            
        except Exception as e:
            raise Exception(f"CapSolver error: {e}")
    
    def _solve_2captcha(self, site_key: str, page_url: str) -> str:
        try:
            # Submit captcha
            submit_params = {
                'key': self.api_key,
                'method': 'userrecaptcha',
                'googlekey': site_key,
                'pageurl': page_url
            }
            
            response = requests.get(self.submit_url, params=submit_params)
            if response.text.startswith('OK|'):
                captcha_id = response.text.split('|')[1]
            else:
                raise Exception(f"2captcha submit error: {response.text}")
            
            # Wait for result
            for attempt in range(30):
                time.sleep(5)
                
                result_params = {
                    'key': self.api_key,
                    'action': 'get',
                    'id': captcha_id
                }
                
                response = requests.get(self.result_url, params=result_params)
                
                if response.text.startswith('OK|'):
                    return response.text.split('|')[1]
                elif response.text == 'CAPCHA_NOT_READY':
                    continue
                else:
                    raise Exception(f"2captcha result error: {response.text}")
            
            raise Exception("2captcha timeout")
            
        except Exception as e:
            raise Exception(f"2captcha error: {e}")
