from datetime import datetime

# ==========================================
# 1. Normalize IsPaid
# ==========================================

def normalize_is_paid(value):

    if value is None:
        return None

    value = str(value).strip().lower()

    paid_values = {
        "true",
        "1",
        "yes",
        "paid",
        "پرداخت شد",
        "پرداخت شده"
    }

    unpaid_values = {
        "false",
        "0",
        "no",
        "خیر",
        "پرداخت نشده"
    }

    if value in paid_values:
        return True

    if value in unpaid_values:
        return False

    return None


# ==========================================
# 2. Normalize Discount
# ==========================================

def normalize_discount(value):

    # مقدار خالی برابر صفر در نظر گرفته می‌شود
    if value is None:
        return 0

    if str(value).strip() == "":
        return 0

    try:
        return float(value)

    except (ValueError, TypeError):
        return None


# ==========================================
# 3. Validate Order
# ==========================================

def validate_order(order):

    issues = []

    quantity = order["Quantity"]
    unit_price = order["UnitPrice"]
    stock = order["Stock"]

    discount = normalize_discount(
        order["DiscountPercent"]
    )

    # بررسی Quantity
    if quantity <= 0:
        issues.append("Quantity نامعتبر است")

    # بررسی UnitPrice
    if unit_price is None or unit_price <= 0:
        issues.append("UnitPrice نامعتبر است")

    # بررسی موجودی
    if stock < quantity:
        issues.append("موجودی کافی نیست")

    # بررسی IsPaid
    is_paid = normalize_is_paid(
        order["IsPaid"]
    )

    if is_paid is None:
        issues.append("IsPaid نامعتبر است")

    elif not is_paid:
        issues.append("پرداخت نشده")

    # بررسی OrderDate
    try:

        datetime.strptime(
            str(order["OrderDate"]).strip(),
            "%Y-%m-%d"
        )

    except (ValueError, TypeError):

        issues.append("OrderDate نامعتبر است")

    # بررسی DiscountPercent
    if discount is None or discount < 0 or discount > 100:

        issues.append(
            "DiscountPercent نامعتبر است"
        )

    return issues


# ==========================================
# 4. Calculate Final Amount
# ==========================================

def calculate_final_amount(order):

    quantity = order["Quantity"]
    unit_price = order["UnitPrice"]

    discount = normalize_discount(
        order["DiscountPercent"]
    )

    # Quantity نامعتبر
    if quantity <= 0:
        return "N/A"

    # UnitPrice نامعتبر
    if unit_price is None or unit_price <= 0:
        return "N/A"

    # Discount نامعتبر
    if discount is None or discount < 0 or discount > 100:
        return "N/A"

    # محاسبه مبلغ نهایی
    return quantity * unit_price * (
        1 - discount / 100
    )


# ==========================================
# 5. Determine Final Status
# ==========================================

def determine_status(issues):

    # بدون خطا
    if not issues:
        return "قابل ارسال"

    # خطاهای داده
    data_errors = {
        "OrderId تکراری",
        "IsPaid نامعتبر است",
        "Quantity نامعتبر است",
        "UnitPrice نامعتبر است",
        "OrderDate نامعتبر است",
        "DiscountPercent نامعتبر است"
    }

    for issue in issues:

        if issue in data_errors:
            return "خطای داده"

    # مشکل موجودی
    if "موجودی کافی نیست" in issues:
        return "مشکل موجودی"

    # پرداخت نشده
    if "پرداخت نشده" in issues:
        return "پرداخت نشده"

    # حالت پیش‌فرض
    return "خطای داده"


# ==========================================
# 6. Process One Order
# ==========================================

def process_order(order):

    # پیدا کردن خطاها
    issues = validate_order(order)

    # نرمال‌سازی وضعیت پرداخت
    is_paid_normalized = normalize_is_paid(
        order["IsPaid"]
    )

    # محاسبه مبلغ نهایی
    final_amount = calculate_final_amount(
        order
    )

    # تعیین وضعیت نهایی
    final_status = determine_status(
        issues
    )

    # ساخت نتیجه
    return {

        "OrderId": order["OrderId"],

        "CustomerName": order["CustomerName"],

        "ProductName": order["ProductName"],

        "FinalAmount": final_amount,

        "IsPaidNormalized": is_paid_normalized,

        "Issues": issues,

        "FinalStatus": final_status
    }


# ==========================================
# 7. Find Duplicate Order IDs
# ==========================================

def find_duplicate_order_ids(orders):

    counts = {}

    # شمارش شناسه سفارش‌ها
    for order in orders:

        order_id = order["OrderId"]

        if order_id in counts:
            counts[order_id] += 1

        else:
            counts[order_id] = 1

    # پیدا کردن شناسه‌های تکراری
    duplicates = set()

    for order_id, count in counts.items():

        if count > 1:
            duplicates.add(order_id)

    return duplicates


# ==========================================
# 8. Test Orders
# ==========================================

orders = [

    {
        "OrderId": 2001,
        "CustomerName": 'آیدا',
        "ProductName": 'لپ\u200cتاپ ThinkBook',
        "Quantity": 1,
        "UnitPrice": 68500000,
        "Stock": 3,
        "IsPaid": 'TRUE',
        "OrderDate": '2026-07-01',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2002,
        "CustomerName": 'بردیا',
        "ProductName": 'مانیتور 27 اینچ',
        "Quantity": 2,
        "UnitPrice": 14800000,
        "Stock": 9,
        "IsPaid": 'Paid',
        "OrderDate": '2026-07-01',
        "DiscountPercent": 5
    },

    {
        "OrderId": 2003,
        "CustomerName": 'ترانه',
        "ProductName": 'کیبورد مکانیکی',
        "Quantity": 1,
        "UnitPrice": 4250000,
        "Stock": 12,
        "IsPaid": 'yes',
        "OrderDate": '2026-07-02',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2004,
        "CustomerName": 'جواد',
        "ProductName": 'ماوس بی\u200cسیم',
        "Quantity": 3,
        "UnitPrice": 1850000,
        "Stock": 15,
        "IsPaid": '1',
        "OrderDate": '2026-07-02',
        "DiscountPercent": 10
    },

    {
        "OrderId": 2005,
        "CustomerName": 'حدیث',
        "ProductName": 'وب\u200cکم Full HD',
        "Quantity": 2,
        "UnitPrice": 3550000,
        "Stock": 7,
        "IsPaid": 'پرداخت شد',
        "OrderDate": '2026-07-03',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2006,
        "CustomerName": 'خسرو',
        "ProductName": 'پایه مانیتور',
        "Quantity": 1,
        "UnitPrice": 2100000,
        "Stock": 8,
        "IsPaid": 'TRUE',
        "OrderDate": '2026-07-03',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2007,
        "CustomerName": 'دانیال',
        "ProductName": 'هاب USB-C',
        "Quantity": 4,
        "UnitPrice": 1450000,
        "Stock": 20,
        "IsPaid": 'Paid',
        "OrderDate": '2026-07-04',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2008,
        "CustomerName": 'روناک',
        "ProductName": 'هدفون نویزکنسلینگ',
        "Quantity": 1,
        "UnitPrice": 9800000,
        "Stock": 5,
        "IsPaid": 'TRUE',
        "OrderDate": '2026-07-04',
        "DiscountPercent": 15
    },

    {
        "OrderId": 2009,
        "CustomerName": 'زیبا',
        "ProductName": 'پرینتر لیزری',
        "Quantity": 1,
        "UnitPrice": 17200000,
        "Stock": 4,
        "IsPaid": 'yes',
        "OrderDate": '2026-07-05',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2010,
        "CustomerName": 'سام',
        "ProductName": 'کارت حافظه 128GB',
        "Quantity": 5,
        "UnitPrice": 890000,
        "Stock": 30,
        "IsPaid": '1',
        "OrderDate": '2026-07-05',
        "DiscountPercent": 5
    },

    {
        "OrderId": 2011,
        "CustomerName": 'شبنم',
        "ProductName": 'میکروفون رومیزی',
        "Quantity": 2,
        "UnitPrice": 2900000,
        "Stock": 11,
        "IsPaid": 'TRUE',
        "OrderDate": '2026-07-06',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2012,
        "CustomerName": 'شایان',
        "ProductName": 'کابل HDMI',
        "Quantity": 6,
        "UnitPrice": 380000,
        "Stock": 40,
        "IsPaid": 'Paid',
        "OrderDate": '2026-07-06',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2013,
        "CustomerName": 'شیما',
        "ProductName": 'روتر دوبانده',
        "Quantity": 1,
        "UnitPrice": 6450000,
        "Stock": 6,
        "IsPaid": 'پرداخت شد',
        "OrderDate": '2026-07-07',
        "DiscountPercent": 8
    },

    {
        "OrderId": 2014,
        "CustomerName": 'صالح',
        "ProductName": 'صندلی ارگونومیک',
        "Quantity": 1,
        "UnitPrice": 13700000,
        "Stock": 3,
        "IsPaid": 'TRUE',
        "OrderDate": '2026-07-07',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2015,
        "CustomerName": 'ضیا',
        "ProductName": 'فلش 64GB',
        "Quantity": 10,
        "UnitPrice": 420000,
        "Stock": 60,
        "IsPaid": 'yes',
        "OrderDate": '2026-07-08',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2016,
        "CustomerName": 'طناز',
        "ProductName": 'شارژر لپ\u200cتاپ',
        "Quantity": 2,
        "UnitPrice": 1950000,
        "Stock": 14,
        "IsPaid": 'TRUE',
        "OrderDate": '2026-07-08',
        "DiscountPercent": 12
    },

    {
        "OrderId": 2017,
        "CustomerName": 'علی',
        "ProductName": 'اسپیکر رومیزی',
        "Quantity": 1,
        "UnitPrice": 3750000,
        "Stock": 8,
        "IsPaid": 'Paid',
        "OrderDate": '2026-07-09',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2018,
        "CustomerName": 'غزل',
        "ProductName": 'تبلت آموزشی',
        "Quantity": 2,
        "UnitPrice": 11600000,
        "Stock": 5,
        "IsPaid": '1',
        "OrderDate": '2026-07-09',
        "DiscountPercent": 5
    },

    {
        "OrderId": 2019,
        "CustomerName": 'فریبا',
        "ProductName": 'دوربین مداربسته',
        "Quantity": 3,
        "UnitPrice": 4250000,
        "Stock": 10,
        "IsPaid": 'TRUE',
        "OrderDate": '2026-07-10',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2020,
        "CustomerName": 'قاسم',
        "ProductName": 'کابل شبکه CAT6',
        "Quantity": 15,
        "UnitPrice": 175000,
        "Stock": 100,
        "IsPaid": 'پرداخت شد',
        "OrderDate": '2026-07-10',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2021,
        "CustomerName": 'کامبیز',
        "ProductName": 'مودم 5G',
        "Quantity": 1,
        "UnitPrice": 12800000,
        "Stock": 4,
        "IsPaid": 'yes',
        "OrderDate": '2026-07-11',
        "DiscountPercent": 10
    },

    {
        "OrderId": 2022,
        "CustomerName": 'لاله',
        "ProductName": 'نمایشگر لمسی',
        "Quantity": 1,
        "UnitPrice": 26500000,
        "Stock": 2,
        "IsPaid": 'TRUE',
        "OrderDate": '2026-07-11',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2023,
        "CustomerName": 'مهدی',
        "ProductName": 'دیسک SSD یک ترابایت',
        "Quantity": 2,
        "UnitPrice": 7900000,
        "Stock": 9,
        "IsPaid": 'Paid',
        "OrderDate": '2026-07-12',
        "DiscountPercent": 5
    },

    {
        "OrderId": 2024,
        "CustomerName": 'نغمه',
        "ProductName": 'قلم نوری',
        "Quantity": 1,
        "UnitPrice": 5600000,
        "Stock": 7,
        "IsPaid": '1',
        "OrderDate": '2026-07-12',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2025,
        "CustomerName": 'وحید',
        "ProductName": 'آداپتور DisplayPort',
        "Quantity": 3,
        "UnitPrice": 690000,
        "Stock": 17,
        "IsPaid": 'TRUE',
        "OrderDate": '2026-07-13',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2026,
        "CustomerName": 'هانیه',
        "ProductName": 'اسکنر اسناد',
        "Quantity": 1,
        "UnitPrice": 9700000,
        "Stock": 3,
        "IsPaid": 'پرداخت شد',
        "OrderDate": '2026-07-13',
        "DiscountPercent": 20
    },

    {
        "OrderId": 2027,
        "CustomerName": 'یاسر',
        "ProductName": 'تلفن تحت شبکه',
        "Quantity": 4,
        "UnitPrice": 3150000,
        "Stock": 13,
        "IsPaid": 'yes',
        "OrderDate": '2026-07-14',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2028,
        "CustomerName": 'ارغوان',
        "ProductName": 'پاوربانک 20000',
        "Quantity": 2,
        "UnitPrice": 2450000,
        "Stock": 20,
        "IsPaid": 'TRUE',
        "OrderDate": '2026-07-14',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2029,
        "CustomerName": 'بهنام',
        "ProductName": 'دستگاه کپی رومیزی',
        "Quantity": 1,
        "UnitPrice": 34500000,
        "Stock": 2,
        "IsPaid": 'Paid',
        "OrderDate": '2026-07-15',
        "DiscountPercent": 7
    },

    {
        "OrderId": 2030,
        "CustomerName": 'پریا',
        "ProductName": 'کارت گرافیک',
        "Quantity": 1,
        "UnitPrice": 43800000,
        "Stock": 5,
        "IsPaid": '1',
        "OrderDate": '2026-07-15',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2031,
        "CustomerName": 'ثنا',
        "ProductName": 'ماشین حساب مهندسی',
        "Quantity": 2,
        "UnitPrice": 1870000,
        "Stock": 9,
        "IsPaid": 'TRUE',
        "OrderDate": '2026-07-16',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2032,
        "CustomerName": 'چکامه',
        "ProductName": 'چراغ مطالعه LED',
        "Quantity": 3,
        "UnitPrice": 980000,
        "Stock": 25,
        "IsPaid": 'پرداخت شد',
        "OrderDate": '2026-07-16',
        "DiscountPercent": 5
    },

    {
        "OrderId": 2033,
        "CustomerName": 'حامد',
        "ProductName": 'ویدئو پروژکتور',
        "Quantity": 1,
        "UnitPrice": 22800000,
        "Stock": 4,
        "IsPaid": 'yes',
        "OrderDate": '2026-07-17',
        "DiscountPercent": 10
    },

    {
        "OrderId": 2034,
        "CustomerName": 'خورشید',
        "ProductName": 'دستگاه حضور و غیاب',
        "Quantity": 1,
        "UnitPrice": 18500000,
        "Stock": 3,
        "IsPaid": 'TRUE',
        "OrderDate": '2026-07-17',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2035,
        "CustomerName": 'رضا',
        "ProductName": 'کیف دوربین',
        "Quantity": 1,
        "UnitPrice": 2650000,
        "Stock": 8,
        "IsPaid": 'FALSE',
        "OrderDate": '2026-07-18',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2036,
        "CustomerName": 'ساغر',
        "ProductName": 'کابل Type-C',
        "Quantity": 4,
        "UnitPrice": 290000,
        "Stock": 30,
        "IsPaid": 'no',
        "OrderDate": '2026-07-18',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2037,
        "CustomerName": 'سروش',
        "ProductName": 'صندوق پول',
        "Quantity": 1,
        "UnitPrice": 7850000,
        "Stock": 4,
        "IsPaid": 'خیر',
        "OrderDate": '2026-07-19',
        "DiscountPercent": 5
    },

    {
        "OrderId": 2038,
        "CustomerName": 'سپیده',
        "ProductName": 'باتری UPS',
        "Quantity": 2,
        "UnitPrice": 3650000,
        "Stock": 8,
        "IsPaid": '0',
        "OrderDate": '2026-07-19',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2039,
        "CustomerName": 'شهرام',
        "ProductName": 'ترازو دیجیتال',
        "Quantity": 1,
        "UnitPrice": 5400000,
        "Stock": 5,
        "IsPaid": 'FALSE',
        "OrderDate": '2026-07-20',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2040,
        "CustomerName": 'شکوفه',
        "ProductName": 'کیف لپ\u200cتاپ چرمی',
        "Quantity": 1,
        "UnitPrice": 3150000,
        "Stock": 10,
        "IsPaid": 'no',
        "OrderDate": '2026-07-20',
        "DiscountPercent": 15
    },

    {
        "OrderId": 2041,
        "CustomerName": 'صبا',
        "ProductName": 'مبدل برق صنعتی',
        "Quantity": 7,
        "UnitPrice": 850000,
        "Stock": 4,
        "IsPaid": 'TRUE',
        "OrderDate": '2026-07-21',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2042,
        "CustomerName": 'ضیاء',
        "ProductName": 'کاغذ پرینتر A4',
        "Quantity": 25,
        "UnitPrice": 235000,
        "Stock": 18,
        "IsPaid": 'Paid',
        "OrderDate": '2026-07-21',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2043,
        "CustomerName": 'طاهر',
        "ProductName": 'هارد اکسترنال 2TB',
        "Quantity": 3,
        "UnitPrice": 6900000,
        "Stock": 2,
        "IsPaid": '1',
        "OrderDate": '2026-07-22',
        "DiscountPercent": 10
    },

    {
        "OrderId": 2044,
        "CustomerName": 'عاطفه',
        "ProductName": 'کابل VGA',
        "Quantity": 12,
        "UnitPrice": 250000,
        "Stock": 9,
        "IsPaid": 'TRUE',
        "OrderDate": '2026-07-22',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2045,
        "CustomerName": 'غلام',
        "ProductName": 'پرینتر حرارتی',
        "Quantity": 2,
        "UnitPrice": 7800000,
        "Stock": 1,
        "IsPaid": 'پرداخت شد',
        "OrderDate": '2026-07-23',
        "DiscountPercent": 5
    },

    {
        "OrderId": 2046,
        "CustomerName": 'فرزانه',
        "ProductName": 'پایه خنک\u200cکننده',
        "Quantity": 5,
        "UnitPrice": 1650000,
        "Stock": 3,
        "IsPaid": 'yes',
        "OrderDate": '2026-07-23',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2047,
        "CustomerName": 'کوروش',
        "ProductName": 'سوییچ 16 پورت',
        "Quantity": 4,
        "UnitPrice": 8950000,
        "Stock": 2,
        "IsPaid": 'TRUE',
        "OrderDate": '2026-07-24',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2048,
        "CustomerName": 'لیلا',
        "ProductName": 'دستگاه پانچ',
        "Quantity": 0,
        "UnitPrice": 1250000,
        "Stock": 6,
        "IsPaid": 'TRUE',
        "OrderDate": '2026-07-24',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2049,
        "CustomerName": 'منوچهر',
        "ProductName": 'وای\u200cفای اکستندر',
        "Quantity": 1,
        "UnitPrice": None,
        "Stock": 7,
        "IsPaid": 'Paid',
        "OrderDate": '2026-07-25',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2050,
        "CustomerName": 'نازنین',
        "ProductName": 'دوربین کنفرانس',
        "Quantity": 1,
        "UnitPrice": 24500000,
        "Stock": 2,
        "IsPaid": 'TRUE',
        "OrderDate": '31-07-2026',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2051,
        "CustomerName": 'هومن',
        "ProductName": 'نمایشگر LED',
        "Quantity": 1,
        "UnitPrice": 19800000,
        "Stock": 4,
        "IsPaid": 'TRUE',
        "OrderDate": '2026-07-26',
        "DiscountPercent": 105
    },

    {
        "OrderId": 2052,
        "CustomerName": 'یگانه',
        "ProductName": 'دستگاه صحافی',
        "Quantity": 2,
        "UnitPrice": 4600000,
        "Stock": 5,
        "IsPaid": 'TRUE',
        "OrderDate": '2026-07-26',
        "DiscountPercent": -10
    },

    {
        "OrderId": 2053,
        "CustomerName": 'امیرحسین',
        "ProductName": 'اسکنر بارکد',
        "Quantity": 3,
        "UnitPrice": 1950000,
        "Stock": -1,
        "IsPaid": 'TRUE',
        "OrderDate": '2026-07-27',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2054,
        "CustomerName": 'بهاره',
        "ProductName": 'محافظ برق',
        "Quantity": 1,
        "UnitPrice": 780000,
        "Stock": 15,
        "IsPaid": 'awaiting',
        "OrderDate": '2026-07-27',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2055,
        "CustomerName": 'پویان',
        "ProductName": 'مینی کامپیوتر',
        "Quantity": -2,
        "UnitPrice": 14200000,
        "Stock": 5,
        "IsPaid": 'TRUE',
        "OrderDate": '2026-07-28',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2056,
        "CustomerName": 'تینا',
        "ProductName": 'دستگاه حضور و غیاب ابری',
        "Quantity": 1,
        "UnitPrice": 23700000,
        "Stock": 3,
        "IsPaid": 'Paid',
        "OrderDate": '2026-07-28',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2057,
        "CustomerName": 'جلیل',
        "ProductName": 'کیس کامپیوتر',
        "Quantity": 2,
        "UnitPrice": 6300000,
        "Stock": 7,
        "IsPaid": '1',
        "OrderDate": '2026-07-29',
        "DiscountPercent": 5
    },

    {
        "OrderId": 2058,
        "CustomerName": 'خاطره',
        "ProductName": 'ماژول GPS',
        "Quantity": 4,
        "UnitPrice": 1150000,
        "Stock": 11,
        "IsPaid": 'TRUE',
        "OrderDate": '2026-07-29',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2059,
        "CustomerName": 'رامین',
        "ProductName": 'پد ماوس طبی',
        "Quantity": 3,
        "UnitPrice": 650000,
        "Stock": 16,
        "IsPaid": 'پرداخت شد',
        "OrderDate": '2026-07-30',
        "DiscountPercent": 0
    },

    {
        "OrderId": 2060,
        "CustomerName": 'زرین',
        "ProductName": 'دستگاه فکس',
        "Quantity": 1,
        "UnitPrice": 9200000,
        "Stock": 4,
        "IsPaid": 'yes',
        "OrderDate": '2026-07-30',
        "DiscountPercent": 10
    },
]

# ==========================================
# 9. Find Duplicates
# ==========================================

duplicate_ids = find_duplicate_order_ids(
    orders
)


# ==========================================
# 10. Process All Orders
# ==========================================

results = []

for order in orders:

    result = process_order(order)

    # بررسی تکراری بودن OrderId
    if order["OrderId"] in duplicate_ids:

        result["Issues"].append(
            "OrderId تکراری"
        )

        result["FinalStatus"] = "خطای داده"

    results.append(result)


# ==========================================
# 11. Show Results
# ==========================================

print(
    "\n================ RESULTS ================\n"
)


for result in results:

    print(
        "OrderId:",
        result["OrderId"]
    )

    print(
        "Customer:",
        result["CustomerName"]
    )

    print(
        "Product:",
        result["ProductName"]
    )

    print(
        "FinalAmount:",
        result["FinalAmount"]
    )

    print(
        "IsPaidNormalized:",
        result["IsPaidNormalized"]
    )

    print(
        "Issues:",
        result["Issues"]
    )

    print(
        "FinalStatus:",
        result["FinalStatus"]
    )

    print(
        "----------------------------------------"
    )