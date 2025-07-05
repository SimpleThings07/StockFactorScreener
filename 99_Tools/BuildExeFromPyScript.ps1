<#
                                     Build script
                                     ----------------------------------
 Language              : PowerShell  5.1.19041.1682
 Filename              : BuildExeFromPyScript.ps1 
 Autor                 : Ivan Antunovic (IVANTUN)
 Description           : This script builds an executable from the source file 'ClangComplerCallSeqGenerator.py'

#>

<#

 $Log: BuildExeFromPyScript.ps1  $
 Revision 1.1 2023/03/30 20:15:48MESZ Antunovic, Ivan (019) (IVANTUN) 
 Initial revision
 Member added to project e:/MKS/Projekte/PEP_Tools/StartDelayTimeValidator/04_Tools/project.pj
 Revision 1.2 2022/11/23 14:09:43MEZ Antunovic, Ivan (019) (IVANTUN) 
 Added Exception Handler if "PyInstaller" command is not found.
 Revision 1.1 2022/10/21 14:47:48MESZ Antunovic, Ivan (019) (IVANTUN) 
 Initial revision
 Member added to project e:/MKS/Projekte/CPC_Multicore/05_Tools/DepAnalyzer/06_CreateCallScripts/Compiler_Call_Sequence_Generator/04_Tools/project.pj

#>

# Directory where the Script resides
$SCRIPT_DIR = (Get-Item .).FullName

# Base name of the python script to be built
$PY_SCRIPT_BASE_NAME = "StockFactorScreener"

# Directory where the sources of the Clang Compiler Script resides
$CLANG_COMPLER_SCRIPT_DIR = ((Get-Item .).Parent).FullName + "\01_Src"

# Directory where the executable of the Clang Compiler Script resides
$CLANG_COMPLER_SCRIPT_BUILD_DIR = ((Get-Item .).Parent).FullName + "\02_Bin"

# Program Successful Exit Code
$EXIT_CODE_SUCCESS = 0

# Argument list passed to the process
$ARG_LIST = @( "--onefile $CLANG_COMPLER_SCRIPT_DIR\$PY_SCRIPT_BASE_NAME.py" )

# Check if the "PyInstaller" command does NOT exist
if ( -Not ( Get-Command "pyinstaller" -errorAction SilentlyContinue ) )
{
    Write-Host "No 'PyInstaller' command found on this machine. Make sure you have 'PyInstaller.exe' installed and that it is added to the PATH." -ForegroundColor Red
    Write-Host "To install the 'PyInstaller.exe', run 'pip install pyinstaller' command in a terminal." -ForegroundColor Red
    Write-Host "Terminating the script." -ForegroundColor Red
    Exit (1)
}

# Start the Process
$buildExeProc = Start-Process -FilePath "pyinstaller" -ArgumentList $ARG_LIST -PassThru -NoNewWindow

# Wait for the process to terminate
$buildExeProc | Wait-Process

# If the EXE-Build Process has exited with the Successful Code
if ( $EXIT_CODE_SUCCESS -eq $buildExeProc.ExitCode )
{
    Write-Host "EXE-Build Process Run was successful. Exit Code: $($buildExeProc.ExitCode)" -ForegroundColor Green

    # If the EXE-File was generated
    if ( [System.IO.file]::Exists( "$SCRIPT_DIR\dist\$PY_SCRIPT_BASE_NAME.exe" ) )
    {
        Write-Host "Moving the EXE-File to $CLANG_COMPLER_SCRIPT_BUILD_DIR" -ForegroundColor Green

        # Move the newly generated EXE file into the '\02_Build' folder and force the replacemenet of the existing EXE file
        Move-Item -Path "$SCRIPT_DIR\dist\$PY_SCRIPT_BASE_NAME.exe" -Destination $CLANG_COMPLER_SCRIPT_BUILD_DIR -Force
    }
}
# If the EXE-Build Process has NOT exited with the Successful Code
else
{
    Write-Host "EXE-Build Process Run was NOT successful. Exit Code: $($buildExeProc.ExitCode)" -BackgroundColor Red
}


# ------------------------------------------------- File and Directory Cleanup ------------------------------------------------- #

# If the 'build' directory was generated
if ( Test-Path -Path "$SCRIPT_DIR\build" )
{
    # Remove the "\build" folder recursively
    Remove-Item -Path "$SCRIPT_DIR\build" -Force -Recurse
}

# If the 'dist' directory was generated
if ( Test-Path -Path "$SCRIPT_DIR\dist\" )
{
    # Remove the "\dist" folder recursively
    Remove-Item -Path "$SCRIPT_DIR\dist" -Force -Recurse
}

# If the 'ClangComplerCallSeqGenerator.spec' file was generated
if ( Test-Path -Path "$SCRIPT_DIR\$PY_SCRIPT_BASE_NAME.spec" )
{
    # Remove the 'ClangComplerCallSeqGenerator.spec' file
    Remove-Item "$SCRIPT_DIR\$PY_SCRIPT_BASE_NAME.spec" -Force
}
