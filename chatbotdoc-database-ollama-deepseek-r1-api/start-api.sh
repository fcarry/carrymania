#!/bin/bash
# Iniciar el servicio de MariaDB
mysqld_safe &

# Esperar a que MariaDB esté listo
sleep 5

# Crear una base de datos y un usuario si no existen
mysql -u root <<EOF
CREATE DATABASE IF NOT EXISTS chatbotdb;
CREATE USER IF NOT EXISTS 'chatbotuser'@'%' IDENTIFIED BY 'password123456';
GRANT ALL PRIVILEGES ON chatbotdb.* TO 'chatbotuser'@'%';
FLUSH PRIVILEGES;
USE chatbotdb;

-- Crear tabla personas
CREATE TABLE IF NOT EXISTS personas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('docente', 'estudiante'))
);

-- Crear tabla estudiantes
CREATE TABLE IF NOT EXISTS estudiantes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    persona_id INT NOT NULL,
    FOREIGN KEY (persona_id) REFERENCES personas(id)
);

-- Crear tabla cursos
CREATE TABLE IF NOT EXISTS cursos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT
);

-- Crear tabla docentes
CREATE TABLE IF NOT EXISTS docentes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    persona_id INT NOT NULL,
    FOREIGN KEY (persona_id) REFERENCES personas(id)
);

-- Crear tabla estudiantes_cursos (relación muchos a muchos)
CREATE TABLE IF NOT EXISTS estudiantes_cursos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    estudiante_id INT NOT NULL,
    curso_id INT NOT NULL,
    FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id),
    FOREIGN KEY (curso_id) REFERENCES cursos(id)
);

-- Insertar datos de ejemplo en personas
INSERT INTO personas (nombre, apellido, tipo) VALUES
('Juan', 'Pérez', 'docente'),
('María', 'Gómez', 'docente'),
('Carlos', 'López', 'estudiante'),
('Ana', 'Martínez', 'estudiante');

-- Insertar datos de ejemplo en docentes
INSERT INTO docentes (persona_id) VALUES
(1), -- Juan Pérez
(2); -- María Gómez

-- Insertar datos de ejemplo en estudiantes
INSERT INTO estudiantes (persona_id) VALUES
(3), -- Carlos López
(4); -- Ana Martínez

-- Insertar datos de ejemplo en cursos
INSERT INTO cursos (nombre, descripcion) VALUES
('Matematicas', 'Curso de matemáticas básicas'),
('Historia', 'Curso de historia universal');

-- Insertar datos de ejemplo en estudiantes_cursos
INSERT INTO estudiantes_cursos (estudiante_id, curso_id) VALUES
(1, 1), -- Carlos López en Matemáticas
(2, 2); -- Ana Martínez en Historia
EOF
ollama serve &
sleep 5
ollama pull deepseek-r1  
cd /app
uvicorn chatbotdoc:app --host 0.0.0.0 --port 8501