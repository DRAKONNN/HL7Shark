<?php

require_once("/var/www/localhost/htdocs/openemr/interface/globals.php");
require_once("/var/www/localhost/htdocs/openemr/src/Services/DocumentService.php");

use OpenEMR\Services\DocumentService;

$service = new DocumentService();

// Parámetros
$pid = 1004; // ID del paciente
$path = "/My_Documents/Images"; // Ruta de categoría en OpenEMR
$imagePath = "/tmp/Chill_Ghibli.jpg"; // Ruta dentro del contenedor

$fileData = [
    'name' => basename($imagePath),
    'tmp_name' => $imagePath
];

$result = $service->insertAtPath($pid, $path, $fileData);

if ($result) {
    echo "✅ Imagen subida correctamente.\n";
} else {
    echo "❌ Error al subir la imagen. Revisa los logs.\n";
}
