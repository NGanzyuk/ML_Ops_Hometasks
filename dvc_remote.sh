#!/bin/bash

source .env

REMOTE_NAME="myremote"

if dvc remote list | grep -q "$REMOTE_NAME"; then
    echo "Удалённый репозиторий '$REMOTE_NAME' уже существует."
else
    dvc remote add -d $REMOTE_NAME s3://$S3_BUCKET_NAME
    dvc remote modify $REMOTE_NAME access_key_id $S3_ACCESS_KEY
    dvc remote modify $REMOTE_NAME secret_access_key $S3_SECRET_KEY
    dvc remote modify $REMOTE_NAME endpointurl $S3_ENDPOINT_URL

    echo "Удалённый репозиторий '$REMOTE_NAME' добавлен с указанными конфигурациями."
fi
