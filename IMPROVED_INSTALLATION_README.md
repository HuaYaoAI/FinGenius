# FinGenius Enhanced Installation

## Overview
This document describes the enhanced installation scripts for FinGenius, which provide improved error handling, logging, backup/rollback functionality, and other advanced features compared to the original installation scripts.

## Enhanced Features

### 1. Improved Error Handling
- Detailed error reporting with context and solutions
- Error codes for different failure types
- Graceful handling of partial failures
- Enhanced error recovery mechanisms

### 2. Comprehensive Logging
- Timestamped logs of all installation steps
- Multiple log levels (INFO, WARN, ERROR)
- Log file creation for troubleshooting (`fingenius_install.log`)
- Structured logging format for easy parsing

### 3. Backup and Rollback Functionality
- Automatic backup of existing installations
- Checkpoint system for recovery from failures
- Rollback mechanism to restore previous state
- Validation of rollback operations

### 4. Interactive Configuration
- Guided setup for API key configuration
- Selection of installation types (minimal, full, development)
- Customizable installation paths
- Configuration validation

### 5. Multiple Installation Types
- **Minimal**: Core dependencies only
- **Full**: All dependencies and tools (default)
- **Development**: Includes development tools and test dependencies

### 6. Improved Progress Reporting
- Visual progress indicators
- Estimated time remaining
- Current operation descriptions
- Overall installation progress

### 7. Post-Installation Validation
- Component verification
- API connectivity testing
- Virtual environment validation
- File permission checks

## Usage

### Bash Script (Linux/macOS)
```bash
# Make the script executable
chmod +x install_fingenius_improved.sh

# Standard installation
./install_fingenius_improved.sh

# Interactive installation
./install_fingenius_improved.sh -i

# Minimal installation
./install_fingenius_improved.sh -t minimal

# Development installation
./install_fingenius_improved.sh -t development

# Rollback previous installation attempt
./install_fingenius_improved.sh -r

# Show all options
./install_fingenius_improved.sh -h
```

### Batch Script (Windows)
```cmd
# Standard installation
install_fingenius_improved.bat

# Interactive installation
install_fingenius_improved.bat -i

# Minimal installation
install_fingenius_improved.bat -t minimal

# Development installation
install_fingenius_improved.bat -t development

# Rollback previous installation attempt
install_fingenius_improved.bat -r

# Show all options
install_fingenius_improved.bat -h
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `-h`, `--help` | Display help message |
| `-i`, `--interactive` | Interactive configuration mode |
| `-t`, `--type TYPE` | Installation type (minimal|full|development) |
| `-r`, `--rollback` | Rollback previous installation attempt |

## Installation Process

1. **System Requirements Check**
   - Python version verification (3.12+)
   - Dependency checking

2. **Backup Creation**
   - Automatic backup of existing installations

3. **Checkpoint System**
   - Resume capability for failed installations
   - Progress tracking

4. **Installation Steps**
   - uv package manager installation
   - Repository cloning
   - Virtual environment creation
   - Dependency installation
   - Configuration file creation
   - Interactive configuration (if selected)

5. **Post-Installation Validation**
   - Component verification
   - Basic functionality testing

6. **Completion**
   - Success reporting
   - Next steps guidance
   - Log file generation

## Log Files
All installation activities are logged to `fingenius_install.log` in the installation directory. The log file includes:
- Timestamped entries
- Log levels (INFO, WARN, ERROR)
- Detailed operation descriptions
- Error messages and stack traces

## Rollback and Recovery

### Automatic Rollback
If an installation fails, the script can automatically rollback to the previous state using:
```bash
./install_fingenius_improved.sh -r
```

### Manual Rollback
Users can manually trigger a rollback at any time to restore from backups.

## Troubleshooting

### Common Issues

1. **Python Version Issues**
   - Ensure Python 3.12 or higher is installed
   - Verify Python is in your PATH

2. **uv Installation Failures**
   - Check internet connectivity
   - Verify curl or wget is available
   - Manually install uv if automatic installation fails

3. **Git Repository Cloning Issues**
   - Check internet connectivity
   - Verify Git is installed and in PATH
   - Check firewall settings

4. **Virtual Environment Issues**
   - Ensure uv is properly installed
   - Check disk space availability

### Log Analysis
Check `fingenius_install.log` for detailed error information:
```bash
# View recent log entries
tail -n 50 fingenius_install.log

# Search for errors
grep "ERROR" fingenius_install.log
```

## Configuration

### Interactive Configuration
When using the `-i` flag, the script will prompt for:
- LLM API type (openai/azure/ollama)
- LLM model name
- API key (hidden input)

### Manual Configuration
After installation, edit `config/config.toml` to:
- Add your API keys
- Customize settings
- Configure LLM providers

## Installation Types

### Minimal Installation
Installs only core dependencies required for basic functionality.

### Full Installation (Default)
Installs all dependencies and tools for complete functionality.

### Development Installation
Installs all dependencies plus development tools:
- pytest (testing framework)
- black (code formatter)
- flake8 (linting tool)

## Cross-Platform Compatibility

### Linux/macOS
- Uses bash scripting
- Compatible with most Unix-like systems
- Handles different shell environments

### Windows
- Uses batch scripting with PowerShell integration
- Compatible with Windows 10 and 11
- Handles PowerShell execution policies

## Testing and Validation

### Post-Installation Tests
The script performs several validation checks:
- Python module imports
- Core component functionality
- Virtual environment activation
- Configuration file creation

### Manual Verification
After installation, you can verify the installation:
```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate.bat  # Windows

# Test import
python -c "import src.config; print('Config imported successfully')"

# Run basic test
python main.py --help
```

## Updating FinGenius

To update an existing installation:
1. Navigate to the FinGenius directory
2. Run the installation script again
3. The script will create a backup before updating

## Uninstalling FinGenius

To remove FinGenius:
1. Delete the FinGenius directory
2. Remove any created virtual environments
3. Delete configuration files if no longer needed

## Support

For issues with the installation scripts, please:
1. Check the log file (`fingenius_install.log`)
2. Verify all system requirements are met
3. Report issues to the project maintainers with:
   - Log file contents
   - System information
   - Steps to reproduce the issue