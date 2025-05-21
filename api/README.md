
# deploy

we need to do this in order:

```bash
# build the final image
make build-prod
# huggingface needs to either build the image itself, or we need to pull it from somewhere
# atm that's github container registry
# so we push it there
make push-prod-ghcr
# now we need to trigger a build in that repo
cd IFX-huge-league && make trigger-build
```

then wait for it to finish building
https://huggingface.co/spaces/ryanbalch/IFX-huge-league?logs=container
