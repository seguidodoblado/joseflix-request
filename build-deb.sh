#!/bin/sh
set -eu
base=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd); stage="$base/.deb-stage"; rm -rf "$stage"; test -x "$base/.venv/bin/python" || { echo "Falta .venv. Ejecuta: python3 -m venv .venv && .venv/bin/pip install PySide6" >&2; exit 1; }; mkdir -p "$stage/DEBIAN" "$stage/opt/venvs/joseflix-request" "$stage/usr/bin" "$stage/usr/share/joseflix-request" "$stage/usr/share/applications" "$stage/usr/share/icons/hicolor/scalable/apps"
cp "$base/joseflix_request.py" "$stage/usr/share/joseflix-request/"; cp -a "$base/.venv/." "$stage/opt/venvs/joseflix-request/"; cp "$base/debian/joseflix-launcher" "$stage/usr/bin/joseflix-request"; cp "$base/debian/joseflix-request.desktop" "$stage/usr/share/applications/"; cp "$base/joseflix-request.svg" "$stage/usr/share/icons/hicolor/scalable/apps/"; chmod 755 "$stage/usr/bin/joseflix-request" "$stage/usr/share/joseflix-request/joseflix_request.py"
cat > "$stage/DEBIAN/control" <<EOF
Package: joseflix-request
Version: 0.1.0-1
Section: video
Priority: optional
Architecture: all
Depends: python3
Maintainer: Joseflix <joseflix@localhost>
Description: Gestor de peticiones para Joseflix
EOF
dpkg-deb --build --root-owner-group "$stage" "$base/../joseflix-request_0.1.0-1_all.deb"
