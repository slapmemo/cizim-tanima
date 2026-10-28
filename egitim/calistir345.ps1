# 345 sınıf: veri hazırlandıktan sonra yarım çizimler, üç model, değerlendirme ve oyun simülasyonu.
# Kullanım (cizim-tanima/ içinde): powershell -File egitim\calistir345.ps1
# "Stop" değil: PowerShell 5.1'de yönlendirilen stderr satırları (uyarılar) betiği durdurur; başarı çıkış koduyla denetlenir
$ErrorActionPreference = "Continue"
$env:SINIF_SETI = "345"
$py = ".\.venv\Scripts\python.exe"
function adim($ad, $komut) {
    Write-Output "$(Get-Date -Format HH:mm) basladi: $ad"
    & $py @komut *> "deneyler\$ad.log"
    if ($LASTEXITCODE -ne 0) { throw "$ad basarisiz (deneyler\$ad.log)" }
    Write-Output "$(Get-Date -Format HH:mm) bitti: $ad"
}
adim "s345_kismi_hazirla" @("egitim\kismi_hazirla.py")
adim "s345_m1" @("egitim\egit.py", "--ad", "s345_m1", "--model", "m1", "--epoch", "10")
adim "s345_m3" @("egitim\egit.py", "--ad", "s345_m3", "--model", "m3", "--epoch", "15", "--artirma")
adim "s345_m3_kismi" @("egitim\egit.py", "--ad", "s345_m3_kismi", "--model", "m3", "--epoch", "15", "--artirma", "--kismi", "0.5")
adim "s345_degerlendir" @("-W", "ignore", "egitim\degerlendir.py")
adim "s345_oyun_simulasyonu" @("egitim\oyun_simulasyonu.py")
Write-Output "hepsi bitti"
