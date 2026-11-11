[Setup]
AppName=FluxDev
AppVersion=1.0.0
AppPublisher=Kamalesh G
DefaultDirName={autopf}\FluxDev
DefaultGroupName=FluxDev
OutputBaseFilename=FluxDev-Setup-1.0.0
OutputDir=installer_output
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "dist\FluxDev\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\FluxDev"; Filename: "{app}\FluxDev.exe"
Name: "{autodesktop}\FluxDev"; Filename: "{app}\FluxDev.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"

[Run]
Filename: "{app}\FluxDev.exe"; Description: "Launch FluxDev"; Flags: nowait postinstall skipifsilent