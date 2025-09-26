#define MyAppName "Expense Manager"
#define MyAppVersion "1.6.0"
#define MyAppPublisher "Mehmet Ali Soylu"
#define MyAppExeName "ExpenseManager"
#define MyAppFolder "C:\Users\mhmts\PycharmProjects\expense_manager\dist"

[Setup]
AppId={{6A339F67-3E46-4D6C-8C1B-6C8037C9F3F2}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
PrivilegesRequired=lowest
DefaultDirName={userpf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=installer\out
OutputBaseFilename=ExpenseManagerSetup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "{#MyAppFolder}\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
