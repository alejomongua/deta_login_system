# Login system

Este proyecto comienza como un sistema de login simple usando https://deta.sh

Necesita un archivo secrets con las siguientes configuraciones:

    {
        "project": "Llave del proyecto de deta",
        "main": "Secreto de la aplicación, cadena aleatoria para los JWT",
        "smtp_user": "usuario del servidor smtp para los correos salientes",
        "smtp_password": "password del servidor smtp",
        "smtp_host": "URL del servidor SMTP",
        "smtp_port": puerto del smtp, normalmente 465,
        "email_sender": "correo electrónico del remitente",
        "email_sendername": "Nombre del remitente"
    }

Se usa FastAPI para la interfaz web

Para la generación de los JWT se usa pyjwt

Para el salting de los password se usó esta guia

https://nitratine.net/blog/post/how-to-hash-passwords-in-python/

La base de datos es deta base
