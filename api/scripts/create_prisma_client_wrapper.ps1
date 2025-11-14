# Create a wrapper script for prisma-client-python
$scriptsPath = "C:\Users\Admin\AppData\Local\Programs\Python\Python312\Scripts"
$wrapperPath = Join-Path $scriptsPath "prisma-client-python.cmd"

$wrapperContent = "@echo off`npython -m prisma.cli %*"

try {
    Set-Content -Path $wrapperPath -Value $wrapperContent
    Write-Host "Created wrapper script at: $wrapperPath"
    Write-Host "Now try: prisma generate --schema prisma/schema.prisma"
} catch {
    Write-Host "Error creating wrapper: $($_.Exception.Message)"
}

