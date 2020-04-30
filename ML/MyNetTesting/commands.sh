gcloud ml-engine jobs submit training keras_on_cloud13 \
  --staging-bucket gs://keras-bucket-kuba \
  --module-name trainer.cloud_train \
  --package-path ./trainer \
  --runtime-version 1.9 \
  --region europe-west1 \
  --config=trainer/cloudml-gpu.yaml \
  -- \
  --job-dir gs://keras-bucket-kuba/


  #plus struktura plikow jak u mnie wywyolanie z google_cloud