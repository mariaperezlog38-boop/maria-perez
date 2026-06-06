[Setup]
AppName=Calculadora BCV
AppVersion=1.0.0
DefaultDirName={pf}\Calculadora BCV
DefaultGroupName=Calculadora BCV
DisableProgramGroupPage=yes
OutputDir=.
OutputBaseFilename=CalculadoraBCV_Installer
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "dist\\CalculadoraBCV.exe"; DestDir: "{app}"; Flags: ignoreversion restartreplace
Source: "fondo.png"; DestDir: "{app}"; Flags: ignoreversion restartreplace

[Icons]
Name: "{group}\\Calculadora BCV"; Filename: "{app}\\CalculadoraBCV.exe"
Name: "{commondesktop}\\Calculadora BCV"; Filename: "{app}\\CalculadoraBCV.exe"; Tasks: desktopicon

[Tasks]
Name: desktopicon; Description: "Crear un acceso directo en el escritorio"; GroupDescription: "Iconos:"; Flags: unchecked

[Run]
Filename: "{app}\\CalculadoraBCV.exe"; Description: "Lanzar Calculadora BCV"; Flags: nowait postinstall shellexec

[Code]
function CmdLineParamExists(const Param: string): Boolean;
var
	i: Integer;
begin
	Result := False;
	for i := 1 to ParamCount do
		if CompareText(ParamStr(i), '/' + Param) = 0 then
		begin
			Result := True;
			Exit;
		end;
end;

procedure KillAppIfRunning();
var
	ResultCode: Integer;
begin
	// Try to close the application silently (Windows taskkill). Non-fatal if it fails.
	Exec('taskkill', '/F /IM CalculadoraBCV.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

function InitializeSetup(): Boolean;
var
	ResultCode: Integer;
begin
	// If installer runs in silent update mode, attempt to close running app silently
	if CmdLineParamExists('SILENTUPDATE') or CmdLineParamExists('VERYSILENT') then
	begin
		KillAppIfRunning();
	end
	else
	begin
		// Normal install: if app is running, prompt user to close it
		if Exec('tasklist', '/FI "IMAGENAME eq CalculadoraBCV.exe" /NH', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
		begin
			// We cannot reliably parse output here; just try to kill and continue
			KillAppIfRunning();
		end;
	end;

	Result := True;
end;
