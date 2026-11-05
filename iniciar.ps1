# Atalho opcional para Windows. Execute dentro da pasta do projeto.
# Yanuska Monalisa Antunes Yabiku - RM 571686.
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
python preparar.py
if ($LASTEXITCODE -ne 0) { throw 'Não foi possível criar a configuração.' }
docker compose up --build -d
if ($LASTEXITCODE -ne 0) { throw 'Abra o Docker Desktop e consulte o README.' }
Write-Host 'Aguarde a inicialização e abra http://127.0.0.1:5055'
Write-Host 'Para carregar exemplos: docker compose exec web python povoar_exemplos.py'
