{
  description = "Warehouse Neuron - Python backend development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonEnv = pkgs.python3.withPackages (ps: with ps; [
          # Formatters
          black
          isort
          
          # Backend dependencies (add your app deps here as needed)
          fastapi
          uvicorn
          sqlalchemy
          pydantic
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.python3Packages.pip
            pkgs.python3Packages.virtualenv
          ];

          shellHook = ''
            # Create and activate venv automatically
            VENV_DIR=".venv"
            
            if [ ! -d "$VENV_DIR" ]; then
              echo "📦 Creating Python virtual environment..."
              ${pythonEnv}/bin/python -m venv $VENV_DIR
              echo "✅ Virtual environment created at $VENV_DIR"
            fi
            
            # Activate the virtual environment
            source $VENV_DIR/bin/activate
            
            # Upgrade pip in venv if needed
            if [ ! -f "$VENV_DIR/.pip_upgraded" ]; then
              pip install --upgrade pip > /dev/null 2>&1
              touch $VENV_DIR/.pip_upgraded
            fi
            
            echo "🚀 Warehouse Neuron dev environment loaded"
            echo "🐍 Python venv activated: $VENV_DIR"
            echo "📦 Available tools:"
            echo "  - black (Python formatter)"
            echo "  - isort (import sorter)"
            echo ""
            echo "💡 Run formatters:"
            echo "  isort . && black ."
          '';
        };
      }
    );
}
