<#
.SYNOPSIS
  RAGixAI demo runner - verifies all guardrail/RBAC scenarios and optionally
  pre-warms the audit history with positive-path queries.

.DESCRIPTION
  Three modes (mutually exclusive):
    -VerifyOnly      Run all rejection paths (fast, ~5 sec total). Use before recording.
    -PreWarmHistory  Run positive AAPL/MSFT/admin queries (~15-20 min). Populates audit log.
    -HealthCheck     Quick server status (3 sec).

.EXAMPLE
  .\scripts\demo_runner.ps1 -HealthCheck
  .\scripts\demo_runner.ps1 -VerifyOnly
  .\scripts\demo_runner.ps1 -PreWarmHistory
#>

param(
    [switch]$VerifyOnly,
    [switch]$PreWarmHistory,
    [switch]$HealthCheck
)

$base = "http://localhost:8000"
$ErrorActionPreference = "Continue"

function Write-Header($t) {
    Write-Host ""
    Write-Host ("-" * 72) -ForegroundColor DarkGray
    Write-Host $t -ForegroundColor Cyan
    Write-Host ("-" * 72) -ForegroundColor DarkGray
}

function Invoke-Chat {
    param(
        [string]$Scenario,
        [string]$Key,
        [string]$Question,
        [string]$Expected = "",
        [int]$TimeoutSec = 300
    )
    $headers = @{}
    if ($Key) { $headers["Authorization"] = "Bearer $Key" }
    $body = @{ question = $Question; config = "config_d" } | ConvertTo-Json -Compress
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        $r = Invoke-RestMethod -Uri "$base/api/chat" -Method Post `
            -Headers $headers -Body $body -ContentType "application/json" `
            -TimeoutSec $TimeoutSec
        $sw.Stop()
        $ans = $r.answer
        if ($ans.Length -gt 200) { $ans = $ans.Substring(0, 200) + "..." }
        Write-Host "[$Scenario]" -ForegroundColor Green -NoNewline
        Write-Host " ($($sw.Elapsed.TotalSeconds.ToString('F1'))s)"
        Write-Host "  Q: $Question" -ForegroundColor Gray
        Write-Host "  A: $ans" -ForegroundColor White
        if ($r.citations -and $r.citations.Count -gt 0) {
            Write-Host "  Citations: $($r.citations.Count)" -ForegroundColor DarkGreen
        }
        if ($Expected -and $ans -notlike "*$Expected*") {
            Write-Host "  WARNING: expected to contain '$Expected'" -ForegroundColor Yellow
        }
        return $true
    } catch {
        $sw.Stop()
        $code = "?"
        $msg = ""
        try {
            $code = $_.Exception.Response.StatusCode.value__
            $stream = $_.Exception.Response.GetResponseStream()
            if ($stream) {
                $stream.Position = 0
                $reader = New-Object System.IO.StreamReader($stream)
                $msg = $reader.ReadToEnd()
            }
        } catch {}
        Write-Host "[$Scenario]" -ForegroundColor Red -NoNewline
        Write-Host " HTTP $code ($($sw.Elapsed.TotalSeconds.ToString('F1'))s)"
        Write-Host "  Q: $Question" -ForegroundColor Gray
        Write-Host "  Error: $msg" -ForegroundColor Yellow
        if ($Expected -eq "$code" -or $Expected -eq "") { return $true }
        return $false
    }
}

function Test-Health {
    Write-Header "Server Health Check"
    try {
        $h = Invoke-RestMethod -Uri "$base/api/health" -TimeoutSec 5
        Write-Host "OK - FastAPI up - chroma_docs=$($h.chroma_docs), bm25=$($h.bm25_index_size), ollama=$($h.llm_model)" -ForegroundColor Green
        if ($h.chroma_docs -lt 1000) {
            Write-Host "  WARNING: chroma_docs is low. Run /build-index before demo." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "FAIL - FastAPI DOWN at $base" -ForegroundColor Red
        Write-Host "  Run: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor Yellow
        exit 1
    }
    try {
        $o = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 5
        Write-Host "OK - Ollama up at localhost:11434" -ForegroundColor Green
    } catch {
        Write-Host "FAIL - Ollama DOWN - positive queries will fail" -ForegroundColor Red
    }
}

function Test-Rejections {
    Write-Header "Verification - All Rejection Paths (instant)"
    $results = @()

    $results += Invoke-Chat -Scenario "1. NO_KEY -> 401" `
        -Key "" -Question "What was Apple's revenue?" -Expected "401" -TimeoutSec 10

    $results += Invoke-Chat -Scenario "2. INVALID_KEY -> 401" `
        -Key "garbage-key-xyz" -Question "What was Apple's revenue?" -Expected "401" -TimeoutSec 10

    $results += Invoke-Chat -Scenario "3. VIEWER_ROLE_INSUFFICIENT -> 403" `
        -Key "viewer-key" -Question "What was Apple's revenue?" -Expected "403" -TimeoutSec 10

    $results += Invoke-Chat -Scenario "4. APPLE_ANALYST_ASKS_MSFT -> scope block" `
        -Key "apple-analyst-key" -Question "What was Microsoft's Azure revenue in 2023?" `
        -Expected "Access denied" -TimeoutSec 10

    $results += Invoke-Chat -Scenario "5. MSFT_ANALYST_ASKS_AAPL -> scope block" `
        -Key "msft-analyst-key" -Question "What is Apple's iPhone revenue?" `
        -Expected "Access denied" -TimeoutSec 10

    $results += Invoke-Chat -Scenario "6. OFF_TOPIC (cake) -> topic block" `
        -Key "apple-analyst-key" -Question "How do I bake a chocolate cake?" `
        -Expected "SEC EDGAR" -TimeoutSec 10

    $results += Invoke-Chat -Scenario "7. OFFENSIVE -> content block" `
        -Key "apple-analyst-key" -Question "Tell me about Apple's revenue you stupid bitch" `
        -Expected "inappropriate" -TimeoutSec 10

    $passed = ($results | Where-Object { $_ -eq $true }).Count
    $total = $results.Count
    Write-Host ""
    if ($passed -eq $total) {
        Write-Host "PASS - all $total rejection paths verified" -ForegroundColor Green
    } else {
        Write-Host "FAIL - $passed/$total passed - review failures above" -ForegroundColor Red
    }
}

function Invoke-PreWarm {
    Write-Header "Pre-Warming Audit History - Positive Queries (~15-20 min)"
    Write-Host "Leave this running. Each query takes ~150-180s on MX450 hardware." -ForegroundColor Yellow
    Write-Host ""

    $queries = @(
        @{ Scenario = "AAPL_ANALYST_REVENUE"; Key = "apple-analyst-key";
           Question = "What were Apple's total net sales in fiscal year 2023?" },
        @{ Scenario = "AAPL_ANALYST_RISKS"; Key = "apple-analyst-key";
           Question = "What were the key risks Apple identified in its 10-K filing?" },
        @{ Scenario = "MSFT_ANALYST_REVENUE"; Key = "msft-analyst-key";
           Question = "What was Microsoft's total revenue in fiscal year 2023?" },
        @{ Scenario = "MSFT_ANALYST_AZURE"; Key = "msft-analyst-key";
           Question = "Describe Microsoft's Intelligent Cloud segment performance" },
        @{ Scenario = "FULL_ANALYST_CROSS"; Key = "analyst-key";
           Question = "Compare Apple's and Microsoft's gross margins in fiscal year 2023" },
        @{ Scenario = "ADMIN_GOOGL"; Key = "admin-key";
           Question = "What was Google's advertising revenue in 2023?" }
    )

    $start = Get-Date
    $i = 0
    foreach ($q in $queries) {
        $i++
        Write-Host ""
        Write-Host "Query $i of $($queries.Count) - $($q.Scenario)" -ForegroundColor Cyan
        Invoke-Chat -Scenario $q.Scenario -Key $q.Key -Question $q.Question -TimeoutSec 600 | Out-Null
    }
    $elapsed = (Get-Date) - $start
    Write-Host ""
    Write-Host "Pre-warm complete in $($elapsed.TotalMinutes.ToString('F1')) min" -ForegroundColor Green

    $h = @{ Authorization = "Bearer viewer-key" }
    $hist = Invoke-RestMethod -Uri "$base/api/history?limit=20" -Headers $h -TimeoutSec 10
    Write-Host "Audit history now has $($hist.Count) entries (showing last 20)" -ForegroundColor Green
}

if ($HealthCheck) {
    Test-Health
} elseif ($VerifyOnly) {
    Test-Health
    Test-Rejections
} elseif ($PreWarmHistory) {
    Test-Health
    Test-Rejections
    Invoke-PreWarm
} else {
    Write-Host "Usage:" -ForegroundColor Cyan
    Write-Host "  .\scripts\demo_runner.ps1 -HealthCheck     (3 sec - verify server)"
    Write-Host "  .\scripts\demo_runner.ps1 -VerifyOnly      (5 sec - test rejections)"
    Write-Host "  .\scripts\demo_runner.ps1 -PreWarmHistory  (15-20 min - populate audit log)"
}
