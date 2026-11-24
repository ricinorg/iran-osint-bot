import re
PREFIXES = {
"همراه اول (پیش‌شماره اولیه)": {"0910","0911","0912","0913","0914","0915","0916","0917","0918","0919","0990","0991","0992","0993"},
"ایرانسل (پیش‌شماره اولیه)": {"0901","0902","0903","0904","0905","0930","0933","0935","0936","0937","0938","0939"},
"رایتل (پیش‌شماره اولیه)": {"0920","0921","0922"}}
def normalize_iran_mobile(value: str):
    digits = re.sub(r"[\s\-()]", "", value)
    if digits.startswith("+98"): digits = "0" + digits[3:]
    elif digits.startswith("0098"): digits = "0" + digits[4:]
    elif digits.startswith("98") and len(digits) == 12: digits = "0" + digits[2:]
    return digits if re.fullmatch(r"09\d{9}", digits) else None
def inspect_phone(value: str):
    number = normalize_iran_mobile(value)
    if not number: return {"valid": False}
    prefix = number[:4]
    carrier = next((name for name, prefixes in PREFIXES.items() if prefix in prefixes), "اپراتور نامشخص")
    return {"valid": True, "number": number, "prefix": prefix, "carrier": carrier}
