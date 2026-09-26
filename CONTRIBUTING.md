# Contributing

<!--
Tip: change the names to adapt this CONTRIBUTING

Package name: plaseval
Module name: plaseval
Remote repository: REPO.git

-->
**Table of content:**

* [Contributing](#contributing)
  * [Workspace](#workspace)
    * [Initialize a new uv project](#initialize-a-new-uv-project)
    * [Use an existing uv project (sync)](#use-an-existing-uv-project-sync)
    * [VSCode users](#vscode-users)
  * [Coding](#coding)
    * [Linting, typing and format](#linting-typing-and-format)
      * [Install](#install)
      * [Usage](#usage)
    * [Testing](#testing)
      * [Install](#install-1)
      * [Usage](#usage-1)
    * [Utils](#utils)
    * [Tags comments](#tags-comments)
  * [Git workflow](#git-workflow)
    * [Git conventions](#git-conventions)
    * [Git tools](#git-tools)
      * [Initialize the environment](#initialize-the-environment)
      * [Develop a feature](#develop-a-feature)
      * [Publish a release](#publish-a-release)

## Workspace

This project uses [uv] to manage Python packaging and environment.

### Initialize a new uv project

[uv] to manage Python packaging and environment.

```sh
uv init --package --name plaseval plaseval-py
cd plaseval-py
```

In `./pyproject.toml` the project scripts path has been adapted:

```toml
[project.scripts]
  # Before:
  # plaseval = "plaseval:main"
  plaseval = "plaseval.__main__:main"
```

### Use an existing uv project (sync)

```sh
git clone https://gitlab.com/vepain/plaseval.git
cd plaseval
uv sync
```

By default, [uv] create a local `virtualenv` Python virtual environment in the directory `.venv`.

Check the command is installed:

```sh
uv run plaseval --help
```

> [!TIP]
> The recommendation is to use `uv` to run the tools.
> If you do not want to use it, you have to activate the virtual environment [uv] created:
>
> ```sh
> source .venv/bin/activate
> # For Fish shell
> source .venv/bin/activate.fish
> ```
>
> Any command `uv run tool ...` can be run as `tool ...` with the virtual environment activated.

### VSCode users

For [VSCode] user, settings are in `.vscode/settings.json` and required extensions are listed in `.vscode/extensions.json`.

## Coding

### Linting, typing and format

We use [ruff] linter and formatter, and [ty] to check typing.

#### Install

Install the linters:

```sh
uv tool install ruff
uv tool install ty
```

#### Usage

Lint and format the code with [ruff]:

```sh
uvx ruff check src/plaseval
uvx ruff format src/plaseval  # With VSCode you can autoformat on save
```

Check typing with [ty]:

```sh
uvx ty check src/plaseval
```

### Testing

#### Install

Add the `test` group to the `dev` group in `pyproject.toml` (c.f. <https://docs.astral.sh/uv/concepts/projects/dependencies/#nesting-groups>):

```toml
[dependency-groups]
  dev = [ { include-group = "test" } ]
```

Install pytest:

```sh
uv add --group test pytest
uv add --group test pytest-cov
```

#### Usage

```sh
uv run pytest
# With coverage report
uv run pytest --cov=plaseval tests
```

> [!TIP]
> If you use [Coverage Gutters VSCode extension]:
>
> ```sh
> uv run pytest --cov=plaseval tests --cov-report=lcov:lcov.info --cov-report=term
> ```

### Utils

Install [deptry] to check correct dependencies:

```sh
uv tool install deptry
```

Check dependencies with [deptry]:

```sh
uvx deptry src/
```

### Tags comments

Follow the convention:

```python
# TAG The message
# TAG (context) The message
```

| Tag        | Purpose                         | Next tag(s)                                    |
| ---------- | ------------------------------- | ---------------------------------------------- |
| `TODO`     | Task to do in priority          |                                                |
| `FIXME`    | Bug to fix in priority          |                                                |
| `FEATURE`  | Future feature idea             | `TODO`                                         |
| `BUG`      | Not urgent bug to fix           | `FIXME`                                        |
| `REFACTOR` | Refactoring task                | `TODO (refactor)`                              |
| `HACK`     | Temporary trick                 | `TODO (hack)` `FIXME (hack)` `REFACTOR (hack)` |
| `XXX`      | Require caution, important area | `TODO` `FIXME` `REFACTOR`                      |
| `TOTEST`   | Require testing                 | `TODO (test)`                                  |
| `OPTIMIZE` | Can do for better performance   | `TODO (optimize)` `REFACTOR (optimize)`        |
| `DOCU`     | Add documentation               | `TODO (docu)`                                  |
| `REVIEW`   | Review code                     | `TODO` `FIXME` `REFACTOR`                      |

> [!NOTE]
> Sources:
>
> * [Conventional comments](https://conventionalcomments.org/)
> * [Medium @scottgrivner | Effectively Managing Technical Debt with TODO, FIXME, and Other Code Reminders](https://medium.com/@scottgrivner/effectively-managing-technical-debt-with-todo-fixme-and-other-code-reminders-e0b770f6180a)
> * [VSCode extension todo-tree](https://github.com/Gruntfuggly/todo-tree)

## Git workflow

### Git conventions

Branching conventions: [Default GitFlow conventions](https://danielkummer.github.io/git-flow-cheatsheet/)

Follow [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) for commit messages

> [!TIP]
> If you use `VSCode`, you can install the [Conventional Commits VSCode extension](https://marketplace.visualstudio.com/items?itemName=vivaxy.vscode-conventional-commits).

### Git tools

[git-flow-next] for git branching template

#### Initialize the environment

```sh
git flow init -d
```

#### Develop a feature

Start a new feature:

```sh
git flow feature start <feature-name>
```

> [!NOTE]
> To give access to the feature to other developers, you must first publish it:
>
> ```sh
> git flow feature publish <feature-name>
> ```

Finish the feature:

* merges to the develop branch
* removes the feature branch

```sh
git flow feature finish <feature-name>
```

#### Publish a release

Create a release branch:

```bash
# Set the release number, e.g. by add a patch
lvl=patch # patch, minor, major... see with `uv version --help`
release=$( uv version --bump $lvl --dry-run --short ) # A release number
# Fish
# set release (uv version --bump $lvl --dry-run --short)

git flow release start $release
# To allow release commits by other developers
git flow release publish $release
```

Bump the version (see [uv doc](https://docs.astral.sh/uv/guides/package/#updating-your-version)):

```sh
uv version --bump $lvl
```

Modify the `CHANGELOG.md` and commit:

```sh
git add --all
git commit -m "Prepare release $release"
```

Finish the release:

```sh
git flow release finish $release -m "New version $release"
git push origin develop
git push origin main
git push origin --tags
```

<!-- LINKS -->

[VSCode]: https://code.visualstudio.com/

[uv]: https://docs.astral.sh/uv/
[ruff]: https://docs.astral.sh/ruff/
[ty]: https://docs.astral.sh/ty/
[deptry]: https://github.com/fpgmaas/deptry

[git-flow-next]: https://github.com/gittower/git-flow-next
