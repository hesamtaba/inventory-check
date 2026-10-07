#define MyAppName "InventoryChecker"
#define MyAppVersion "1.0.0"
#define MyAppExeName "InventoryChecker.exe"
[Setup]
AppId={{B9859368-94E0-4D25-A965-9DA1E879FF45}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf64}\InventoryChecker
DefaultGroupName=InventoryChecker
OutputDir=..\dist
OutputBaseFilename=InventoryChecker_Setup_1.0.0
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
UninstallDisplayIcon={app}\{#MyAppExeName}
[Tasks]
Name: "desktopicon"; Description: "ایجاد میانبر روی Desktop"; GroupDescription: "میانبرها:"; Flags: unchecked
[Files]
Source: "..\dist\InventoryChecker\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\InventoryChecker"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\InventoryChecker"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "اجرای InventoryChecker"; Flags: nowait postinstall skipifsilent
; User data lives under %LOCALAPPDATA%\InventoryChecker and is intentionally not removed on uninstall.
