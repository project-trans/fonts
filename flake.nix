{
  description = "PJTS Fonts' Nix flake";
  nixConfig = {
    experimental-features = [
      "nix-command"
      "flakes"
    ];

    extra-substituters = [
      "https://cryolitia.cachix.org"
      "https://nix-community.cachix.org"
      "https://cuda-maintainers.cachix.org"
    ];
    extra-trusted-public-keys = [
      "cryolitia.cachix.org-1:/RUeJIs3lEUX4X/oOco/eIcysKZEMxZNjqiMgXVItQ8="
      "nix-community.cachix.org-1:mB9FSh9qf2dCimDSUo8Zy7bkq5CX+/rkCWyvRCYg3Fs="
      "cuda-maintainers.cachix.org-1:0dq3bujKpuEPMCX6U4WylrUDZ9JyUG0VpVZa7CNfq5E="
    ];
  };
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

    nur-cryolitia = {
      url = "github:Cryolitia/nur-packages";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      nur-cryolitia,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (system: rec {
      pkgs = import nixpkgs { inherit system; };

      fonts-version = {
        source-han-serif = {
          version = "2.003";
          version-in-nixpkgs = pkgs.source-han-serif.version;
        };
        sarasa-ui = {
          version = "1.0.25";
          version-in-nixpkgs = pkgs.sarasa-gothic.version;
        };
        lxgw-neoxihei = {
          version = "1.211";
          version-in-nixpkgs = pkgs.lxgw-neoxihei.version;
        };
        lxgw-weikai = {
          version = "1.501";
          version-in-nixpkgs = pkgs.lxgw-wenkai.version;
        };
      };

      #nix eval --json .#check-version
      check-version =
        with pkgs.lib.attrsets;
        mapAttrs' (
          name: value:
          nameValuePair name ({
            version = value.version;
            version-in-nixpkgs = value.version-in-nixpkgs;
            updated =
              if value.version != value.version-in-nixpkgs then
                (pkgs.lib.warn "${name} version mismatch") false
              else
                true;
          })
        ) fonts-version;

      packages = {
        cn-font-split = nur-cryolitia.packages.${system}.cn-font-split;
        default =
          let
            pkgs = import nixpkgs {
              inherit system;
              overlays = [
                (final: prev: {
                  cn-font-split = nur-cryolitia.packages."${prev.system}".cn-font-split;
                  fonts-version = fonts-version;
                })
              ];
            };
          in
          pkgs.callPackage (
            {
              lib,
              stdenvNoCC,
              fetchzip,
              fetchurl,
              p7zip,
              cn-font-split,
              python3,
              fonts-version,
            }:
            let
              index-html = ./index.html;
              build-python = ./build.py;

              source-han-serif-version = fonts-version.source-han-serif.version;
              source-han-serif = fetchzip {
                url = "https://github.com/adobe-fonts/source-han-serif/releases/download/${source-han-serif-version}R/09_SourceHanSerifSC.zip";
                hash = "sha256-j7RC3Fw4g+fW1YCno7ThT8cLViBWwBgJfzzio1H3H6k=";
                stripRoot = false;
              };

              sarasa-ui-version = fonts-version.sarasa-ui.version;
              sarasa-ui = fetchurl {
                url = "https://github.com/be5invis/Sarasa-Gothic/releases/download/v${sarasa-ui-version}/SarasaUiSC-TTF-${sarasa-ui-version}.7z";
                hash = "sha256-B8sLbye2nnfX0wHg3p+0tKR/qF6jrFnbdiPmbp93Z98=";
              };

              LxgwNeoXiHei-version = fonts-version.lxgw-neoxihei.version;
              LxgwNeoXiHei = fetchurl {
                url = "https://github.com/lxgw/LxgwNeoXiHei/releases/download/v${LxgwNeoXiHei-version}/LXGWNeoXiHei.ttf";
                hash = "sha256-w3Rk0NDYXPzzg1JGsC6zIvr0SiM3ZzHHW9NwHNAhnaM=";
              };

              LxgwWenkai-version = fonts-version.lxgw-weikai.version;
              LxgwWenkai = fetchzip {
                url = "https://github.com/lxgw/LxgwWenKai/releases/download/v${LxgwWenkai-version}/lxgw-wenkai-v${LxgwWenkai-version}.zip";
                hash = "sha256-rpzrclb5w9MZonuHTcRxoPCUl2IQVAWWrBPVX6R7syQ=";
                stripRoot = false;
              };

              # commit e0a1fcc75bdf5af26457533df880591a62ed862a
              # date 2024-09-30T06:24:58.000Z
              NeoXiHei-Code = fetchurl {
                url = "https://github.com/lxgw/NeoXiHei-Code/raw/e0a1fcc75bdf5af26457533df880591a62ed862a/NeoXiHeiCode-Regular.ttf";
                hash = "sha256-Y5f1qqdbnG531c/WH+/cWUyrPHA+0ehaF3ycPERpsgM=";
              };

            in
            stdenvNoCC.mkDerivation {
              pname = "project-trans-fonts";
              version = "unstable";

              nativeBuildInputs = [
                cn-font-split
                python3
                p7zip
              ];

              unpackPhase = ''
                runHook preUnpack

                cp -rv ${source-han-serif} ./source-han-serif
                7z x ${sarasa-ui} -o"./sarasa-ui"
                cp -v ${LxgwNeoXiHei} ./LXGWNeoXiHei.ttf
                cp -rv ${LxgwWenkai}/lxgw-wenkai-v${LxgwWenkai-version} ./LXGWWenKai
                cp -v ${NeoXiHei-Code} ./NeoXiHeiCode-Regular.ttf

                runHook postUnpack
              '';

              buildPhase = ''
                runHook preBuild

                mkdir -p ./result
                install -Dm755 ${build-python} ./build.py
                python3 ./build.py

                runHook postBuild
              '';

              installPhase = ''
                runHook preInstall

                mkdir $out
                install -Dm 644 ${index-html} $out/index.html
                cp -r ./result/* $out/

                runHook postInstall
              '';

              meta = with lib; {
                description = "Project Trans Fonts";
                homepage = "https://github.com/project-trans/fonts";
                maintainers = with maintainers; [ Cryolitia ];
              };
            }
          ) { };
      };
    });
}
