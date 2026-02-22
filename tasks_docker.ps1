param(
  [Parameter(Position=0)]
  [ValidateSet("up","down","logs","ingest","batch","aggregate","load-db","run","partitions","help")]
  [string]$Task = "help",

  [int]$Limit = 0,
  [switch]$Force,
  [string]$Partition = ""
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

function Batch {
  $args = @("python","run_batch.py")
  if ($Limit -gt 0) {
    $args += @("--limit",$Limit)
  }

  Write-Host "[INFO] Running processing batch in Docker: $($args -join ' ')"
  docker compose --profile batch run --rm processing @args
}

function Aggregate {
  $args = @("python","run_aggregate.py")
  if ($Force) {
    $args += "--force"
  }
  if ($Partition -ne "") {
    $args += @("--partition",$Partition)
  }

  Write-Host "[INFO] Running aggregation in Docker: $($args -join ' ')"
  docker compose --profile batch run --rm aggregation @args
}

function Partitions {
  docker compose --profile batch run --rm aggregation python run_aggregate.py --list-partitions
}

function LoadDb {
  $args = @("python","run_load_db.py")
  Write-Host "[INFO] Loading aggregated results into Postgres (Docker): $($args -join ' ')"
  docker compose --profile batch --profile analytics run --rm processing @args
}

function Help {
  Write-Host ""
  Write-Host "Usage (Docker):"
  Write-Host "  .\tasks_docker.ps1 up                 # start ingestion (background)"
  Write-Host "  .\tasks_docker.ps1 logs               # follow ingestion logs"
  Write-Host "  .\tasks_docker.ps1 ingest             # show Swagger URL"
  Write-Host "  .\tasks_docker.ps1 batch [-Limit 50]  # run processing batch"
  Write-Host "  .\tasks_docker.ps1 aggregate [-Force] [-Partition 'date=YYYY-MM-DD/hour=HH']"
  Write-Host "  .\tasks_docker.ps1 run                # batch + aggregation"
  Write-Host "  .\tasks_docker.ps1 partitions         # list processed partitions"
  Write-Host "  .\tasks_docker.ps1 down               # stop everything"
  Write-Host ""
}

switch ($Task) {
  "up" { Up }
  "down" { Down }
  "logs" { Logs }
  "ingest" { IngestInfo }
  "batch" { Batch }
  "aggregate" { Aggregate }
  "load-db" { LoadDb }
  "run" {
    Write-Host "[INFO] Running batch + aggregation (Docker)"
    docker compose --profile batch run --rm processing python run_batch.py
    docker compose --profile batch run --rm aggregation python run_aggregate.py
  }
  "partitions" { Partitions }
  default { Help }
}