<?php
// upload_document.php

// 1. Configurar rutas base confirmadas
$openemr_root = '/var/www/localhost/htdocs/openemr';

// 2. Cargar componentes esenciales con las rutas correctas
require_once $openemr_root . '/interface/globals.php';  // Ruta confirmada
require_once $openemr_root . '/library/sql.inc.php';    // Ruta confirmada (nota el .php al final)

// 3. Verificar funciones esenciales
if (!function_exists('sqlStatement')) {
    die("❌ Error crítico: La función sqlStatement() aún no está disponible después de cargar los archivos");
}

// 4. Configuración del entorno OpenEMR
$GLOBALS['webroot'] = $openemr_root;
$GLOBALS['srcdir'] = $openemr_root . '/library';
$_SERVER['HTTP_HOST'] = 'localhost';

// 5. Cargar DocumentService
$document_service_path = $openemr_root . '/src/Services/DocumentService.php';
if (!file_exists($document_service_path)) {
    die("❌ Error: No se encuentra DocumentService.php en $document_service_path");
}
require_once $document_service_path;

// 6. Función para crear datos de archivo (la misma que tenías)
function createFileData($tmpPath, $originalName) {
    if (!file_exists($tmpPath)) {
        die("❌ El archivo $tmpPath no existe");
    }
    
    return [
        'tmp_name' => $tmpPath,
        'name' => $originalName,
        'type' => mime_content_type($tmpPath),
        'error' => 0,
        'size' => filesize($tmpPath)
    ];
}

// 7. Parámetros de ejemplo (ajusta estos valores)
$patientId = 1002; // ID de paciente real
$categoryPath = '/Patients'; // Ruta base de categoría
$filePath = $openemr_root . '/sites/default/documents/1002/Chill_Ghibli.jpg';
$fileName = 'Chill_Ghibli.jpg';

// 8. Verificar existencia del archivo
if (!file_exists($filePath)) {
    die("❌ El archivo a importar no existe en: $filePath");
}

// 9. Procesar el documento
try {
    $documentService = new OpenEMR\Services\DocumentService();
    $fileData = createFileData($filePath, $fileName);
    
    echo "⏳ Intentando importar documento...\n";
    $result = $documentService->insertAtPath($patientId, $categoryPath, $fileData);
    
    if ($result) {
        echo "✅ Documento importado correctamente\n";
    } else {
        echo "❌ Error al importar (ver logs de OpenEMR)\n";
    }
} catch (Exception $e) {
    die("❌ Error crítico: " . $e->getMessage());
}