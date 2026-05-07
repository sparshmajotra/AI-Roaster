$ErrorActionPreference = "Stop"

function Assert-HttpOk {
    param(
        [string]$Name,
        [string]$Url
    )

    $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 10
    if ($response.StatusCode -lt 200 -or $response.StatusCode -ge 400) {
        throw "$Name returned HTTP $($response.StatusCode)"
    }
    Write-Host "$Name OK ($($response.StatusCode))"
}

Assert-HttpOk -Name "Frontend" -Url "http://127.0.0.1:3000"
Assert-HttpOk -Name "Backend docs" -Url "http://127.0.0.1:8000/api/docs/"

$demo = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/v1/accounts/users/demo_token/"
if (!$demo.access) {
    throw "Demo token endpoint did not return an access token."
}
Write-Host "Demo login OK"

$headers = @{ Authorization = "Bearer $($demo.access)" }
$body = @{
    category = "Roast My Bio"
    roast_style = "Brutal Roast"
    visibility = "public"
    text_content = "Testing Roastly from the smoke test script."
} | ConvertTo-Json

$post = Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8000/api/v1/roasts/posts/" `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $body

if ($post.status -ne "ready" -or !$post.ai_roast) {
    throw "Roast creation failed. Status: $($post.status)"
}

$lineCount = ($post.ai_roast -split "`n" | Where-Object { $_.Trim() }).Count
if ($lineCount -lt 5) {
    throw "Roast should have at least 5 lines, got $lineCount."
}

Write-Host "Roast creation OK"
Write-Host "Lines: $lineCount"
Write-Host "Score: $($post.ai_score)"
Write-Host "Aura:  $($post.aura)"
Write-Host "Roast: $($post.ai_roast)"
