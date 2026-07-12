# Generate a cryptographically strong JWT secret for HS256.
# Copy the output into your deployment .env as JWT_SECRET=...

$bytes = New-Object byte[] 32
[System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
$secret = [Convert]::ToBase64String($bytes)

Write-Host ""
Write-Host "Add this to your .env file (do NOT commit .env):"
Write-Host ""
Write-Host "JWT_SECRET=$secret"
Write-Host ""
