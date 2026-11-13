param(
    [string]$InputPath,
    [string]$OutputPath = "assets/demo.gif",
    [int]$Fps = 15,
    [int]$Width = 900
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    throw "ffmpeg nao encontrado no PATH. Reinicie o terminal apos instalar ou adicione o ffmpeg ao PATH."
}

$videoExtensions = @(".mp4", ".mov", ".mkv", ".avi", ".webm")

if (-not $InputPath) {
    if (-not (Test-Path "assets")) {
        throw "Pasta 'assets' nao encontrada."
    }

    $latestVideo = Get-ChildItem -Path "assets" -File |
        Where-Object { $videoExtensions -contains $_.Extension.ToLowerInvariant() } |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if (-not $latestVideo) {
        throw "Nenhum arquivo de video encontrado em 'assets/' (extensoes suportadas: $($videoExtensions -join ', '))."
    }

    $InputPath = $latestVideo.FullName
}

if (-not (Test-Path $InputPath)) {
    throw "Arquivo de entrada nao encontrado: $InputPath"
}

$outputDir = Split-Path -Path $OutputPath -Parent
if ($outputDir -and -not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

$paletteFile = [System.IO.Path]::ChangeExtension([System.IO.Path]::GetTempFileName(), ".png")
$filters = "fps=$Fps,scale=${Width}:-1:flags=lanczos"

try {
    Write-Host "Gerando paleta otimizada a partir de: $InputPath"
    & ffmpeg -y -i $InputPath -vf "$filters,palettegen=stats_mode=diff" $paletteFile
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao gerar paleta com ffmpeg (codigo $LASTEXITCODE)."
    }

    Write-Host "Convertendo para GIF: $OutputPath"
    & ffmpeg -y -i $InputPath -i $paletteFile -lavfi "$filters [x]; [x][1:v] paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" -loop 0 $OutputPath
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao gerar GIF com ffmpeg (codigo $LASTEXITCODE)."
    }

    $sizeMb = [math]::Round((Get-Item $OutputPath).Length / 1MB, 2)
    Write-Host "GIF gerado com sucesso: $OutputPath ($sizeMb MB)"
    if ($sizeMb -gt 10) {
        Write-Warning "O GIF tem $sizeMb MB (acima de 10 MB). Considere reduzir -Width ou -Fps para melhor carregamento no GitHub."
    }
}
finally {
    if (Test-Path $paletteFile) {
        Remove-Item $paletteFile -Force -ErrorAction SilentlyContinue
    }
}
