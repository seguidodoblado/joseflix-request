#!/bin/sh
set -eu
base=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd); version=$(sed -n '1s/^[^ ]* (\([^)]*\)).*/\1/p' "$base/debian/changelog"); test -n "$version" || { echo "No se pudo leer la versión de debian/changelog" >&2; exit 1; }; stage="$base/.deb-stage"; rm -rf "$stage"; mkdir -p "$stage/DEBIAN" "$stage/opt/joseflix-request" "$stage/usr/bin" "$stage/usr/share/applications" "$stage/usr/share/icons/hicolor/scalable/apps"
cp "$base/joseflix_request.py" "$stage/opt/joseflix-request/"; printf '%s\n' "${version%-*}" > "$stage/opt/joseflix-request/VERSION"; cp "$base/debian/joseflix-launcher" "$stage/usr/bin/joseflix-request"; cp "$base/debian/joseflix-request.desktop" "$stage/usr/share/applications/"; cp "$base/joseflix-request.svg" "$stage/usr/share/icons/hicolor/scalable/apps/"; chmod 755 "$stage/usr/bin/joseflix-request" "$stage/opt/joseflix-request/joseflix_request.py"
cat > "$stage/DEBIAN/control" <<EOF
Package: joseflix-request
Version: $version
Section: video
Priority: optional
Architecture: all
Depends: python3, python3-gi, gir1.2-gtk-4.0
Maintainer: Joseflix <joseflix@localhost>
Description: Gestor de peticiones para Joseflix
EOF
output_dir="${DEB_OUTPUT_DIR:-$base/..}"; mkdir -p "$output_dir"; dpkg-deb --build --root-owner-group "$stage" "$output_dir/joseflix-request_${version}_all.deb"
