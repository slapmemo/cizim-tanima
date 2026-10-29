# 345 sınıf: veri hazırlandıktan sonra yarım çizimler, üç model, değerlendirme ve oyun ölçümü.
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
adim "dogrulama_vuruslar" @("egitim\dogrulama_vuruslar.py")
adim "esdeger_aday" @("egitim\esdeger_aday.py")        # adaylar elle onaylanıp demo\public\model\esdeger.json'a yazılır
adim "oyun_kelimeleri" @("egitim\oyun_kelimeleri.py")
$env:SINIF_SETI = "50"                                  # olcum.py iki sekmeyi kendisi seçer (50 verisinin doğrulama vuruşları da gerekir)
adim "dogrulama_vuruslar50" @("egitim\dogrulama_vuruslar.py")
adim "olcum" @("egitim\olcum.py")
Write-Output "hepsi bitti"
