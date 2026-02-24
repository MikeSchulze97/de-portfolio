param(
  [Parameter(Position=0)]
  [ValidateSet("up","down","logs","ingest","run","generator","help")]
  [string]$Task = "help"
)

$ErrorActionPreference = "Stop"

function Up {
  Write-Host "[INFO] Starting ingestion (background) on http://localhost:8000"
  docker compose up -d ingestion
}

function Down {
  Write-Host "[INFO] Stopping containers"
  docker compose down
}

function Logs {
  docker compose logs -f ingestion
}

function IngestInfo {
  Write-Host "[INFO] Open Swagger UI:"
  Write-Host "  http://localhost:8000/docs"
}

function RunSpark {
  Write-Host "[INFO] Running pipeline (Spark): processing + aggregation"
  Write-Host "[INFO] Running Spark batch processing"
  docker compose --profile spark run --rm spark-processing

  Write-Host "[INFO] Running Spark aggregation"
  docker compose --profile spark run --rm spark-aggregation
}

function Generator {
  Write-Host "[INFO] Running event generator (CSV -> ingestion). Stop with CTRL+C."
  docker compose --profile generator run --rm event-generator
}

function Help {
  Write-Host ""
  Write-Host "Usage (Docker):"
  Write-Host "  .\tasks_docker.ps1 up        # start ingestion (background)"
  Write-Host "  .\tasks_docker.ps1 logs      # follow ingestion logs"
  Write-Host "  .\tasks_docker.ps1 ingest    # show Swagger URL"
  Write-Host "  .\tasks_docker.ps1 run       # run Spark processing + Spark aggregation"
  Write-Host "  .\tasks_docker.ps1 generator # run CSV event generator (optional demo, stop with CTRL+C)"
  Write-Host "  .\tasks_docker.ps1 down      # stop everything"
  Write-Host ""
}

switch ($Task) {
  "up" { Up }
  "down" { Down }
  "logs" { Logs }
  "ingest" { IngestInfo }
  "run" { RunSpark }
  "generator" { Generator }
  default { Help }
}