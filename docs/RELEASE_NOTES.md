# Release Steps

1. **Prepare the package:**
   ```bash
   # Install build tools
   pip install build twine

   # Build the package
   python -m build
   ```

2. **Test the package locally:**
   ```bash
   # Install in development mode
   pip install -e .
   
   # Run tests
   pytest tests/
   ```

3. **Upload to Test PyPI:**
   ```bash
   # Upload to test PyPI first
   python -m twine upload --repository testpypi dist/*
   
   # Test installation from test PyPI
   pip install --index-url https://test.pypi.org/simple/ invocate
   ```

4. **Upload to PyPI:**
   ```bash
   # Upload to production PyPI
   python -m twine upload dist/*
   ```

5. **Create GitHub release:**
   - Tag the release: `git tag v0.1.0`
   - Push tags: `git push --tags`
   - Create release on GitHub with changelog
