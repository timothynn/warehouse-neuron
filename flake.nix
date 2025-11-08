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
          # fastapi
          # uvicorn
          # sqlalchemy
          # pydantic
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.python3Packages.pip
          ];

          shellHook = ''
            echo "🚀 Warehouse Neuron dev environment loaded"
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
