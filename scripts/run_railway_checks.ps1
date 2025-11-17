# Script para verificar state del servicio Railway y ejecutar migraciones/collectstatic
# Guarda salida en run_output.txt en la carpeta actual

$outfile = "$PWD\run_output.txt"
"`n--- Railway checks: $(Get-Date) ---`n" | Out-File $outfile -Encoding utf8

function run-and-log($cmd) {
    "`n>>> $cmd`n" | Out-File $outfile -Append -Encoding utf8
    try {
        iex $cmd 2>&1 | Out-File $outfile -Append -Encoding utf8
    } catch {
        $_ | Out-File $outfile -Append -Encoding utf8
    }
}

# 1) railway version
run-and-log "railway -v"

# 2) comprobar DATABASE_URL en el contenedor
run-and-log 'railway run --service juguetesonline -- python -c "import os; print(\"DATABASE_URL=\", os.getenv(\"DATABASE_URL\"))"'

# 3) check Django and PyMySQL
run-and-log 'railway run --service juguetesonline -- python -m pip show Django'
run-and-log 'railway run --service juguetesonline -- python -m pip show PyMySQL'

# 4) migraciones
run-and-log 'railway run --service juguetesonline -- python -c "import sys; sys.path.insert(0,\'/app\'); from django.core.management import execute_from_command_line; execute_from_command_line([\'/app/manage.py\',\'migrate\',\'--noinput\'])"'

# 5) collectstatic
run-and-log 'railway run --service juguetesonline -- python -c "import sys; sys.path.insert(0,\'/app\'); from django.core.management import execute_from_command_line; execute_from_command_line([\'/app/manage.py\',\'collectstatic\',\'--noinput\'])"'

Write-Output "Done. Output saved to $outfile"
