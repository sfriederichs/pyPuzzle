#NSIS Example Install Script
#This file will be placed in the 'install' subdirectory in the project

#Basic definitions
!define APPNAME "Sample App"
!define COMPANYNAME "Steves Toolbox LLC"
!define DESCRIPTION "Basic Python Application"
!define APPSHORTNAME "pyCli"

#Ask for administrative rights
RequestExecutionLevel admin

#Other options include:
#none
#user
#highest

#Default installation location - Program Files or Program Files (x86)
InstallDir "$PROGRAMFILES\${APPSHORTNAME}"

#Text (or RTF) file with license information. The text file must be in DOS end line format (\r\n)
LicenseData "..\license.md"

#'Name' goes in the installer's title bar
Name "${COMPANYNAME}-${APPSHORTNAME}"

#Icon for the installer - this is the default icon
#Icon "logo.ico"

#The following lines replace the default icons
!include "MUI2.nsh"

#The name of the installer executable
outFile "${APPSHORTNAME}-inst.exe"

#...Not certain about this one
!include LogicLib.nsh

#Defines installation pages - these are known to NSIS
#Shows the license
Page license
#Allows user to pick install path
Page directory
#Installs the files
Page instfiles

#A macro to verify that administrator rights have been acquired
!macro VerifyUserIsAdmin
UserInfo::GetAccountType
pop $0
${If} $0 != "admin" ;Require admin rights on NT4+
        messageBox mb_iconstop "Administrator rights required!"
        setErrorLevel 740 ;ERROR_ELEVATION_REQUIRED
        quit
${EndIf}
!macroend

#This ensures the administrator check is performed at startup?
function .onInit
	setShellVarContext all
	!insertmacro VerifyUserIsAdmin
functionEnd

# Files for the install directory - to build the installer, these should be in the same directory as the install script (this file)
section "install"
    setOutPath $INSTDIR
	
	#Create directories
	
	#Logfiles
	CreateDirectory $INSTDIR\logs
	
	#Docs
	CreateDirectory $INSTDIR\docs
    
	#Config files
	CreateDirectory $INSTDIR\cfg
	
	#Resources
	CreateDirectory $INSTDIR\res
	
	# Files added here should be removed by the uninstaller (see section "uninstall")
    file /r ..\dist\*.*
	
	#Copy the license file to the docs directory
	file /oname=docs\LICENSE.md ..\LICENSE.md
	file /oname=docs\README.md ..\README.md

	
	# Add any other files for the install directory (license files, app data, etc) here
    
    #This creates a shortcut to the executable on the desktop - the second set of options in quotes are for command-line arguments
	CreateShortcut "$desktop\pyApp.lnk" "$instdir\pyCli.exe" 
 
sectionEnd