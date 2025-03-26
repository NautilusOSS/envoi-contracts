#!/bin/bash
arc72-build-image() {
  docker build . -t algokit-builder
}
arc72-build-artifacts() {
  docker run -v $(pwd):/src -v $(pwd)/artifacts:/artifacts algokit-builder && 
  cp -v artifacts/VNSRegistryClient.ts ./src/scripts/clients/ 
  cp -v artifacts/VNSPublicResolverClient.ts ./src/scripts/clients/ 
  cp -v artifacts/VNSRSVPClient.ts ./src/scripts/clients/ 
  cp -v artifacts/OSARC200TokenClient.ts ./src/scripts/clients/
  cp -v artifacts/OSARC200TokenFactoryClient.ts ./src/scripts/clients/
  cp -v artifacts/VNSRegistrarClient.ts ./src/scripts/clients/
  cp -v artifacts/ReverseRegistrarClient.ts ./src/scripts/clients/
  cp -v artifacts/CollectionRegistrarClient.ts ./src/scripts/clients/
  cp -v artifacts/StakingRegistrarClient.ts ./src/scripts/clients/
}
arc72-build-all() {
  arc72-build-image && arc72-build-artifacts
}
arc72-cli() {
  (
    cd src/scripts
    source demo/utils.sh
    npx tsc
    cli ${@}
  )
}
arc72-pytest() {
  (
    cd src
    pytest
  )
}
arc72-demo() {
  (
    cd src/scripts
    npx tsc
    case ${1} in
      *) {
        echo "demo not found"
        false
      } ;;
    esac
  )
}
arc72-mocha() {
  (
    set -e
    cd src/scripts
    npx tsc
    test ${#} -eq 0 && {
      npm test
      true
    } || {
      npm run test-${1}
    }
  )
}