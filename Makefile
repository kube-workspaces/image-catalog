# image-catalog Makefile

.PHONY: validate build lint clean sync-crd check-crd

## Validate every images/*.yaml against structural rules and, if kubeconform
## is installed, against the Image CRD schema.
validate:
	@scripts/validate.sh

## Build dist/images.yaml (full catalog) and dist/images-examples.yaml
## (curated examples only).
build:
	@scripts/build.sh

## Lint YAML formatting.
lint:
	@yamllint images/ 2>/dev/null || echo "yamllint not installed, skipping"

clean:
	@rm -rf dist

## Re-vendor the Image CRD schema from the controller repo. Requires a local
## checkout of kube-workspaces/controller as a sibling directory, or set
## CONTROLLER_REPO to its path.
CONTROLLER_REPO ?= ../controller
sync-crd:
	@cp "$(CONTROLLER_REPO)/config/crd/bases/kubeworkspaces.io_images.yaml" crds/
	@echo "Synced crds/kubeworkspaces.io_images.yaml from $(CONTROLLER_REPO)"

## Verify the vendored CRD schema matches the controller repo (fails CI on drift).
check-crd:
	@if ! diff -q "$(CONTROLLER_REPO)/config/crd/bases/kubeworkspaces.io_images.yaml" crds/kubeworkspaces.io_images.yaml >/dev/null 2>&1; then \
		echo "DRIFT: crds/kubeworkspaces.io_images.yaml differs from $(CONTROLLER_REPO)"; \
		echo "Run 'make sync-crd' to resolve."; \
		exit 1; \
	fi
	@echo "crds/kubeworkspaces.io_images.yaml is in sync with $(CONTROLLER_REPO)"
