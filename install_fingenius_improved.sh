#!/bin/bash

# FinGenius Enhanced Automatic Installation Script
# This script automates the installation process for the FinGenius project with improved error handling and features

# Set strict mode but handle errors gracefully
set -uo pipefail  # Exit on undefined vars and pipe failures, but not immediately on command failures

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Global variables
LOG_FILE="fingenius_install.log"
INSTALL_TYPE="full"
INTERACTIVE_MODE=false
CHECKPOINT_FILE=".install_checkpoint"
BACKUP_DIR=".backup_$(date +%Y%m%d_%H%M%S)"
START_TIME=$(date +%s)

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
    log_message "INFO" "$1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
    log_message "INFO" "$1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    log_message "WARN" "$1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
    log_message "ERROR" "$1"
}

# Function to log messages with timestamps
log_message() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Function to handle script exit
cleanup() {
    local exit_code=$?
    local end_time=$(date +%s)
    local duration=$((end_time - START_TIME))
    
    if [ $exit_code -eq 0 ]; then
        print_success "Installation completed successfully in $duration seconds"
        log_message "INFO" "Installation completed successfully in $duration seconds"
    else
        print_error "Installation failed with exit code $exit_code after $duration seconds"
        log_message "ERROR" "Installation failed with exit code $exit_code after $duration seconds"
        print_error "Check $LOG_FILE for detailed error information"
    fi
    
    # Remove checkpoint file on successful completion
    if [ $exit_code -eq 0 ] && [ -f "$CHECKPOINT_FILE" ]; then
        rm -f "$CHECKPOINT_FILE"
    fi
    
    exit $exit_code
}

# Set trap for cleanup
trap cleanup EXIT INT TERM

# Function to create checkpoint
create_checkpoint() {
    local step=$1
    echo "$step" > "$CHECKPOINT_FILE"
    log_message "INFO" "Checkpoint created: $step"
}

# Function to restore from checkpoint
restore_checkpoint() {
    if [ -f "$CHECKPOINT_FILE" ]; then
        local checkpoint=$(cat "$CHECKPOINT_FILE")
        print_warning "Found previous installation attempt at step: $checkpoint"
        log_message "INFO" "Found previous installation attempt at step: $checkpoint"
        return 0
    else
        return 1
    fi
}

# Function to create backup
create_backup() {
    if [ -d "FinGenius" ]; then
        print_info "Creating backup of existing installation..."
        mkdir -p "$BACKUP_DIR"
        cp -r FinGenius "$BACKUP_DIR/"
        print_success "Backup created in $BACKUP_DIR"
        log_message "INFO" "Backup created in $BACKUP_DIR"
    fi
}

# Function to rollback installation
rollback_installation() {
    print_warning "Rolling back installation..."
    log_message "INFO" "Rolling back installation"
    
    # Restore from backup if available
    if [ -d "$BACKUP_DIR" ] && [ -d "$BACKUP_DIR/FinGenius" ]; then
        print_info "Restoring from backup..."
        rm -rf FinGenius
        cp -r "$BACKUP_DIR/FinGenius" ./
        print_success "Restored from backup"
        log_message "INFO" "Restored from backup"
    else
        # Clean up partial installation
        print_info "Cleaning up partial installation..."
        rm -rf FinGenius .venv
        print_success "Cleanup completed"
        log_message "INFO" "Cleanup completed"
    fi
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    print_info "Checking Python version..."
    create_checkpoint "check_python_version"
    
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_info "Found Python version: $PYTHON_VERSION"
        
        # Check if Python version is 3.12 or higher
        IFS='.' read -ra VERSION_PARTS <<< "$PYTHON_VERSION"
        MAJOR=${VERSION_PARTS[0]}
        MINOR=${VERSION_PARTS[1]}
        
        if [[ $MAJOR -gt 3 ]] || [[ $MAJOR -eq 3 && $MINOR -ge 12 ]]; then
            print_success "Python version is compatible (3.12+)"
            return 0
        else
            print_error "Python version is too old. FinGenius requires Python 3.12 or higher."
            return 1
        fi
    else
        print_error "Python 3 is not installed. Please install Python 3.12 or higher."
        return 1
    fi
}

# Function to install uv
install_uv() {
    print_info "Installing uv package manager..."
    create_checkpoint "install_uv"
    
    if command_exists uv; then
        print_success "uv is already installed"
        return 0
    fi
    
    # Try to install uv
    if command_exists curl; then
        print_info "Downloading and installing uv with curl..."
        if curl -LsSf https://astral.sh/uv/install.sh | sh; then
            print_success "uv installed successfully with curl"
        else
            print_error "Failed to install uv with curl"
            return 1
        fi
    elif command_exists wget; then
        print_info "Downloading and installing uv with wget..."
        if wget -O - https://astral.sh/uv/install.sh | sh; then
            print_success "uv installed successfully with wget"
        else
            print_error "Failed to install uv with wget"
            return 1
        fi
    else
        print_error "Neither curl nor wget is available. Please install one of them to download uv."
        return 1
    fi
    
    # Add uv to PATH if needed
    if ! command_exists uv; then
        print_info "Adding uv to PATH..."
        export PATH="$HOME/.local/bin:$PATH"
        
        # Try to source shell configuration files
        if [ -f "$HOME/.bashrc" ]; then
            source "$HOME/.bashrc"
        elif [ -f "$HOME/.zshrc" ]; then
            source "$HOME/.zshrc"
        fi
        
        # Check again if uv is available
        if ! command_exists uv; then
            print_warning "uv was installed but is not in PATH. Please restart your terminal or add ~/.local/bin to your PATH."
        fi
    fi
    
    print_success "uv installation completed"
}

# Function to clone the repository
clone_repository() {
    print_info "Cloning FinGenius repository..."
    create_checkpoint "clone_repository"
    
    if [ -d "FinGenius" ]; then
        print_success "FinGenius directory already exists"
        cd FinGenius || { print_error "Failed to enter FinGenius directory"; return 1; }
    else
        if command_exists git; then
            if git clone https://github.com/HuaYaoAI/FinGenius.git; then
                print_success "Repository cloned successfully"
                cd FinGenius || { print_error "Failed to enter FinGenius directory"; return 1; }
            else
                print_error "Failed to clone repository. Please check your internet connection and try again."
                return 1
            fi
        else
            print_error "Git is not installed. Please install Git to clone the repository."
            return 1
        fi
    fi
    
    print_success "Repository cloned/verified"
}

# Function to create virtual environment
create_virtual_environment() {
    print_info "Creating virtual environment..."
    create_checkpoint "create_virtual_environment"
    
    if ! command_exists uv; then
        print_error "uv is not available. Please install uv first."
        return 1
    fi
    
    # Determine Python version for venv
    local python_version="3.12"
    if [ "$INSTALL_TYPE" = "minimal" ]; then
        python_version="3.12"
    fi
    
    if uv venv --python "$python_version"; then
        print_success "Virtual environment created"
    else
        print_error "Failed to create virtual environment"
        return 1
    fi
    
    # Activate virtual environment
    print_info "Activating virtual environment..."
    if source .venv/bin/activate; then
        print_success "Virtual environment activated"
    else
        print_error "Failed to activate virtual environment"
        return 1
    fi
}

# Function to install dependencies
install_dependencies() {
    print_info "Installing project dependencies..."
    create_checkpoint "install_dependencies"
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found. Make sure you are in the FinGenius directory."
        return 1
    fi
    
    # For minimal installation, we might want to install only core dependencies
    if [ "$INSTALL_TYPE" = "minimal" ]; then
        print_info "Installing minimal dependencies..."
        # For now, we'll still install all dependencies but this is where we could filter
        if uv pip install -r requirements.txt; then
            print_success "Minimal dependencies installed"
        else
            print_error "Failed to install minimal dependencies"
            return 1
        fi
    elif [ "$INSTALL_TYPE" = "development" ]; then
        print_info "Installing development dependencies..."
        # Install main dependencies first
        if uv pip install -r requirements.txt; then
            # Install additional development tools
            if uv pip install pytest black flake8; then
                print_success "Development dependencies installed"
            else
                print_error "Failed to install development tools"
                return 1
            fi
        else
            print_error "Failed to install core dependencies"
            return 1
        fi
    else
        print_info "Installing full dependencies..."
        if uv pip install -r requirements.txt; then
            print_success "Full dependencies installed"
        else
            print_error "Failed to install full dependencies"
            return 1
        fi
    fi
}

# Function to create configuration file
create_config() {
    print_info "Creating configuration file..."
    create_checkpoint "create_config"
    
    if [ ! -f "config/config.example.toml" ]; then
        print_error "config/config.example.toml not found."
        return 1
    fi
    
    if cp config/config.example.toml config/config.toml; then
        print_success "Configuration file created: config/config.toml"
        
        # Interactive configuration if requested
        if [ "$INTERACTIVE_MODE" = true ]; then
            configure_interactive
        else
            print_info "Please edit config/config.toml to add your API keys and customize settings."
        fi
    else
        print_error "Failed to create configuration file"
        return 1
    fi
}

# Function for interactive configuration
configure_interactive() {
    print_info "Starting interactive configuration..."
    
    read -p "Enter your LLM API type (openai/azure/ollama) [openai]: " api_type
    api_type=${api_type:-openai}
    
    read -p "Enter your LLM model name [gpt-4o]: " model_name
    model_name=${model_name:-gpt-4o}
    
    read -p "Enter your API key (input will be hidden): " -s api_key
    echo
    
    if [ -n "$api_key" ]; then
        # Update config file with user inputs
        sed -i.bak "s/api_type = \".*\"/api_type = \"$api_type\"/" config/config.toml
        sed -i.bak "s/model = \".*\"/model = \"$model_name\"/" config/config.toml
        sed -i.bak "s/api_key = \".*\"/api_key = \"$api_key\"/" config/config.toml
        rm -f config/config.toml.bak
        print_success "Configuration updated with your settings"
    else
        print_info "No API key provided. Please edit config/config.toml manually."
    fi
}

# Function to verify installation
verify_installation() {
    print_info "Verifying installation..."
    create_checkpoint "verify_installation"
    
    # Check if main.py exists
    if [ ! -f "main.py" ]; then
        print_error "main.py not found. Installation may be incomplete."
        return 1
    fi
    
    # Try to import required modules
    source .venv/bin/activate
    if python -c "import src.config" 2>/dev/null; then
        print_success "Python modules imported successfully"
    else
        print_warning "Some Python modules could not be imported. There might be an issue with the installation."
    fi
    
    # Run basic functionality test
    print_info "Running basic functionality test..."
    if python -c "from src.agent.base import BaseAgent; print('BaseAgent imported successfully')" 2>/dev/null; then
        print_success "Core components verified"
    else
        print_warning "Core components verification failed"
    fi
    
    print_success "Installation verification completed"
}

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -h, --help          Display this help message"
    echo "  -i, --interactive   Interactive configuration mode"
    echo "  -t, --type TYPE     Installation type (minimal|full|development) [default: full]"
    echo "  -r, --rollback      Rollback previous installation attempt"
    echo "  -v, --verbose       Enable verbose logging"
    echo ""
    echo "Examples:"
    echo "  $0                  # Standard installation"
    echo "  $0 -i               # Interactive installation"
    echo "  $0 -t minimal       # Minimal installation"
    echo "  $0 -t development   # Development installation"
    echo "  $0 -r               # Rollback previous attempt"
}

# Function to parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit 0
                ;;
            -i|--interactive)
                INTERACTIVE_MODE=true
                shift
                ;;
            -t|--type)
                INSTALL_TYPE="$2"
                if [[ ! "$INSTALL_TYPE" =~ ^(minimal|full|development)$ ]]; then
                    print_error "Invalid installation type. Use minimal, full, or development."
                    exit 1
                fi
                shift 2
                ;;
            -r|--rollback)
                print_info "Rolling back previous installation..."
                rollback_installation
                print_success "Rollback completed"
                exit 0
                ;;
            -v|--verbose)
                # Enable verbose logging (could redirect more to log file)
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
}

# Main installation process
main() {
    print_info "=== FinGenius Enhanced Automatic Installation ==="
    print_info "This script will install the FinGenius project with all its dependencies."
    print_info "Installation type: $INSTALL_TYPE"
    print_info "Interactive mode: $INTERACTIVE_MODE"
    print_info "Log file: $LOG_FILE"
    echo ""
    
    # Parse command line arguments
    parse_args "$@"
    
    # Check for existing checkpoint
    if restore_checkpoint; then
        read -p "Do you want to resume from the previous installation attempt? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Starting fresh installation..."
            rm -f "$CHECKPOINT_FILE"
        fi
    fi
    
    # Create backup of existing installation
    create_backup
    
    # Check Python version
    if ! check_python_version; then
        print_error "Please install Python 3.12 or higher and run this script again."
        exit 1
    fi
    
    echo ""
    
    # Install uv
    if ! install_uv; then
        print_error "Failed to install uv. Please install it manually and run this script again."
        exit 1
    fi
    
    echo ""
    
    # Clone repository
    if ! clone_repository; then
        print_error "Failed to clone repository. Please check your internet connection and try again."
        exit 1
    fi
    
    echo ""
    
    # Create virtual environment
    if ! create_virtual_environment; then
        print_error "Failed to create virtual environment. Please check the error message above."
        exit 1
    fi
    
    echo ""
    
    # Install dependencies
    if ! install_dependencies; then
        print_error "Failed to install dependencies. Please check the error message above."
        exit 1
    fi
    
    echo ""
    
    # Create configuration file
    if ! create_config; then
        print_error "Failed to create configuration file. Please check the error message above."
        exit 1
    fi
    
    echo ""
    
    # Verify installation
    if ! verify_installation; then
        print_error "Installation verification failed. Please check the error message above."
        exit 1
    fi
    
    echo ""
    print_success "=== Installation Completed Successfully ==="
    echo ""
    print_info "Next steps:"
    print_info "1. Edit config/config.toml to add your API keys and customize settings"
    print_info "2. Activate the virtual environment: source .venv/bin/activate"
    print_info "3. Run the application: python main.py STOCK_CODE"
    echo ""
    print_info "Example: python main.py 000001"
    echo ""
    print_info "For more information, please read the INSTALLATION_GUIDE.md file."
    print_info "Installation log saved to: $LOG_FILE"
}

# Run main function with all arguments
main "$@"