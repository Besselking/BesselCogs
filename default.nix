with import <nixpkgs> {};
stdenv.mkDerivation rec {
  name = "env";
  env = buildEnv { name = name; paths = buildInputs; };
  buildInputs = [
    python38
    python38Packages.pip
    python38Packages.autopep8
    python38Packages.setuptools
    python38Packages.wheel
  ];
  # Customizable development shell setup
  shellHook = ''
    alias python='python3'
  '';
}
