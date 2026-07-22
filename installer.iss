#define MyAppName "Elita Reports Extractor"
#define MyAppVersion GetEnv("APP_VERSION")
#define MyAppPublisher "Nguyen Minh Duc"
#define MyAppExeName "Elita Reports Extractor.exe"

[Setup]
AppId={{6C88B7C6-55D2-4E90-B5E8-92E66F7A1234}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\Elita Reports Extractor
DefaultGroupName=Elita Reports Extractor

OutputDir=Release
OutputBaseFilename=Elita Reports Extractor_Setup_v{#MyAppVersion}

Compression=lzma
SolidCompression=yes

WizardStyle=modern

SetupIconFile=icon.ico

PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]

Source: "dist\Elita Reports Extractor\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]

Name: "{group}\Elita Reports Extractor"; Filename: "{app}\Elita Reports Extractor.exe"

Name: "{autodesktop}\Elita Reports Extractor"; Filename: "{app}\Elita Reports Extractor.exe"; Tasks: desktopicon

[Tasks]

Name: "desktopicon"; Description: "Desktop icon included"; GroupDescription: "Additional icons:"

[Run]

Filename: "{app}\Elita Reports Extractor.exe"; Description: "Launch Elita Reports Extractor"; Flags: nowait postinstall skipifsilent