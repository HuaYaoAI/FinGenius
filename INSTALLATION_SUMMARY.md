# FinGenius Installation Summary

This document provides a comprehensive overview of all the available methods to install and use the FinGenius project.

## Installation Methods

### 1. Manual Installation with uv (Recommended)

Follow the instructions in the main README.md file:

1. Install uv package manager
2. Clone the repository
3. Create a virtual environment
4. Install dependencies
5. Configure the project

### 2. Automatic Installation with Shell Script (Unix/macOS)

For Unix-like systems, use the provided shell script:

```bash
./install_fingenius.sh
```

### 3. Automatic Installation with Batch Script (Windows)

For Windows systems, use the provided batch script:

```cmd
install_fingenius.bat
```

### 4. Installation with Makefile

If you have `make` installed, you can use the Makefile:

```bash
make install
```

For conda users:
```bash
make install-conda
```

## Verification

After installation, you can verify that everything is working correctly:

```bash
python test_installation.py
```

Or with make:
```bash
make test
```

## Running the Application

### Direct execution:
```bash
python main.py STOCK_CODE
```

### With make:
```bash
make run STOCK_CODE=000001
```

## Configuration

After installation, you must configure the project by editing `config/config.toml` to add your API keys and customize settings.

## Additional Resources

- `INSTALLATION_GUIDE.md` - Detailed installation instructions
- `AUTO_INSTALLATION_README.md` - Specific instructions for automatic installation
- `README.md` - Main project documentation