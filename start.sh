#!/bin/bash
. /opt/venv/bin/activate  # Activar el entorno virtual
flask init-db             # Inicializar la base de datos
exec gunicorn app:create_app()  # Iniciar el servidor WSGI
