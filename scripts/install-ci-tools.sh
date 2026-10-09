#!/usr/bin/env bash
set -euo pipefail
destination="${1:?Pass an installation directory}"
mkdir -p "$destination"
case "$(uname -m)" in
  x86_64) uv_arch=x86_64; uv_sha=30ccbf0a66dc8727a02b0e245c583ee970bdafecf3a443c1686e1b30ec4939e8 ;;
  aarch64) uv_arch=aarch64; uv_sha=f71040c59798f79c44c08a7a1c1af7de95a8d334ea924b47b67ad6b9632be270 ;;
  *) echo "Unsupported CI architecture" >&2; exit 1 ;;
esac
temporary=$(mktemp -d)
trap 'rm -rf "$temporary"' EXIT
archive="uv-${uv_arch}-unknown-linux-gnu.tar.gz"
curl --fail --location --silent --show-error "https://github.com/astral-sh/uv/releases/download/0.9.26/$archive" -o "$temporary/$archive"
printf '%s  %s\n' "$uv_sha" "$temporary/$archive" | sha256sum --check -
tar -xzf "$temporary/$archive" -C "$temporary"
install -m 755 "$temporary/uv-${uv_arch}-unknown-linux-gnu/uv" "$destination/uv"
"$destination/uv" --version
destination=$(cd "$destination" && pwd)
spec_pin=a1d110de252bcc3cb2fa6d47fe37137a1a328b97
git init "$temporary/spec"
git -C "$temporary/spec" remote add origin https://github.com/docker/sandbox-kit-spec.git
git -C "$temporary/spec" fetch --depth 1 origin "$spec_pin"
git -C "$temporary/spec" checkout --detach FETCH_HEAD
test "$(git -C "$temporary/spec" rev-parse HEAD)" = "$spec_pin"
(cd "$temporary/spec" && GOTOOLCHAIN=go1.26.8 go build -mod=readonly -trimpath -o "$destination/kit-tck" ./cmd/kit-tck)
"$destination/kit-tck" version
go version -m "$destination/kit-tck" | grep -F "$spec_pin"
