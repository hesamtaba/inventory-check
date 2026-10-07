# InventoryChecker 1.0.0

نرم‌افزار آفلاین ویندوز برای مغایرت‌گیری موجودی و شماره لیبل با Python 3.12، PySide6، SQLite، pandas و openpyxl.

## ساختار فایل نمونه واقعی
فایل `نرم افزار مغایرت گیری.xlsx` بررسی شده است. شیت‌ها: `موجودی`، `ثبت لیبل`، `مغایرت` و `طرح نرم افزار`. شیت `موجودی` دارای 839 ردیف و 16 ستون است؛ سرستون در ردیف 1 و ستون لیبل صحیح `محصول` است. نمونه واقعی: `GD02002967 - میرو` که به `GD02002967` نرمال می‌شود.

## اجرا از سورس
1. Python 3.12 x64 نصب کنید.
2. در پوشه پروژه: `py -3.12 -m venv .venv`
3. `.venv\\Scripts\\activate`
4. `pip install -r requirements.txt`
5. `run.bat`

## ساخت EXE و Setup روی Windows 10/11 x64
Inno Setup 6 و Python 3.12 x64 را نصب کنید. سپس `build.bat` را اجرا کنید. تست‌ها ابتدا اجرا می‌شوند و بعد خروجی onedir در `dist\\InventoryChecker\\InventoryChecker.exe` ساخته می‌شود. اگر `ISCC.exe` در PATH باشد Setup نیز ساخته می‌شود؛ در غیر این صورت `installer\\installer.iss` را با Inno Setup Compiler باز و Compile کنید. خروجی Setup: `dist\\InventoryChecker_Setup_1.0.0.exe`.

## داده‌های کاربر
دیتابیس و Log در `%LOCALAPPDATA%\\InventoryChecker` قرار می‌گیرند و Uninstaller آن‌ها را حذف نمی‌کند.

## نکات
- فایل‌های `.xlsx` و `.xls` پشتیبانی می‌شوند (`xlrd` برای xls).
- عملیات بارگذاری موجودی، ورود گروهی و خروجی در Thread پس‌زمینه اجرا می‌شوند.
- تمام لیبل‌ها رشته هستند و صفر ابتدایی حفظ می‌شود.
- برای صدای موفق/هشدار از beep سیستم استفاده شده تا برنامه کاملاً آفلاین و بدون وابستگی فایل صوتی باشد.
- آزمون واقعی Windows 10/11 و ساخت نهایی PyInstaller/Inno Setup باید روی Windows x64 انجام شود؛ محیط Linux نمی‌تواند اعتبار اجرایی Windows را تضمین کند.

## ساخت خودکار EXE با GitHub Actions

پروژه شامل فایل `.github/workflows/build-windows.yml` است. پس از قراردادن کل محتویات پروژه در یک Repository گیت‌هاب:

1. وارد تب **Actions** شوید.
2. Workflow با نام **Build Windows EXE** را انتخاب کنید.
3. روی **Run workflow** و سپس **Run workflow** کلیک کنید.
4. پس از سبز شدن Build، در همان صفحه از بخش **Artifacts** فایل `InventoryChecker-Windows-x64-1.0.0` را دانلود کنید.
5. داخل Artifact، فایل اجرایی در `dist/InventoryChecker/InventoryChecker.exe` و نسخه Portable به نام `InventoryChecker_Windows_x64_1.0.0.zip` قرار دارد.

Workflow روی Windows x64 و Python 3.12 اجرا می‌شود، وابستگی‌ها را نصب می‌کند، تست‌ها را اجرا می‌کند و فقط در صورت موفقیت تست‌ها EXE را تحویل می‌دهد.
