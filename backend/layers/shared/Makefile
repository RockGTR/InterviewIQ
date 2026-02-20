build-SharedDepsLayer:
	mkdir -p "$(ARTIFACTS_DIR)/python/shared"
	python3 -m pip install -r requirements.txt -t "$(ARTIFACTS_DIR)/python/" --platform manylinux2014_x86_64 --only-binary=:all: 2>/dev/null || python3 -m pip install -r requirements.txt -t "$(ARTIFACTS_DIR)/python/"
	cp -r python/shared/*.py "$(ARTIFACTS_DIR)/python/shared/"
