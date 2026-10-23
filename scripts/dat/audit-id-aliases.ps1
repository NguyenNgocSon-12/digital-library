param(
    [string[]]$Containers = @('dl_redis','dl_dat_acceptance_20261022203530_82c03582','dl_dat_review_20261022204608'),
    [Parameter(Mandatory=$true)][string]$Output
)
$ErrorActionPreference='Stop'
if (Test-Path -LiteralPath $Output) { throw 'Choose a new output file; existing evidence is preserved.' }
function Read-RedisJson([string]$Container,[int]$Database,[string[]]$Command) {
    $raw = & docker exec $Container redis-cli -n $Database --json @Command
    if ($LASTEXITCODE -ne 0) { throw "Redis read failed: $Container db$Database" }
    return ,($raw | ConvertFrom-Json -NoEnumerate)
}
$rows = [Collections.Generic.List[object]]::new()
foreach ($container in $Containers) {
    if ($container -notmatch '^dl_(redis|dat_(acceptance|review)_[a-z0-9_]+)$') { throw 'Only explicitly selected digital-library Redis containers are allowed.' }
    for ($db=0; $db -lt 16; $db++) {
        $keys=[Collections.Generic.HashSet[string]]::new()
        $cursor='0'
        do {
            $page=Read-RedisJson $container $db @('SCAN',$cursor,'COUNT','200')
            $cursor=[string]$page[0]
            foreach($key in $page[1]) {
                if($key -match '(^|:)progress:[^:]+:[^:]+$' -or $key -match '(^|:)ranking:books$') { [void]$keys.Add($key) }
            }
        } while($cursor -ne '0')
        foreach($key in ($keys | Sort-Object)) {
            $type=Read-RedisJson $container $db @('TYPE',$key)
            if($key -match '^(.*progress:)([^:]+):([^:]+)$') {
                $prefix=$Matches[1]; $user=$Matches[2]; $book=$Matches[3]
                $valid=$user -cmatch '^[a-fA-F0-9]{24}$' -and $book -cmatch '^[a-fA-F0-9]{24}$'
                $canonical=if($valid){$prefix+$user.ToLowerInvariant()+':'+$book.ToLowerInvariant()}else{$null}
                $fields=if($type -eq 'hash'){Read-RedisJson $container $db @('HGETALL',$key)}else{$null}
                $rows.Add([ordered]@{container=$container;database=$db;kind='progress';key=$key;type=$type;validIds=$valid;canonicalKey=$canonical;isAlias=($valid -and $key -cne $canonical);fields=$fields})
            } elseif($type -eq 'zset') {
                $members=Read-RedisJson $container $db @('ZRANGE',$key,'0','-1','WITHSCORES')
                foreach($pair in $members) {
                    $member=[string]$pair[0]; $valid=$member -cmatch '^[a-fA-F0-9]{24}$'
                    $canonical=if($valid){$member.ToLowerInvariant()}else{$null}
                    $rows.Add([ordered]@{container=$container;database=$db;kind='ranking';key=$key;member=$member;score=$pair[1];validIds=$valid;canonicalMember=$canonical;isAlias=($valid -and $member -cne $canonical)})
                }
            }
        }
    }
}
$parent=Split-Path -Parent ([IO.Path]::GetFullPath($Output))
[void][IO.Directory]::CreateDirectory($parent)
$progressGroups=@($rows | Where-Object {$_.kind -eq 'progress' -and $_.validIds} | Group-Object -Property { "$($_.container)|$($_.database)|$($_.canonicalKey)" } | Where-Object Count -gt 1 | ForEach-Object { @{identity=$_.Name;count=$_.Count;keys=@($_.Group|ForEach-Object{$_.key})} })
$rankingGroups=@($rows | Where-Object {$_.kind -eq 'ranking' -and $_.validIds} | Group-Object -Property { "$($_.container)|$($_.database)|$($_.key)|$($_.canonicalMember)" } | Where-Object Count -gt 1 | ForEach-Object { @{identity=$_.Name;count=$_.Count;members=@($_.Group|ForEach-Object{$_.member});scores=@($_.Group|ForEach-Object{$_.score})} })
$report=@{time=(Get-Date).ToString('o');readOnly=$true;scope=@{containers=$Containers;databases='0..15';keys='progress:* and *:progress:*; ranking:books and *:ranking:books; no session values read'};aliasRows=@($rows|Where-Object isAlias -eq $true).Count;progressConflicts=$progressGroups;rankingConflicts=$rankingGroups;rows=$rows.ToArray()}
[IO.File]::WriteAllText([IO.Path]::GetFullPath($Output),($report|ConvertTo-Json -Depth 12))
Write-Output "Read-only audit: $($rows.Count) rows, $($report.aliasRows) alias rows, $($progressGroups.Count) progress conflicts, $($rankingGroups.Count) ranking conflicts. $Output"
