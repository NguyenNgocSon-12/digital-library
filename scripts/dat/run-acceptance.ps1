param(
    [string]$JavaHome = $env:JAVA_HOME,
    [string]$MongoUri = 'mongodb://admin:admin123@localhost:27017/?authSource=admin',
    [string]$Output,
    [string]$TestSelector = 'DatRedisIntegrationTest',
    [switch]$ReviewTests
)
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path "$PSScriptRoot/../..").Path
if (-not (Test-Path -LiteralPath "$JavaHome/bin/java.exe")) { throw 'Pass -JavaHome pointing to an existing JDK.' }
$runId = (Get-Date -Format 'yyyyMMddHHmmss') + '_' + ([guid]::NewGuid().ToString('N').Substring(0,8))
$container = 'dl_dat_acceptance_' + $runId.ToLowerInvariant()
$mongoDatabase = 'digital_library_dat_acceptance_' + $runId
if (-not $Output) { $Output = "$repoRoot/docs/dat/evidence/acceptance/$runId" }
$outputPath = [IO.Path]::GetFullPath($Output)
if (Test-Path -LiteralPath $outputPath) { throw 'Use a new output directory to preserve prior evidence.' }
New-Item -ItemType Directory -Path $outputPath | Out-Null
# A new Redis instance avoids clearing any existing DB or exhausting numbered logical DBs.
& docker run -d --name $container --label 'vn.edu.huit.dat.acceptance=true' -p '127.0.0.1::6379' redis:7-alpine redis-server --appendonly yes *> (Join-Path $outputPath 'docker-start.log')
if ($LASTEXITCODE -ne 0) { throw 'Could not create dedicated acceptance Redis. Existing data was not cleared.' }
$boundPort = (& docker inspect $container --format '{{(index (index .NetworkSettings.Ports "6379/tcp") 0).HostPort}}').Trim()
if ($LASTEXITCODE -ne 0 -or $boundPort -notmatch '^\d+$') { throw 'Could not read dedicated Redis port.' }
$uri = [UriBuilder]$MongoUri
$uri.Path = $mongoDatabase
$settings = @{
    JAVA_HOME = $JavaHome
    MONGO_URI = $uri.Uri.AbsoluteUri
    REDIS_URL = "redis://localhost:$boundPort/0"
    DAT_INTEGRATION_TESTS = 'true'
    DAT_ACCEPTANCE_OUTPUT = $outputPath
    DAT_REVIEW_TESTS = $(if ($ReviewTests) { 'true' } else { 'false' })
}
$metadata = @{
    time = (Get-Date).ToString('o')
    baseCommit = (& git -C $repoRoot rev-parse HEAD).Trim()
    mongoDatabase = $mongoDatabase
    redisContainer = $container
    redisEndpoint = "localhost:$boundPort/0"
    sourceSha256 = (Get-FileHash -Algorithm SHA256 "$repoRoot/backend/src/test/java/vn/edu/huit/digitallibrary/reading/DatRedisIntegrationTest.java").Hash
    command = "mvnw.cmd -B -Dtest=$TestSelector test"
    dataPolicy = 'Fresh Mongo database and dedicated Redis container; preserve all evidence and data, no flush'
}
$metadata | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $outputPath 'environment.json')
Get-ChildItem "$repoRoot/backend/src/main/java" -Recurse -Filter *.java | ForEach-Object {
    @{path=$_.FullName.Substring($repoRoot.Length+1).Replace('\','/');sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash}
} | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath (Join-Path $outputPath 'production-checksums.json')
$previous = @{}
foreach ($key in $settings.Keys) { $previous[$key] = [Environment]::GetEnvironmentVariable($key,'Process') }
try {
    foreach ($key in $settings.Keys) { [Environment]::SetEnvironmentVariable($key,$settings[$key],'Process') }
    Push-Location "$repoRoot/backend"
    try {
        & .\mvnw.cmd -B "-Dtest=$TestSelector" test *> (Join-Path $outputPath 'test.log')
        $testExit = $LASTEXITCODE
        Get-Content -LiteralPath (Join-Path $outputPath 'test.log') -Tail 16
        if ($testExit -ne 0) { throw "Acceptance failed (exit $testExit); container/data kept for diagnosis." }
        Write-Output "Evidence: $outputPath"
        Write-Output "Redis preserved: $container (localhost:$boundPort); Mongo database: $mongoDatabase"
    } finally { Pop-Location }
} finally {
    foreach ($key in $previous.Keys) { [Environment]::SetEnvironmentVariable($key,$previous[$key],'Process') }
}
