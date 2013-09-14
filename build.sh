#!/bin/bash

BASE_DIR=$(cd "$(dirname "$0")"; pwd)
ENV_DIR=$BASE_DIR/env

MANAGER="${ENV_DIR}/bin/python ${BASE_DIR}/manage.py"
GIT="git"
VIRTUALENV="virtualenv"

function create_env()
{
    echo $0: Creating virtual environment.

    if [ ! -d "$ENV_DIR" ]
    then
        rm -rf $ENV_DIR
        $VIRTUALENV --prompt="coinscollection" $ENV_DIR
    fi

    source $ENV_DIR/bin/activate
    export PIP_REQUIRE_VIRTUALENV=true
    $ENV_DIR/bin/pip install --upgrade --requirement=./requirements.txt --log=$BASE_DIR/logs/build_pip_packages.log

    echo $0: Making virtual environment relocatable
    $VIRTUALENV --relocatable $ENV_DIR

    echo $0: Creating virtual environment finished.
}

function create_database()
{
    echo $0: Creating database.
    DATABASE_FILE=$BASE_DIR/db/coins.db

    if [ ! -e "$DATABASE_FILE" ]
    then
        touch $DATABASE_FILE
    fi

    $MANAGER syncdb --noinput --all
    echo $0: Creating database finished.
}

function django_refresh()
{
    $MANAGER collectstatic --noinput

    cd $BASE_DIR/coins
    $MANAGER compilemessages -l ru
    cd $BASE_DIR
}

function first_run()
{
    mkdir -p $BASE_DIR/logs
    mkdir -p $BASE_DIR/public/static
    mkdir -p $BASE_DIR/public/media
    mkdir -p $BASE_DIR/db

    create_env
    create_database

    $MANAGER createsuperuser
    $MANAGER countries

    django_refresh
}

function deploy()
{
    echo $0: Update source from git.

    $GIT fetch origin master:refs/remotes/origin/master
    $GIT reset --hard origin/master

    echo $0: Update source from git finished.

    django_refresh
}

ARG=${1:-"-h"}
while test -n "$ARG"
do
    case "$ARG" in
      -d | --deploy)
          deploy
          ;;
      -i | --install)
          first_run
          ;;
      -h | --help | --)
          cat <<EOF
SYNOPSIS
       ${0##*/} [-d|--deploy] [-i|--install]

OPTIONS
       -d, --deploy
           Deploy application.

       -i, --install
           Install application.

       -h, --help
           Prints the synopsis and a list of the most commonly used commands.
EOF

          break
          ;;
      -*)
          echo "Error: Unknown option: $1" >&2
          exit 1
          ;;

    esac

    shift
    ARG=$1
done