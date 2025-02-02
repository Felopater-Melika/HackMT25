{
  description = "Blue Buddy Flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    poetry2nix,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
        config.allowUnfree = true;
        # config.permittedInsecurePackages = [
        # "openssl-1.1.1v"
        # "openssl-1.1.1w"
        # ];
        overlay = [poetry2nix.overlay];
      };
    in {
      devShells.default =
        (pkgs.buildFHSEnv {
          name = "env";
          targetPkgs = p:
            with p; [
              # openssl
              # sqlite
              python312
              poetry
              python312Packages.uvicorn
              bun
              # openssl_1_1
              # alsa-lib
              # libuuid
            ];

          profile = "source pyapi/.venv/bin/activate; fish";
        })
        .env;
      shellHook = with pkgs; ''
        fish
      '';
    });
}
