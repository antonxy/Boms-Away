let
  pkgs = import <nixpkgs> {};
  pypkgs = pkgs.python27Packages;
in
pkgs.mkShell rec {
  buildInputs = with pypkgs; [ pkgs.python27 sqlalchemy wxPython pkgs.xdotool ];
}
