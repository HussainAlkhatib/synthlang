!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "FileFunc.nsh"

Name "SynthLang"
OutFile "set-slang.exe"
InstallDir "C:\slang"
SetCompressor /SOLID lzma
RequestExecutionLevel admin

!define VERSION "1.0.0"
!define PUBLISHER "SynthLang Team"

!define MUI_ICON "assets\installer-icon.ico"
!define MUI_UNICON "assets\uninstaller-icon.ico"
!define MUI_ABORTWARNING

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "French"
!insertmacro MUI_LANGUAGE "German"
!insertmacro MUI_LANGUAGE "Spanish"

Section "MainSection" SEC01
    SectionIn RO
    SetOutPath "$INSTDIR"
    
    File "dist\slang.exe"
    CreateDirectory "$INSTDIR\bin"
    Rename "$INSTDIR\slang.exe" "$INSTDIR\bin\slang.exe"
    
    CreateDirectory "$INSTDIR\lib\core"
    CreateDirectory "$INSTDIR\lib\stdlib"
    CreateDirectory "$INSTDIR\lib\slangs\python"
    CreateDirectory "$INSTDIR\lib\slangs\node"
    
    SetOutPath "$INSTDIR\colors"
    File /r "colors\*.*"
    
    SetOutPath "$INSTDIR\docs"
    File /r "docs\*.*"
    
    SetOutPath "$INSTDIR\examples"
    File /r "examples\*.*"
    
    SetOutPath "$INSTDIR\projects"
    File /r "projects\*.*"
    
    SetOutPath "$INSTDIR\assets"
    File /r "assets\*.*"
    
    SetOutPath "$INSTDIR\tools\vscode-extension"
    SetOutPath "$INSTDIR\tools\lsp-server"
    
    FileOpen $0 "$INSTDIR\version.txt" w
    FileWrite $0 "${VERSION}"
    FileClose $0
SectionEnd

Section "PATHSection" SEC02
    ReadRegStr $0 HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "Path"
    ${If} $0 != ""
        StrCpy $0 "$0;$INSTDIR\bin"
    ${Else}
        StrCpy $0 "$INSTDIR\bin"
    ${EndIf}
    WriteRegStr HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "Path" $0
SectionEnd

Section "VSCodeSection" SEC03
    SetOutPath "$INSTDIR\tools\vscode-extension"
    ${If} ${FileExists} "vscode-synthlang\*.*"
        File /r "vscode-synthlang\*.*"
    ${EndIf}
SectionEnd

Section "AntigravitySection" SEC04
    CreateDirectory "$PROFILE\.antigravity-ide\extensions"
    SetOutPath "$PROFILE\.antigravity-ide\extensions\synthlang-1.0.0"
    File /r "colors\antigravity\*.*"
SectionEnd

Section "ShortcutsSection" SEC05
    CreateDirectory "$SMPROGRAMS\SynthLang"
    CreateShortCut "$SMPROGRAMS\SynthLang\Uninstall.lnk" "$INSTDIR\uninstall.exe"
    CreateShortCut "$SMPROGRAMS\SynthLang\Documentation.lnk" "$INSTDIR\docs\syntax.md"
SectionEnd

Section "-Finish"
    WriteRegStr HKLM "Software\SynthLang" "InstallPath" "$INSTDIR"
    WriteRegStr HKLM "Software\SynthLang" "Version" "${VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SynthLang" "DisplayName" "SynthLang"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SynthLang" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SynthLang" "DisplayVersion" "${VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SynthLang" "Publisher" "${PUBLISHER}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SynthLang" "DisplayIcon" "$INSTDIR\assets\installer-icon.ico"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SynthLang" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SynthLang" "NoRepair" 1
    
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; Register .sl file association with icon
    WriteRegStr HKCR ".sl" "" "SynthLang.File"
    WriteRegStr HKCR "SynthLang.File" "" "SynthLang Source File"
    WriteRegStr HKCR "SynthLang.File\DefaultIcon" "" "$INSTDIR\assets\installer-icon.ico"
    WriteRegStr HKCR "SynthLang.File\shell\open\command" "" '"$INSTDIR\bin\slang.exe" "%1"'
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\bin\slang.exe"
    Delete "$INSTDIR\version.txt"
    Delete "$INSTDIR\uninstall.exe"
    
    Delete "$SMPROGRAMS\SynthLang\Uninstall.lnk"
    Delete "$SMPROGRAMS\SynthLang\Documentation.lnk"
    RMDir "$SMPROGRAMS\SynthLang"
    
    DeleteRegKey HKLM "Software\SynthLang"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SynthLang"
    
    ; Unregister .sl file association
    DeleteRegKey HKCR "SynthLang.File"
    DeleteRegKey HKCR ".sl"
    
    RMDir "$INSTDIR\colors\vscode"
    RMDir "$INSTDIR\colors\sublime"
    RMDir "$INSTDIR\colors\vim\syntax"
    RMDir "$INSTDIR\colors\vim\ftdetect"
    RMDir "$INSTDIR\colors\vim"
    RMDir "$INSTDIR\colors\neovim\syntax"
    RMDir "$INSTDIR\colors\neovim\ftdetect"
    RMDir "$INSTDIR\colors\neovim"
    RMDir "$INSTDIR\colors\emacs"
    RMDir "$INSTDIR\colors\jetbrains"
    RMDir "$INSTDIR\colors\notepadpp"
    RMDir "$INSTDIR\colors\antigravity"
    RMDir "$INSTDIR\colors"
    
    Delete "$PROFILE\.antigravity-ide\extensions\synthlang-1.0.0\*.*"
    RMDir "$PROFILE\.antigravity-ide\extensions\synthlang-1.0.0"
    
    RMDir "$INSTDIR\tools\vscode-extension"
    RMDir "$INSTDIR\tools\lsp-server"
    RMDir "$INSTDIR\tools"
    RMDir "$INSTDIR\docs"
    RMDir "$INSTDIR\examples"
    RMDir "$INSTDIR\projects"
    RMDir "$INSTDIR\assets"
    RMDir "$INSTDIR\lib\slangs\python"
    RMDir "$INSTDIR\lib\slangs\node"
    RMDir "$INSTDIR\lib\slangs"
    RMDir "$INSTDIR\lib\stdlib"
    RMDir "$INSTDIR\lib\core"
    RMDir "$INSTDIR\lib"
    RMDir "$INSTDIR\bin"
    
    RMDir "$INSTDIR"
SectionEnd