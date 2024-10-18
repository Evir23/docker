from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import shutil
import os
from dock_redactor import process_documents

router = APIRouter()

# Путь для сохранения PDF-файлов
output_directory = "output_pdfs"
os.makedirs(output_directory, exist_ok=True)

# Путь для сохранения загруженных файлов (шаблонов и протоколов)
upload_directory = "uploaded_files"
os.makedirs(upload_directory, exist_ok=True)

templates = Jinja2Templates(directory='templates')


# Маршрут для обработки данных и передачи их в dock_redactor.py
@router.post("/process_data")
async def process_data(
    company_name: str = Form(...),
    template: UploadFile = File(...),
    group: str = Form(...),
    protocol: UploadFile = File(...)
):
    try:
        # Сохраняем протокол в папку для загруженных файлов
        protocol_path = os.path.join(upload_directory, protocol.filename)
        with open(protocol_path, "wb") as buffer:
            buffer.write(await protocol.read())  # Асинхронное чтение файла

        # Сохраняем шаблон в папку для загруженных файлов
        template_path = os.path.join(upload_directory, template.filename)
        with open(template_path, "wb") as buffer:
            buffer.write(await template.read())  # Асинхронное чтение файла

        # Передаем сохранённые пути к файлам для дальнейшей обработки
        process_documents(company_name, template_path, group, protocol_path, output_directory)

        return JSONResponse({"message": "Данные обработаны, PDF файлы созданы."})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# Маршрут для скачивания файлов
@router.get("/download_documents")
async def download_documents():
    # Путь к сгенерированным PDF-файлам
    pdf_files = [os.path.join(output_directory, f) for f in os.listdir(output_directory) if f.endswith('.pdf')]

    # Если есть хотя бы один PDF файл
    if pdf_files:
        # Можно создать ZIP-архив для скачивания всех PDF файлов
        zip_filename = "documents.zip"
        shutil.make_archive(zip_filename[:-4], 'zip', output_directory)

        return FileResponse(zip_filename, filename=zip_filename, media_type='application/zip')
    else:
        return JSONResponse({"message": "Нет доступных файлов для скачивания."})


@router.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})
