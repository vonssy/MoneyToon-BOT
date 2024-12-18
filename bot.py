import requests
import json
import os
import urllib.parse
from colorama import *
from datetime import datetime, timedelta
import time
import pytz

wib = pytz.timezone('Asia/Jakarta')

class MoneyToon:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
            'Host': 'mt.promptale.io',
            'Origin': 'https://mt.promptale.io',
            'Pragma': 'no-cache',
            'Referer': 'https://mt.promptale.io/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'
        }

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Claim {Fore.BLUE + Style.BRIGHT}Money Toon - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_data(self, query: str) -> dict:
        parsed_query = urllib.parse.parse_qs(query)
        user_data = json.loads(parsed_query['user'][0])
        first_name = user_data.get("first_name", "")    
        data = {
            "authDate": parsed_query["auth_date"][0],
            "chatInstance": parsed_query.get("chat_instance", [None])[0],
            "chatType": parsed_query.get("chat_type", [None])[0],
            "hash": parsed_query["hash"][0],
            "queryId": parsed_query.get("query_id", [None])[0],
            "startParam": "2B860D",
            "user": {
                "allowsWriteToPm": user_data.get("allows_write_to_pm", [None]),
                "firstName": first_name,
                "id": user_data["id"],
                "languageCode": user_data.get("language_code", ""),
                "lastName": user_data.get("last_name", ""),
                "photoUrl": user_data.get("photo_url", ""),
                "username": user_data.get("username", ""),
            }
        }
        return {"data":data, "first_name":first_name}

    def load_tokens(self):
        try:
            if not os.path.exists('tokens.json'):
                return {"accounts": []}

            with open('tokens.json', 'r') as file:
                data = json.load(file)
                if "accounts" not in data:
                    return {"accounts": []}
                return data
        except json.JSONDecodeError:
            return {"accounts": []}

    def save_tokens(self, tokens):
        with open('tokens.json', 'w') as file:
            json.dump(tokens, file, indent=4)

    def generate_tokens(self, queries: list):
        tokens_data = self.load_tokens()
        accounts = tokens_data["accounts"]

        for idx, query in enumerate(queries):
            account_name = self.load_data(query)["first_name"]

            existing_account = next((acc for acc in accounts if acc["first_name"] == account_name), None)

            if not existing_account:
                print(
                    f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}Token Is None{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} ] [{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} Generating Token... {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}",
                    end="\r", flush=True
                )
                time.sleep(1)

                token = self.user_login(query)
                if token:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}] [{Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT} Successfully Generated Token {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}                           "
                    )
                    accounts.insert(idx, {"first_name": account_name, "token": token})
                else:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT}Query Isn't Valid{Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT} ] [{Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT} Failed to Generate Token {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}                           "
                    )

                time.sleep(1)
                self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}" * 75)

        self.save_tokens({"accounts": accounts})

    def renew_token(self, account_name):
        tokens_data = self.load_tokens()
        accounts = tokens_data.get("accounts", [])
        
        account = next((acc for acc in accounts if acc["first_name"] == account_name), None)
        
        if account and "token" in account:
            token = account["token"]
            if not self.user_points(token):
                print(
                    f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT}Token Isn't Valid{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} ] [{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} Regenerating Token... {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}",
                    end="\r", flush=True
                )
                time.sleep(1)
                
                accounts = [acc for acc in accounts if acc["first_name"] != account_name]
                
                query = next((query for query in self.load_queries() if self.load_data(query)["first_name"] == account_name), None)
                if query:
                    new_token = self.user_login(query)
                    if new_token:
                        accounts.append({"first_name": account_name, "token": new_token})
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT}Query Is Valid{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} ] [{Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT} Successfully Generated Token {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}                           "
                        )
                    else:
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                            f"{Fore.YELLOW + Style.BRIGHT}Query Isn't Valid{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} ] [{Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT} Failed to Generate Token {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}                           "
                        )
                else:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}] [{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Query Is None. Skipping {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}                           "
                    )

                time.sleep(1)
        
        self.save_tokens({"accounts": accounts})

    def load_queries(self):
        with open('query.txt', 'r') as file:
            return [line.strip() for line in file if line.strip()]

    def user_login(self, query: str, retries=5):
        url = 'https://mt.promptale.io/auth/loginTg'
        data = json.dumps({"initData":query, "initDataUnsafe":self.load_data(query)["data"]})
        self.headers.update({
            'Content-Type': 'application/json'
        })

        for attempt in range(retries):
            try:
                response = self.session.post(url, headers=self.headers, data=data, timeout=20)
                response.raise_for_status()
                return response.json()["data"]["accessToken"]
            except (requests.RequestException, requests.Timeout, ValueError) as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT}HTTP ERROR.{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} Retrying {attempt+1}/{retries} {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None
                
    def user_points(self, token: str, retries=5):
        url = 'https://mt.promptale.io/main/mypoint'
        self.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

        for attempt in range(retries):
            try:
                response = self.session.get(url, headers=self.headers, timeout=20)
                if response.status_code == 401:
                      return None

                response.raise_for_status()
                return response.json()["data"]
            except (requests.RequestException, requests.Timeout, ValueError) as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT}HTTP ERROR.{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} Retrying {attempt+1}/{retries} {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None
                
    def user_attendance(self, token: str, retries=5):
        url = 'https://mt.promptale.io/tasks/isAttendanceToday'
        self.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

        for attempt in range(retries):
            try:
                response = self.session.get(url, headers=self.headers, timeout=20)
                response.raise_for_status()
                return response.json()["data"]
            except (requests.RequestException, requests.Timeout, ValueError) as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT}HTTP ERROR.{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} Retrying {attempt+1}/{retries} {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None
                
    def claim_attendance(self, token: str, retries=5):
        url = 'https://mt.promptale.io/tasks/attend'
        self.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

        for attempt in range(retries):
            try:
                response = self.session.post(url, headers=self.headers, timeout=20)
                response.raise_for_status()
                return response.json()["data"]
            except (requests.RequestException, requests.Timeout, ValueError) as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT}HTTP ERROR.{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} Retrying {attempt+1}/{retries} {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None
                  
    def get_notif(self, token: str, code: str, retries=5):
        url = f'https://mt.promptale.io/main/pointNoti?getFromCode={code}'
        self.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

        for attempt in range(retries):
            try:
                response = self.session.get(url, headers=self.headers, timeout=20)
                response.raise_for_status()
                return response.json()["data"]
            except (requests.RequestException, requests.Timeout, ValueError) as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT}HTTP ERROR.{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} Retrying {attempt+1}/{retries} {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None
                  
    def read_notif(self, token: str, code: str, idx: int, retries=5):
        url = 'https://mt.promptale.io/main/pointNotiOk'
        data = json.dumps({"getFromCode":code, "pointIdx":idx})
        self.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

        for attempt in range(retries):
            try:
                response = self.session.post(url, headers=self.headers, data=data, timeout=20)
                response.raise_for_status()
                return response.json()["data"]
            except (requests.RequestException, requests.Timeout, ValueError) as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT}HTTP ERROR.{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} Retrying {attempt+1}/{retries} {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None

    def game_status(self, token: str, game_id: list, retries=5):
        url = f'https://mt.promptale.io/games/status?gameCode={game_id}'
        self.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

        for attempt in range(retries):
            try:
                response = self.session.get(url, headers=self.headers, timeout=20)
                response.raise_for_status()
                return response.json()["data"]
            except (requests.RequestException, requests.Timeout, ValueError) as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT}HTTP ERROR.{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} Retrying {attempt+1}/{retries} {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None
                
    def game_run(self, token: str, game_id: list, level: str, retries=5):
        url = 'https://mt.promptale.io/games/gameRun'
        data = json.dumps({"gameId":game_id, "level":level, "logStatus":"S"})
        self.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

        for attempt in range(retries):
            try:
                response = self.session.post(url, headers=self.headers, data=data, timeout=20)
                response.raise_for_status()
                result = response.json()
                if result and result['success']:
                    return result["data"]
                else:
                    return None
            except (requests.RequestException, requests.Timeout, ValueError) as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT}HTTP ERROR.{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} Retrying {attempt+1}/{retries} {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None
                
    def game_complete(self, token: str, game_id: list, level: str, runIdx: int, retries=5):
        url = 'https://mt.promptale.io/games/gameComplete'
        data = json.dumps({"gameId":game_id, "level":level, "runIdx":str(runIdx)})
        self.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

        for attempt in range(retries):
            try:
                response = self.session.post(url, headers=self.headers, data=data, timeout=20)
                response.raise_for_status()
                result = response.json()
                if result and result['success']:
                    return result["data"]
                else:
                    return None
            except (requests.RequestException, requests.Timeout, ValueError) as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT}HTTP ERROR.{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} Retrying {attempt+1}/{retries} {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None
                
    def tasks_list(self, token: str, retries=5):
        url = 'https://mt.promptale.io/tasks'
        self.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

        for attempt in range(retries):
            try:
                response = self.session.get(url, headers=self.headers, timeout=20)
                response.raise_for_status()
                return response.json()["data"]
            except (requests.RequestException, requests.Timeout, ValueError) as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT}HTTP ERROR.{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} Retrying {attempt+1}/{retries} {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None
                
    def start_tasks(self, token: str, task_id: int, retries=5):
        url = 'https://mt.promptale.io/tasks/taskRun'
        data = json.dumps({"taskIdx":task_id})
        self.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

        for attempt in range(retries):
            try:
                response = self.session.post(url, headers=self.headers, data=data, timeout=20)
                response.raise_for_status()
                return response.json()["data"]
            except (requests.RequestException, requests.Timeout, ValueError) as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT}HTTP ERROR.{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} Retrying {attempt+1}/{retries} {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None
                
    def claim_tasks(self, token: str, task_id: int, retries=5):
        url = 'https://mt.promptale.io/tasks/taskComplete'
        data = json.dumps({"taskIdx":task_id})
        self.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

        for attempt in range(retries):
            try:
                response = self.session.post(url, headers=self.headers, data=data, timeout=20)
                response.raise_for_status()
                return response.json()["data"]
            except (requests.RequestException, requests.Timeout, ValueError) as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT}HTTP ERROR.{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} Retrying {attempt+1}/{retries} {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None
                
    def sl_pass_list(self, token: str, retries=5):
        url = 'https://mt.promptale.io/rewards/mySlPassList'
        self.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

        for attempt in range(retries):
            try:
                response = self.session.get(url, headers=self.headers, timeout=20)
                response.raise_for_status()
                return response.json()["data"]
            except (requests.RequestException, requests.Timeout, ValueError) as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT}HTTP ERROR.{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} Retrying {attempt+1}/{retries} {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None
                
    def claim_sl_pass(self, token: str, sl_pass_id: str, retries=5):
        url = 'https://mt.promptale.io/rewards/slPassClaim'
        data = json.dumps({"slPassId":sl_pass_id})
        self.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

        for attempt in range(retries):
            try:
                response = self.session.post(url, headers=self.headers, data=data, timeout=20)
                if response.status_code == 500:
                    return None
                
                response.raise_for_status()
                return response.json()["data"]
            except (requests.RequestException, requests.Timeout, ValueError) as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT}HTTP ERROR.{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} Retrying {attempt+1}/{retries} {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None
                
    def egg_count(self, token: str, retries=5):
        url = 'https://mt.promptale.io/rewards/myEggCount'
        self.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

        for attempt in range(retries):
            try:
                response = self.session.get(url, headers=self.headers, timeout=20)
                response.raise_for_status()
                return response.json()["data"]
            except (requests.RequestException, requests.Timeout, ValueError) as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT}HTTP ERROR.{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} Retrying {attempt+1}/{retries} {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None
                
    def egg_open(self, token: str, retries=5):
        url = 'https://mt.promptale.io/rewards/myEggOpen'
        self.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

        for attempt in range(retries):
            try:
                response = self.session.post(url, headers=self.headers, timeout=20)
                response.raise_for_status()
                return response.json()["data"]
            except (requests.RequestException, requests.Timeout, ValueError) as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT}HTTP ERROR.{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} Retrying {attempt+1}/{retries} {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    time.sleep(2)
                else:
                    return None
        
    def process_query(self, query: str):
        account_name = self.load_data(query)["first_name"]
        tokens_data = self.load_tokens()
        accounts = tokens_data.get("accounts", [])
        exist_account = next((acc for acc in accounts if acc["first_name"] == account_name), None)
        if not exist_account:
            self.log(
                f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT}Token Not Found in tokens.json{Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
            )
            return
        
        if exist_account and "token" in exist_account:
            token = exist_account["token"]

            balance = self.user_points(token)
            if not balance:
                self.renew_token(account_name)
                tokens_data = self.load_tokens()
                new_account = next((acc for acc in tokens_data["accounts"] if acc["first_name"] == account_name), None)
                
                if new_account and "token" in new_account:
                    new_token = new_account["token"] 
                    balance = self.user_points(new_token)

            if balance:
                self.log(
                    f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {account_name} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}] [ Balance{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {balance['point']} $OWP {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}] [ egg{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {balance['egg']} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                )
                time.sleep(1)

                check_in = self.user_attendance(new_token if 'new_token' in locals() else token)
                if not check_in:
                    claim = self.claim_attendance(new_token if 'new_token' in locals() else token)
                    if claim:
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}[ Check-In{Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT} Is Claimed {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}] [ Reward{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {claim['point']} $OWP {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                    else:
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}[ Check-In{Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT} Isn't Claimed {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                else:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Check-In{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Is Already Claimed {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
                time.sleep(1)

                for code in ["Referral", "Rank"]:
                    notif = self.get_notif(new_token if 'new_token' in locals() else token, code)
                    if notif:
                        completed = False
                        for item in notif:
                            idx = item['pointIdx']
                            reward = item.get('getPoint', 0)

                            if item:
                                read = self.read_notif(new_token if 'new_token' in locals() else token, code, idx)
                                if read:
                                    self.log(
                                        f"{Fore.MAGENTA + Style.BRIGHT}[ Notif{Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT} {code} {Style.RESET_ALL}"
                                        f"{Fore.GREEN + Style.BRIGHT}Is Claimed{Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT} ] [ Reward{Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT} {reward} {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                                    )
                                else:
                                    self.log(
                                        f"{Fore.MAGENTA + Style.BRIGHT}[ Notif{Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT} {code} {Style.RESET_ALL}"
                                        f"{Fore.RED + Style.BRIGHT}Isn't Claimed{Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
                                    )
                                time.sleep(1)

                            else:
                                completed = True

                        if completed:
                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}[ Notif{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {code} {Style.RESET_ALL}"
                                f"{Fore.GREEN + Style.BRIGHT}Is Completed{Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
                            )
                    else:
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}[ Notif{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {code} {Style.RESET_ALL}"
                            f"{Fore.YELLOW + Style.BRIGHT}No Available Message{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
                        )
                    time.sleep(1)

                for game_id in ["MahJong", "Matching", "Sliding"]:
                    games = self.game_status(new_token if 'new_token' in locals() else token, game_id)
                    if games:
                        completed = False
                        for game in games:
                            level = game['level']
                            count = game['times']
                            max_count = game['dailyTimes']

                            if game:
                                if count < max_count:
                                    while count < max_count:
                                        runIdx = self.game_run(new_token if 'new_token' in locals() else token, game_id, level)
                                        if runIdx:
                                            count += 1
                                            self.log(
                                                f"{Fore.MAGENTA + Style.BRIGHT}[ Game{Style.RESET_ALL}"
                                                f"{Fore.WHITE + Style.BRIGHT} {game['gameName']} {Style.RESET_ALL}"
                                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                                f"{Fore.WHITE + Style.BRIGHT} Level {level} {Style.RESET_ALL}"
                                                f"{Fore.GREEN + Style.BRIGHT}Is Started{Style.RESET_ALL}"
                                                f"{Fore.MAGENTA + Style.BRIGHT} ] [ ID{Style.RESET_ALL}"
                                                f"{Fore.WHITE + Style.BRIGHT} {runIdx} {Style.RESET_ALL}"
                                                f"{Fore.MAGENTA + Style.BRIGHT}] [ Chance{Style.RESET_ALL}"
                                                f"{Fore.WHITE + Style.BRIGHT} {count}/{max_count} {Style.RESET_ALL}"
                                                f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                                            )
                                            time.sleep(1)

                                            complete = self.game_complete(new_token if 'new_token' in locals() else token, game_id, level, runIdx)
                                            if complete:
                                                self.log(
                                                    f"{Fore.MAGENTA + Style.BRIGHT}[ Game{Style.RESET_ALL}"
                                                    f"{Fore.WHITE + Style.BRIGHT} {game['gameName']} {Style.RESET_ALL}"
                                                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                                    f"{Fore.WHITE + Style.BRIGHT} Level {level} {Style.RESET_ALL}"
                                                    f"{Fore.GREEN + Style.BRIGHT}Is Completed{Style.RESET_ALL}"
                                                    f"{Fore.MAGENTA + Style.BRIGHT} ] [ Reward{Style.RESET_ALL}"
                                                    f"{Fore.WHITE + Style.BRIGHT} {complete['point']} $OWP {Style.RESET_ALL}"
                                                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                                    f"{Fore.WHITE + Style.BRIGHT} {complete['egg']} Egg {Style.RESET_ALL}"
                                                    f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                                                )
                                            else:
                                                self.log(
                                                    f"{Fore.MAGENTA + Style.BRIGHT}[ Game{Style.RESET_ALL}"
                                                    f"{Fore.WHITE + Style.BRIGHT} {game['gameName']} {Style.RESET_ALL}"
                                                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                                    f"{Fore.WHITE + Style.BRIGHT} Level {level} {Style.RESET_ALL}"
                                                    f"{Fore.YELLOW + Style.BRIGHT}Not Eligible to Complete{Style.RESET_ALL}"
                                                    f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
                                                )
                                                break
                                            time.sleep(1)

                                        else:
                                            self.log(
                                                f"{Fore.MAGENTA + Style.BRIGHT}[ Game{Style.RESET_ALL}"
                                                f"{Fore.WHITE + Style.BRIGHT} {game['gameName']} {Style.RESET_ALL}"
                                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                                f"{Fore.WHITE + Style.BRIGHT} Level {level} {Style.RESET_ALL}"
                                                f"{Fore.YELLOW + Style.BRIGHT}Not Eligible to Start{Style.RESET_ALL}"
                                                f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
                                            )
                                            break

                                        time.sleep(1)

                                    if count == max_count:
                                        self.log(
                                            f"{Fore.MAGENTA + Style.BRIGHT}[ Game{Style.RESET_ALL}"
                                            f"{Fore.WHITE + Style.BRIGHT} {game['gameName']} {Style.RESET_ALL}"
                                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                            f"{Fore.WHITE + Style.BRIGHT} Level {level} {Style.RESET_ALL}"
                                            f"{Fore.YELLOW + Style.BRIGHT}No Available Chance{Style.RESET_ALL}"
                                            f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
                                        )

                                else:
                                    self.log(
                                        f"{Fore.MAGENTA + Style.BRIGHT}[ Game{Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT} {game['gameName']} {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT} Level {level} {Style.RESET_ALL}"
                                        f"{Fore.YELLOW + Style.BRIGHT}No Available Chance{Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
                                    )

                            else:
                                completed = True

                        if completed:
                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}[ Game{Style.RESET_ALL}"
                                f"{Fore.GREEN + Style.BRIGHT} Is Completed {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                            )

                    else:
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}[ Game{Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT} Data Is None {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                    time.sleep(1)

                tasks = self.tasks_list(new_token if 'new_token' in locals() else token)
                if tasks:
                    completed_task = False
                    for task in tasks:
                        task_id = task['taskIdx']
                        status = task['runStatus']
                        completed = task['completeCount']

                        if task and status is None:
                            start = self.start_tasks(new_token if 'new_token' in locals() else token, task_id)
                            if start:
                                self.log(
                                    f"{Fore.MAGENTA + Style.BRIGHT}[ Task{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} {task['taskMainTitle']} {Style.RESET_ALL}"
                                    f"{Fore.GREEN + Style.BRIGHT}Is Started{Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
                                )
                                time.sleep(1)

                                claim = self.claim_tasks(new_token if 'new_token' in locals() else token, task_id)
                                if claim:
                                    self.log(
                                        f"{Fore.MAGENTA + Style.BRIGHT}[ Task{Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT} {task['taskMainTitle']} {Style.RESET_ALL}"
                                        f"{Fore.GREEN + Style.BRIGHT}Is Claimed{Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT} ] [ Reward{Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT} {claim['point']} $OWP {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT} {claim['egg']} Egg {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                                    )
                                else:
                                    self.log(
                                        f"{Fore.MAGENTA + Style.BRIGHT}[ Task{Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT} {task['taskMainTitle']} {Style.RESET_ALL}"
                                        f"{Fore.RED + Style.BRIGHT}Isn't Claimed{Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
                                    )
                            else:
                                self.log(
                                    f"{Fore.MAGENTA + Style.BRIGHT}[ Task{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} {task['taskMainTitle']} {Style.RESET_ALL}"
                                    f"{Fore.RED + Style.BRIGHT}Isn't Started{Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
                                )
                            time.sleep(1)

                        elif task and status == "S" and completed == 0:
                            claim = self.claim_tasks(new_token if 'new_token' in locals() else token, task_id)
                            if claim:
                                self.log(
                                    f"{Fore.MAGENTA + Style.BRIGHT}[ Task{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} {task['taskMainTitle']} {Style.RESET_ALL}"
                                    f"{Fore.GREEN + Style.BRIGHT}Is Claimed{Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT} ] [ Reward{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} {claim['point']} $OWP {Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} {claim['egg']} Egg {Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                                )
                            else:
                                self.log(
                                    f"{Fore.MAGENTA + Style.BRIGHT}[ Task{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} {task['taskMainTitle']} {Style.RESET_ALL}"
                                    f"{Fore.RED + Style.BRIGHT}Isn't Claimed{Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
                                )
                            time.sleep(1)

                        else:
                            completed_task = True

                    if completed_task:
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}[ Task{Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT} Is Completed {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                        )

                else:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Task{Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT} Data Is None {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
                time.sleep(1)
                            
                pass_list = self.sl_pass_list(new_token if 'new_token' in locals() else token)
                if pass_list:
                    completed = False
                    free_sl_pass = [sl_pass for sl_pass in pass_list if sl_pass["slPassId"].startswith("free")]
                    for sl_pass in free_sl_pass:
                        sl_pass_id = sl_pass["slPassId"]

                        owp_reward = 0
                        egg_reward = 0
                        for reward in sl_pass.get("getItems", []):
                            if reward["item"] == "OWP":
                                owp_reward = reward["count"]
                            elif reward["item"] == "Egg":
                                egg_reward = reward["count"]

                        claimed = sl_pass["isClaim"]

                        if not claimed:
                            claim = self.claim_sl_pass(new_token if 'new_token' in locals() else token, sl_pass_id)
                            if claim:
                                self.log(
                                    f"{Fore.MAGENTA + Style.BRIGHT}[ SL Pass{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} Level {sl_pass['step']} {Style.RESET_ALL}"
                                    f"{Fore.GREEN + Style.BRIGHT}Is Claimed{Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT} ] [ Reward{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} {owp_reward} $OWP {Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} {egg_reward} Egg {Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
                                )
                            else:
                                self.log(
                                    f"{Fore.MAGENTA + Style.BRIGHT}[ SL Pass{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} {sl_pass['step']} {Style.RESET_ALL}"
                                    f"{Fore.YELLOW + Style.BRIGHT}Not Eligible to Claim{Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
                                )
                                break
                            time.sleep(1)

                        else:
                            completed = True

                    if completed:
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}[ SL Pass{Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT} Is Completed {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                        )

                else:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ SL Pass{Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT} Data Is None {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
                time.sleep(1)

                egg = self.egg_count(new_token if 'new_token' in locals() else token)
                if egg is not None and egg > 0:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Egg{Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT} Is Prepared to Open {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}] [ Count{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {egg} Egg {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
                    time.sleep(1)

                    while egg > 0:
                        open = self.egg_open(new_token if 'new_token' in locals() else token)
                        if open:
                            egg -= 1
                            reward = open.get('getPoint', 0)
                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}[ Egg{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {open['codeName']} {Style.RESET_ALL}"
                                f"{Fore.GREEN + Style.BRIGHT}Is Opened{Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT} ] [ Reward{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {reward} $OWP {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}] [ Count{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {egg} Left {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                            )
                        else:
                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}[ Egg{Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} Isn't Opened {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                            )
                            break

                        time.sleep(1)

                    if egg == 0:
                        self.log(
                            f"{Fore.MAGENTA + Style.BRIGHT}[ Egg{Style.RESET_ALL}"
                            f"{Fore.YELLOW + Style.BRIGHT} No Available Left {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                        )

                else:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Egg{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} No Available Left {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
                time.sleep(1)


    def main(self):
        self.clear_terminal()
        try:
            queries = self.load_queries()
            self.generate_tokens(queries)

            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(queries)}{Style.RESET_ALL}"
                )
                self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

                for query in queries:
                    if query:
                        self.process_query(query)
                        self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)
                        time.sleep(3)

                seconds = 1800
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}",
                        end="\r"
                    )
                    time.sleep(1)
                    seconds -= 1

        except KeyboardInterrupt:
            self.log(f"{Fore.RED + Style.BRIGHT}[ EXIT ] Money Toon - BOT{Style.RESET_ALL}")
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}An error occurred: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    bot = MoneyToon()
    bot.main()