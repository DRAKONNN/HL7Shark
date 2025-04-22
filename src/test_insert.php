<?php
$servername = "192.168.1.98";
$username = "openemr";
$password = "openemr";
$dbname = "openemr"; // Cambia este si el nombre es distinto

// Crear conexión
$conn = new mysqli($servername, $username, $password, $dbname, 3306);

// Verificar conexión
if ($conn->connect_error) {
    die("Conexión fallida: " . $conn->connect_error);
}

// SQL INSERT
$sql = "INSERT INTO `patient_data` (
    `pid`, `title`, `language`, `financial`, `fname`, `lname`, `mname`, `DOB`, 
    `street`, `postal_code`, `city`, `state`, `country_code`, 
    `drivers_license`, `ss`, `occupation`, `phone_home`, `phone_biz`, 
    `phone_cell`, `status`, `sex`, `email`, `race`, `ethnicity`, 
    `pubpid`, `hipaa_mail`, `hipaa_voice`, `regdate`
) VALUES (
    1002, 'Mrs.', 'english', '1', 'Susan', 'Richards', 'Storm', '1982-07-15',
    '42 Fantastic Four Blvd', '10001', 'New York', 'NY', 'US',
    'NY87654321', '987-65-4321', 'Scientist/Adventurer', '212-555-1961', '212-555-1964',
    '212-555-1965', 'active', 'Female', 'sue.richards@fantasticfour.org', 'White', 'Not Hispanic or Latino',
    'FF002', 'YES', 'YES', NOW()
)";

// Ejecutar
if ($conn->query($sql) === TRUE) {
    echo "Insert realizado correctamente.";
} else {
    echo "Error: " . $sql . "<br>" . $conn->error;
}

$conn->close();
?>
