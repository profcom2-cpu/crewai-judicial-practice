# Ярлык на рабочем столе: отдельное приложение CrewAI Practice.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$bat = Join-Path $root "scripts\launch_desktop.bat"
$desktop = [Environment]::GetFolderPath("Desktop")
# ASCII-имя: Windows PowerShell 5 иначе портит кириллицу в .lnk
$lnkPath = Join-Path $desktop "CrewAI Practice.lnk"
$shell = New-Object -ComObject WScript.Shell
$lnk = $shell.CreateShortcut($lnkPath)
$lnk.TargetPath = $bat
$lnk.WorkingDirectory = $root
$lnk.WindowStyle = 7
$lnk.Description = "Пилот CrewAI: поиск судебной практики"
$lnk.Save()
Write-Output $lnkPath
