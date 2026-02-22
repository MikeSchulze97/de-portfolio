param(
  [Parameter(Position=0)]
  [ValidateSet("venv","ingestion","generator","batch","aggregate","partitions","cleanup","help")]
  [string]$Task = "help",

  [int]$Limit = 0,
  [switch]$Force,
  [string]$Partition = ""
)

$ErrorActionPreference = "Stop"

function Activate-Venv {
  if (-not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "[ERROR] venv not found in project root."
    exit 1
  }
  . .\venv\Scripts\Activate.ps1
  Write-Host "[OK] venv activated"
}

function Run-Ingestion {
  Activate-Venv
  Set-Location ".\services\ingestion"
  Write-Host "[INFO] Starting ingestion service on http://localhost:8001"
  uvicorn app:app --host 0.0.0.0 --port 8001
}

function Run-Generator {
  Activate-Venv
  Set-Location ".\services\event-generator"
  Write-Host "[INFO] Starting event generator (sends to ingestion)"
  python app.py
}

function Run-Batch {
  Activate-Venv
  Set-Location $PSScriptRoot

  if ($Limit -gt 0) {
    Write-Host "[INFO] Running batch with --limit $Limit"
    python .\services\processing\run_batch.py --limit $Limit
  } else {
    Write-Host "[INFO] Running batch"
    python .\services\processing\run_batch.py
  }
}

function Run-Aggregate {
  Activate-Venv
  Set-Location $PSScriptRoot

  $args = @()
  if ($Force) { $args += "--force" }
  if ($Partition -ne "") { $args += "--partition"; $args += $Partition }

  if ($args.Count -gt 0) {
    Write-Host "[INFO] Running aggregate with args: $($args -join ' ')"
    python .\services\processing\run_aggregate.py @args
  } else {
    Write-Host "[INFO] Running aggregate"
    python .\services\processing\run_aggregate.py
  }
}

function List-Partitions {
  Activate-Venv
  Set-Location $PSScriptRoot
  python .\services\processing\run_aggregate.py --list-partitions
}

function Run-Cleanup {
  Activate-Venv
  Set-Location $PSScriptRoot

  if (Test-Path ".\services\processing\tools\cleanup_checkpoint.py") {
    python .\services\processing\tools\cleanup_checkpoint.py
  } elseif (Test-Path ".\services\processing\cleanup_checkpoint.py") {
    python .\services\processing\cleanup_checkpoint.py
  } else {
    Write-Host "[ERROR] cleanup_checkpoint.py not found."
    exit 1
  }
}

function Show-Help {
  Write-Host ""
  Write-Host "Usage:"
  Write-Host "  .\tasks.ps1 partitions"
  Write-Host "  .\tasks.ps1 batch [-Limit 50]"
  Write-Host "  .\tasks.ps1 aggregate [-Force] [-Partition 'date=YYYY-MM-DD/hour=HH']"
  Write-Host "  .\tasks.ps1 cleanup"
  Write-Host ""
  Write-Host "Services (run in their own terminal):"
  Write-Host "  .\tasks.ps1 ingestion"
  Write-Host "  .\tasks.ps1 generator"
  Write-Host ""
}

switch ($Task) {
  "venv" { Activate-Venv }
  "ingestion" { Run-Ingestion }
  "generator" { Run-Generator }
  "batch" { Run-Batch }
  "aggregate" { Run-Aggregate }
  "partitions" { List-Partitions }
  "cleanup" { Run-Cleanup }
  default { Show-Help }
}
