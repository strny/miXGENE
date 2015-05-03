#!/bin/bash

#. /usr/local/bin/virtualenvwrapper.sh
#workon mixgene_venv
cd /Migration/skola/phd/projects/miXGENE/mixgene_project && CELERY_RDBSIG=1 celery worker --app=mixgene.celery --loglevel=DEBUG
