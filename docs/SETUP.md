# Requirements and Setup

- [Requirements and Setup](#requirements-and-setup)
    * [Requirements](#requirements)
    * [Setup](#setup)
        + [pipenv](#pipenv)
        + [npm](#npm)
        + [pre-commit](#pre-commit)

## Requirements

| Tool                                                                                     | Description                                     |
|:-----------------------------------------------------------------------------------------|:------------------------------------------------|
| [Pipenv](https://pypi.org/project/pipenv/)                                               | Required by AWS CDK, AWS CLI and pre-commit     |
| [NodeJS](https://nodejs.org/en/download)                                                 | Required by AWS CDK                             |
| [AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/cli.html)                             | Used for Infrastructure as Code (IaC)           |
| [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) | Used for Ad hoc AWS tasks                       |
| [pre-commit](https://pre-commit.com/)                                                    | Used to ensure standard prior to commits        |
| [websocat](https://docs.rs/crate/websocat/1.0.1)                                         | [Optional] Used for websocket testing           |
| [wscat](https://www.npmjs.com/package/wscat)                                             | [Optional] Used for websocket testing           |
| [sslscal](https://github.com/rbsec/sslscan)                                              | [Optional] Used for TLS/SSL cert validation     |

## Setup

### pipenv

Pipenv is used to manage all python dependencies.

```shell
pip install pipenv
```

```shell
pipenv install -d
```

### npm

npm is used to manage all node dependencies.

```shell
npm install
```

### pre-commit

[pre-commit](https://pre-commit.com/) is used to enforce standards on this repository prior to committing any changes. This forms part of
our [Contributing](../CONTRIBUTING.md) standards. Please also see the
[pre-commit-config.yaml](../.pre-commit-config.yaml) file.

This is installed via the Pipfile, though this has to be initialised within this repository by running the below
command:

```shell
pre-commit install
```
