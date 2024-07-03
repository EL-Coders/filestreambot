# To learn more about how to use Nix to configure your environment
# see: https://developers.google.com/idx/guides/customize-idx-env
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-23.11"; # or "unstable"

  # Use https://search.nixos.org/packages to find packages
  packages = [
    # pkgs.go
    pkgs.python311
    pkgs.ruff
    pkgs.python311Packages.pip
    pkgs.docker 
  ];

  # Sets environment variables in the workspace
  env = {};
  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      # "vscodevim.vim"
      "alefragnani.project-manager"
      "charliermarsh.ruff"
      "donjayamanne.git-extension-pack"
      "donjayamanne.githistory"
      "donjayamanne.python-environment-manager"
      "felipecaputo.git-project-manager"
      "GitHub.vscode-pull-request-github"
      "KevinRose.vsc-python-indent"
      "mikestead.dotenv"
      "monokai.theme-monokai-pro-vscode"
      "ms-python.autopep8"
      "ms-python.debugpy"
      "ms-python.isort"
      "ms-python.pylint"
      "ms-python.python"
      "PKief.material-icon-theme"
    ];

    # Enable previews
    previews = {
      enable = false;
      previews = {
        # web = {
        #   # Example: run "npm run dev" with PORT set to IDX's defined port for previews,
        #   # and show it in IDX's web preview panel
        #   command = ["npm" "run" "dev"];
        #   manager = "web";
        #   env = {
        #     # Environment variables to set for your server
        #     PORT = "$PORT";
        #   };
        # };
      };
    };

    # Workspace lifecycle hooks
    workspace = {
      # Runs when a workspace is first created
      onCreate = {
        create-venv = ''
          python -m venv .venv
          source .venv/bin/activate
          pip install -r requirements.txt
        '';
      };
      # Runs when the workspace is (re)started
      onStart = {
        # Example: start a background task to watch and re-build backend code
        # watch-backend = "npm run watch-backend";
      };
    };
  };
}
