param(
    [ValidateSet('seed','benchmark','verify')][string]$Action = 'seed',
    [string]$JavaHome = $env:JAVA_HOME,
    [string]$MongoUri = 'mongodb://admin:admin123@localhost:27017/?authSource=admin',
    [string]$RedisUrl = 'redis://localhost:6379/0',
    [string]$Database = 'digital_library_dat_fixture_v1',
    [string]$Namespace = 'dat-fixture:v1:',
    [string]$Manifest,
    [int]$Warmup = 200,
    [int]$Runs = 1000,
    [string]$Output = "$PSScriptRoot/../../docs/dat/evidence/fixture"
)
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path "$PSScriptRoot/../..").Path
$settings = @{
    JAVA_HOME = $JavaHome
    DAT_FIXTURE_ACTION = $Action
    DAT_FIXTURE_MONGO_URI = $MongoUri
    DAT_FIXTURE_REDIS_URL = $RedisUrl
    DAT_FIXTURE_DATABASE = $Database
    DAT_FIXTURE_NAMESPACE = $Namespace
    DAT_FIXTURE_MANIFEST = $(if ($Manifest) { (Resolve-Path -LiteralPath $Manifest).Path } else { '' })
    DAT_FIXTURE_OUTPUT = [IO.Path]::GetFullPath($Output)
    DAT_BENCH_WARMUP = [string]$Warmup
    DAT_BENCH_RUNS = [string]$Runs
}
$previous = @{}
foreach ($key in $settings.Keys) { $previous[$key] = [Environment]::GetEnvironmentVariable($key, 'Process') }
try {
    foreach ($key in $settings.Keys) { [Environment]::SetEnvironmentVariable($key, $settings[$key], 'Process') }
    if (-not (Test-Path -LiteralPath "$JavaHome/bin/java.exe")) { throw 'Pass -JavaHome pointing to an existing JDK.' }
    Push-Location "$repoRoot/backend"
    try {
        & .\mvnw.cmd -B '-Dtest=DatFixtureToolTest' test
        if ($LASTEXITCODE -ne 0) { throw "Fixture tool failed (exit $LASTEXITCODE). Review the log; do not clear databases." }
        $metadata = @{
            time = (Get-Date).ToString('o')
            action = $Action
            cpu = @(Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors)
            totalPhysicalMemory = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory
            sourceSha256 = (Get-FileHash -Algorithm SHA256 "$repoRoot/backend/src/test/java/vn/edu/huit/digitallibrary/reading/DatFixtureToolTest.java").Hash
        }
        $metadata | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $settings.DAT_FIXTURE_OUTPUT 'run-environment.json')
    } finally { Pop-Location }
} finally {
    foreach ($key in $previous.Keys) { [Environment]::SetEnvironmentVariable($key, $previous[$key], 'Process') }
}
