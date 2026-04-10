@echo off
echo Iniciando o Motor de Dados do TCC...

cd "C:\Users\lucas\OneDrive\Documentos\vscode\tcc"
call .venv\Scripts\activate
python automacao\rotina_semanal.py
call deactivate

echo Extracao concluida!
pause