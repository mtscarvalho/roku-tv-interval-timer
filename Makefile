.PHONY: assets package clean

assets:
	python3 tools/generate_assets.py

package: assets
	python3 tools/package.py

clean:
	rm -rf dist


