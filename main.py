import requests
import json
import os
import time
import random
from datetime import datetime


# ================= CONFIG =================

COOKIES_FILE = "cookies.json"
COUPON_FILE = "coupons.txt"

URL = "https://www.sheinindia.in/api/cart/apply-voucher"

OUTPUT = "coupanlelo.txt"

DELAY_MIN = 12
DELAY_MAX = 12

CYCLE_DELAY = 60

TIMEOUT = 15
RETRIES = 2


# ================= GLOBAL COUNTERS =================

TOTAL_CHECKED = 0
VALID_COUNT = 0
INVALID_COUNT = 0
ERROR_COUNT = 0


# ================= LOAD COOKIES =================

def load_cookies():

    with open(COOKIES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):

        return "; ".join(
            f"{c['name']}={c['value']}"
            for c in data
        )

    if isinstance(data, dict):

        return "; ".join(
            f"{k}={v}"
            for k, v in data.items()
        )


# ================= LOAD COUPONS =================

def load_coupons():

    with open(COUPON_FILE) as f:
        return [x.strip() for x in f if x.strip()]


# ================= HEADERS =================

def get_headers(cookie):

    return {
        "accept": "application/json",
        "content-type": "application/json",
        "origin": "https://www.sheinindia.in",
        "referer": "https://www.sheinindia.in/cart",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "x-tenant-id": "SHEIN",
        "cookie": cookie
    }


# ================= SAVE =================

def save_valid(code, data):

    dis = data.get("voucherDiscountValue", "NA")

    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(OUTPUT, "a", encoding="utf-8") as f:
        f.write(f"[{t}] {code} | {dis}\n")


# ================= CHECK COUPON =================

def check_coupon(code, head):

    global TOTAL_CHECKED, VALID_COUNT, INVALID_COUNT, ERROR_COUNT

    TOTAL_CHECKED += 1

    payload = {
        "voucherId": code,
        "device": {"client_type": "web"}
    }

    for attempt in range(1, RETRIES + 1):

        try:

            r = requests.post(
                URL,
                json=payload,
                headers=head,
                timeout=TIMEOUT
            )

            print("Status:", r.status_code)

            # Block
            if r.status_code == 403:

                print("⛔ BLOCKED! Stop program")
                exit()

            # Non JSON
            if "application/json" not in r.headers.get("Content-Type", ""):

                print("🚫 Non-JSON / Blocked")
                ERROR_COUNT += 1
                return

            data = r.json()

            # Invalid
            if "errorMessage" in data:

                print("❌ Invalid:", code)
                INVALID_COUNT += 1

            # Valid
            else:

                print("✅ VALID:", code)

                VALID_COUNT += 1

                save_valid(code, data)

            return


        except requests.exceptions.ReadTimeout:

            print(f"⏱ Timeout (Try {attempt}/{RETRIES})")

            time.sleep(random.randint(10, 20))


        except requests.exceptions.RequestException as e:

            print("⚠️ Network error:", e)

            time.sleep(random.randint(10, 20))


    print("❌ Failed after retries:", code)

    ERROR_COUNT += 1


# ================= MAIN LOOP =================

def main():

    global TOTAL_CHECKED, VALID_COUNT, INVALID_COUNT, ERROR_COUNT

    print("🔐 Loading cookies...")

    cookie = load_cookies()

    head = get_headers(cookie)

    print("✅ Ready\n")


    while True:

        # Reset counters every cycle
        TOTAL_CHECKED = 0
        VALID_COUNT = 0
        INVALID_COUNT = 0
        ERROR_COUNT = 0


        coupons = load_coupons()

        print("📊 Total coupons:", len(coupons), "\n")


        for code in coupons:

            print("Checking:", code)

            check_coupon(code, head)


            wait = random.randint(DELAY_MIN, DELAY_MAX)

            print(f"Waiting {wait} sec...\n")

            time.sleep(wait)


        # ================= SUMMARY =================

        print("\n================ ROUND SUMMARY ================\n")

        print("📌 Total Checked :", TOTAL_CHECKED)
        print("✅ Valid         :", VALID_COUNT)
        print("❌ Invalid       :", INVALID_COUNT)
        print("⚠️ Error/Skip    :", ERROR_COUNT)

        print("\n===============================================\n")


        print("🔁 Next round in 2 minutes...\n")

        time.sleep(CYCLE_DELAY)



# ================= RUN =================

if __name__ == "__main__":

    main()
