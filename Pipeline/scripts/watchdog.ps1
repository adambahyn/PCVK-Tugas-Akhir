# Watchdog: jaga pipeline tetap jalan walau proses utama mati / laptop restart.
# Aturan:
#  - kalau Pipeline/outputs/metrics.json sudah ada -> selesai, keluar
#  - kalau proses nbconvert masih hidup -> tunggu
#  - kalau tidak ada proses -> jalankan ulang notebook (deteksi akan dilatih ulang dari awal)
$ErrorActionPreference = "Continue"
$root = "C:\Kuliah\Tingkat 3\PCVK\Project"
$nb = Join-Path $root "Pipeline\PCVK_Pipeline_Deteksi_Klasifikasi_Impaksi.ipynb"
$metrics = Join-Path $root "Pipeline\outputs\metrics.json"
$log = Join-Path $root "Pipeline\outputs\nbconvert.log"
$py = Join-Path $root ".venv\Scripts\python.exe"

while ($true) {
    if (Test-Path $metrics) {
        Add-Content $log ("[{0}] watchdog: metrics.json ada -> selesai" -f (Get-Date -Format s))
        break
    }
    $running = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
        Where-Object { $_.CommandLine -like "*nbconvert*" } |
        Select-Object -First 1
    if (-not $running) {
        Add-Content $log ("[{0}] watchdog: notebook tidak berjalan -> mulai ulang" -f (Get-Date -Format s))
        Push-Location $root
        & $py -m jupyter nbconvert --to notebook --execute --inplace `
            --ExecutePreprocessor.timeout=7200 --ExecutePreprocessor.kernel_name=python3 $nb *>> $log
        Pop-Location
        Start-Sleep -Seconds 120
    } else {
        Start-Sleep -Seconds 60
    }
}
