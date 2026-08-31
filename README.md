# Joseflix Request

Aplicación local para gestionar peticiones de películas y series de Joseflix.

## Ejecución

Instala `python3-gi` y GTK4 en Linux Mint y configura la clave de TMDB:

```bash
export TMDB_API_KEY="tu_clave"
python3 joseflix_request.py
```

## Paquete Debian

```bash
dpkg-buildpackage -us -uc -b
sudo apt install ../joseflix-request_*.deb
```
