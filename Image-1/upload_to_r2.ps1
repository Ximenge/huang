$ErrorActionPreference = "Stop"

# Configuration
$remoteName = "small"
$baseRemotePath = "small"
$localPath = "C:\huang\Image-1"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "R2 Auto Upload Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function: Convert folder name (replace spaces with hyphens)
function Convert-FolderName {
    param(
        [string]$folderName
    )
    return $folderName -replace ' ', '-'
}

# Function: Check if remote directory exists (with space/hyphen conversion)
function Test-RemoteDirectoryExists {
    param(
        [string[]]$remoteDirs,
        [string]$targetDir
    )
    
    # Check exact match
    if ($remoteDirs -contains $targetDir) {
        return $true
    }
    
    # Check with space to hyphen conversion
    $convertedName = Convert-FolderName $targetDir
    if ($remoteDirs -contains $convertedName) {
        return $true
    }
    
    # Check with hyphen to space conversion
    $reversedName = $targetDir -replace '-', ' '
    if ($remoteDirs -contains $reversedName) {
        return $true
    }
    
    return $false
}

# Function: Get R2 remote directory list
function Get-RemoteDirectories {
    param(
        [string]$remotePath
    )
    
    Write-Host "Getting remote directory list: $remotePath..." -ForegroundColor Yellow
    
    try {
        $result = rclone lsd "$remoteName`:$remotePath" 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Warning: Cannot get remote directory list" -ForegroundColor Yellow
            return @()
        }
        
        $dirs = @()
        foreach ($line in $result) {
            if ($line -match '\s+(-?\d+)\s+\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+(-?\d+)\s+(.+)$') {
                $dirName = $matches[3].Trim()
                $dirs += $dirName
            }
        }
        
        return $dirs
    }
    catch {
        Write-Host "Error: Failed to get remote directory list - $_" -ForegroundColor Red
        return @()
    }
}

# Function: Check if local directory exists
function Test-LocalDirectory {
    param(
        [string]$dirPath
    )
    
    return Test-Path -Path $dirPath -PathType Container
}

# Function: Upload directory
function Upload-Directory {
    param(
        [string]$localDir,
        [string]$remoteDir
    )
    
    $localFullPath = Join-Path $localPath $localDir
    $remoteFullPath = "$baseRemotePath/$remoteDir"
    
    Write-Host ""
    Write-Host "----------------------------------------" -ForegroundColor Green
    Write-Host "Uploading: $localDir -> $remoteDir" -ForegroundColor Green
    Write-Host "----------------------------------------" -ForegroundColor Green
    
    try {
        $result = rclone copy $localFullPath "$remoteName`:$remoteFullPath" --progress
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Upload success: $localDir" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "[FAIL] Upload failed: $localDir" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "[ERROR] Upload exception: $localDir - $_" -ForegroundColor Red
        return $false
    }
}

# Main process
try {
    # Get existing remote directories
    Write-Host "Step 1: Checking R2 remote directories..." -ForegroundColor Cyan
    $remoteDirs = Get-RemoteDirectories $baseRemotePath
    Write-Host "Remote existing directories: $($remoteDirs -join ', ')" -ForegroundColor Gray
    Write-Host ""
    
    # Get all local subdirectories
    Write-Host "Step 2: Scanning local directories..." -ForegroundColor Cyan
    $localDirs = Get-ChildItem -Path $localPath -Directory | Where-Object { $_.Name -ne 'conversion_record.json' -and $_.Name -notlike '*.ps1' -and $_.Name -notlike '*.py' -and $_.Name -notlike '*.bat' }
    Write-Host "Found $($localDirs.Count) local directories" -ForegroundColor Gray
    Write-Host ""
    
    # Check and upload each folder
    $uploadCount = 0
    $skipCount = 0
    $failCount = 0
    
    foreach ($dir in $localDirs) {
        $localDirName = $dir.Name
        $remoteDirName = Convert-FolderName $localDirName
        
        Write-Host "Checking folder: $localDirName (remote name: $remoteDirName)" -ForegroundColor Cyan
        
        # Check if local directory exists
        $localFullPath = Join-Path $localPath $localDirName
        if (-not (Test-LocalDirectory $localFullPath)) {
            Write-Host "  [SKIP] Local directory not found: $localDirName" -ForegroundColor Yellow
            $skipCount++
            continue
        }
        
        # Check if remote directory already exists
        if (Test-RemoteDirectoryExists $remoteDirs $remoteDirName) {
            Write-Host "  [SKIP] Remote directory already exists: $remoteDirName" -ForegroundColor Yellow
            $skipCount++
            continue
        }
        
        # Upload directory
        $success = Upload-Directory $localDirName $remoteDirName
        if ($success) {
            $uploadCount++
        }
        else {
            $failCount++
        }
    }
    
    # Output summary
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Upload Complete!" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Successfully uploaded: $uploadCount folders" -ForegroundColor Green
    Write-Host "Skipped (already exists): $skipCount folders" -ForegroundColor Yellow
    Write-Host "Failed: $failCount folders" -ForegroundColor Red
    Write-Host ""
    
    # Display current remote directory status
    Write-Host "Current remote directory list:" -ForegroundColor Cyan
    $finalRemoteDirs = Get-RemoteDirectories $baseRemotePath
    foreach ($dir in $finalRemoteDirs) {
        Write-Host "  - $dir" -ForegroundColor Gray
    }
    
}
catch {
    Write-Host ""
    Write-Host "[ERROR] Script execution failed: $_" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')